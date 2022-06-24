"""
    Try to provide services for every client with the same file. Maybe isolate based on 
    token value. 

    Graph services are all same using the same client variable.

"""

from app.core.config import settings
from app.core.graphdb import get_session
from app.core.constants import RESERVED_COMMANDS
from app.utilities.bot_handler import resolve_query
from app.utilities.payload_creator import createCashFreeLinkGeneratorPayload
from app.models.api import GenerateOtp

import telegram
import jwt
import time
import pyotp

from fastapi.responses import JSONResponse
from fastapi import FastAPI, Path, Depends
from fastapi.staticfiles import StaticFiles
from base64 import b32encode

app = FastAPI()
chat_data = {}

app.mount("/frontend/", StaticFiles(directory="frontend/"), name="static")

@app.get('/set_webhook') #'A general API that can be called for onboarding new service providers'
def set_webhook(bot_token: str):
    bot = telegram.Bot(token=bot_token)
    s = bot.setWebhook('{URL}{HOOK}/{TOKEN}'.format(URL=settings.HEROKU_URL, HOOK=settings.UNIQUE_STRING, TOKEN=bot_token))
    if not s:
        return "webhook setup failed"
    else:
        return "webhook setup ok"

@app.post(f"/{settings.UNIQUE_STRING}/"+"{token}")
def enquire_order(token: str = Path(...), payload: dict=None, graph_driver = Depends(get_session)) -> None:
    bot = telegram.Bot(token=token)
    update = telegram.Update.de_json(payload, bot)
    query = update.callback_query
    print("UPDATE", update) 

    sp_info = list(graph_driver.run(f'MATCH (SP:ServiceProvider) where SP.token="{token}" RETURN SP'))[0]['SP']
    client_info = list(graph_driver.run(f'MATCH (C:Client) where C.client_id={update.message.chat_id} \
    RETURN C'))

    print(client_info, "CLIENT_INFO", len(client_info))

    #Check if the client is already in the database.
    if (len(client_info)==0):
        query = "CREATE (C:Client $props) RETURN C"
        graph_driver.run(query, props={'client_id': update.message.chat_id,
         'service_provider': sp_info['seller_id'],
         'token_count': 0})

    client_info = list(graph_driver.run(f'MATCH (C:Client) where C.client_id={update.message.chat_id} \
    RETURN C'))[0]['C']

    if query is not None:
        button(bot, update)

    elif str(update.message.text).lower() in RESERVED_COMMANDS:
        return_text = resolve_query(str(update.message.text).lower(), sp_info['name'])
        bot.send_message(update.message.chat_id, text=return_text)

    else:
        if (str(update.message.text).lower() == 'order'):
            start(bot, update, sp_info, client_info, graph_driver)
        else:
            bot.send_message(update.message.chat_id, text="Sorry, I don't understand!")

@app.get("/validate_token/{token}")
def validate_token(token: str, graph_driver = Depends(get_session)):
    """
        As far as I can comprehend, this prevents any sorts of replay attack becuz of token count
        check. Also it also prevents MiM tampering attack due to the nature of JWT.


    """
    try:
        decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
        client_info = list(graph_driver.run(f'MATCH (C:Client) where C.client_id={decode_data["chat_id"]} \
        RETURN C'))[0]['C']
        print("client-info", client_info, type(client_info['token_count']))
        print("decoded data", decode_data, type(decode_data['token_id']))
        if (int(client_info['token_count'])-1 != int(decode_data['token_id'])):
            return JSONResponse(status_code=401, content={'success': False})
        return JSONResponse(status_code=200, content={'success': True})
    except jwt.exceptions.InvalidSignatureError as e:
        return JSONResponse(status_code=401, content={'success': False})

@app.get("/populate_menu/{token}")
def populate_menu(token: str, graph_driver = Depends(get_session)):
    result = validate_token(token=token, graph_driver=graph_driver)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})

    decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
    client_info = list(graph_driver.run(f'MATCH p=(S:ServiceProvider)-[R:SELLS]->(P:ProductCatalogue)\
        where S.seller_id="{decode_data["sp_id"]}" RETURN S,R,P'))
    menu_items = []
    item_price = []
    for item in client_info:
        if len(item['R'].get('unit', []))==0:
            menu_items.append(item['P']['name'])
            item_price.append(item['R']['price'])
        else:
            for unit, price in zip(item['R'].get('unit', []), item['R'].get('price', [])):
                metric = item['R'].get('metric', '')
                menu_items.append(item['P']['name']+f" (Pack of {unit}{metric})")
                item_price.append(price)
    
    return JSONResponse(status_code=200, content={'success': True, 'data': {'store_name':client_info[0]['S']['name'], 'menu_items': menu_items, 
    'item_price': item_price}})

@app.post("/place_order/{token}")
def place_order(data: dict, token: str, graph_driver = Depends(get_session)):
    """
    Currently after an order is placed, we are incrementing the token count, which 
    makes us lose track of how much order query is invoked by the client - 
    overcome this!  
    """
    result = validate_token(token=token, graph_driver=graph_driver)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})
    
    decode_data = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
    client_info = list(graph_driver.run(f'MATCH p=(S:ServiceProvider)-[R:SELLS]->(P:ProductCatalogue)\
        where S.seller_id="{decode_data["sp_id"]}" RETURN S,R,P'))

    bot = telegram.Bot(token=client_info[0]['S']['token'])
    print("CLIENT", client_info)
    ctr = 0
    match_query = ""
    create_query = "CREATE "
    props = {}
    total_order_price = 0
    for item in client_info:
        if len(item['R'].get('unit', []))==0:
            qty = data[str(ctr//4)+"_"+str(ctr%4+1)] 
            if qty==0:
                ctr+=1
                continue
            item_name = str(item['P']['name'])
            match_query+=f"({item_name}{ctr}: ProductCatalogue " + "{name: $"+f"{item_name}{ctr}"+"}), "
            temp=f"-[I{ctr}:INCLUDES"+ "{"+f"total_price:$tp_{item_name}{ctr}, quantity: $qt_{item_name}{ctr}, unit: $ut_{item_name}{ctr}"+"}"+f" ]->({item_name}{ctr}), "
            
            if ctr == 0:
                create_query += (f"(O:Order"+"{date_time: $date_time, payment_status: 'In Progress', total_amount: $total_order_price})"+temp)
            else:
                create_query += ("(O)"+temp)
            total_order_price+=price*qty
            props[f"{item_name}{ctr}"] = f"{item_name}"
            props[f"tp_{item_name}{ctr}"] = qty*price
            props[f"qt_{item_name}{ctr}"] = qty
            props[f"ut_{item_name}{ctr}"] = unit
            ctr+=1
        else:
            for unit, price in zip(item['R'].get('unit', []), item['R'].get('price', [])): 
                qty = data[str(ctr//4)+"_"+str(ctr%4+1)]
                if qty==0:
                    ctr+=1
                    continue
                item_name = str(item['P']['name'])
                item_unit = unit
                match_query+=f"({item_name}{ctr}: ProductCatalogue " + "{name: $"+f"{item_name}{ctr}"+"}), "
                temp=f"-[I{ctr}:INCLUDES"+"{"+f"total_price:$tp_{item_name}{ctr}, quantity: $qt_{item_name}{ctr}, unit: $ut_{item_name}{ctr}"+"}"+f" ]->({item_name}{ctr}), "
                if ctr == 0:
                    create_query += (f"(O:Order"+"{date_time: $date_time, payment_status: 'In Progress', total_amount: $total_order_price})"+temp)
                else:
                    create_query += ("(O)"+temp)
                total_order_price+=price*qty
                props[f"{item_name}{ctr}"] = f"{item_name}"
                props[f"tp_{item_name}{ctr}"] = qty*price
                props[f"qt_{item_name}{ctr}"] = qty
                props[f"ut_{item_name}{ctr}"] = unit
                ctr+=1

    #Creating an order node in the db.

    match_query = "MATCH "+match_query
    props["date_time"] = int(time.time())
    props["total_order_price"] = total_order_price
    
    print("MATCH: ", match_query)
    print("CREATE: ", create_query)
    print("TOA: ", total_order_price)
    print("PROP: ", props)
    result = graph_driver.run(match_query[:-2]+" "+create_query[:-2]+" return O;", props)
    print(list(result))
    
    payload = createCashFreeLinkGeneratorPayload(mobile = "8277607950", unique_id = "<something>",
    amount = 100, purpose="<Something>", expiry = "2022-10-14T15:04:05+05:30")
    
    bot.send_message(decode_data['chat_id'], text = "We've received your order!")

    query = f"MATCH (C:Client) where C.client_id={decode_data['chat_id']} \
    SET C.token_count={decode_data['token_id']+2}" #Two becuz, the actual token sent to the user is one behind the count (0 index).
    graph_driver.run(query)
    return JSONResponse(status_code=200, content={'success': True})
    
def start(bot, update, sp_info, client_info, graph_driver) -> None:
    """Sends a message with three inline buttons attached."""

    """
        Thinking of developing 'host-my-menu' as a service, and it can called here.

        Create a JWT, with following properties:
            1: chat_id: Need this to send message back to the user.
            2: sp_id: Do not user token-id
            2: token_id: incremental. at any time, just a single token must be active.
    """

    jwt_payload = {
        "chat_id": update.message.chat_id,
        "sp_id": sp_info["seller_id"],
        "token_id": client_info['token_count'] #Need to maintain a db for token related info
    }
    query = f"MATCH (C:Client) where C.client_id={update.message.chat_id} \
    SET C.token_count={client_info['token_count']+1}"
    graph_driver.run(query)

    encoded_jwt = jwt.encode(jwt_payload, settings.SECRET, algorithm="HS256")
    bot.sendMessage(text=f'Please follow this link to place the order\n{settings.HEROKU_URL}frontend/index.html?identifier={encoded_jwt}',
                    chat_id=update.message.chat_id)


@app.get("/generate_otp/{token}/{mobile_no}")
def generate_otp(input: GenerateOtp = Depends(GenerateOtp), graph_driver = Depends(get_session)):
    result = validate_token(token=input.token, graph_driver=graph_driver)
    if result.status_code!=200:
       return JSONResponse(status_code=401, content={'success': False})

    totp = pyotp.TOTP(b32encode(bytes(settings.SECRET+str(input.mobile_no), 'utf-8')))
    return JSONResponse(status_code=201, content={'success': True, 'data': {'otp': totp.now()}})
