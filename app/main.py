"""
    Try to provide services for every client with the same file. Maybe isolate based on 
    token value. 

    Graph services are all same using the same client variable.

"""

from fastapi.responses import JSONResponse
from uuid import uuid4

from fastapi import FastAPI, Path, Depends, Request
from fastapi.staticfiles import StaticFiles
from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
import telegram
import jwt
from app.core.config import settings
from app.core.graphdb import get_session
from app.core.constants import RESERVED_COMMANDS
from app.utilities.bot_handler import resolve_query

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
def place_order(token: str = Path(...), payload: dict=None, graph_driver = Depends(get_session)) -> None:
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
        if str(update.message.chat_id) in chat_data.keys():
            if (str(update.message.text).lower() == 'order'):
                start(bot, update, chat_data, sp_info, client_info, graph_driver)
            else:
                pass
        elif (str(update.message.text).lower() == 'order'):
            start(bot, update, chat_data, sp_info, client_info, graph_driver)
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
        if (int(client_info['token_count']) != int(decode_data['token_id'])-1):
            return JSONResponse(status_code=401, content={'success': False})
        return JSONResponse(status_code=200, content={'success': True})
    except jwt.exceptions.InvalidSignatureError as e:
        return JSONResponse(status_code=401, content={'success': False})
def start(bot, update,chat_data, sp_info, client_info, graph_driver) -> None:
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

def button(bot, update) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    print(query, "QUERY-----------------") #Confirm later the field access correctly.
    if str(query.data).startswith("PO"):
        bot.edit_message_text(text = "Thankyou for placing the order, "
                                     "follow the link below to complete the payment." ,chat_id=update.callback_query.message.chat.id,
                              message_id=update.callback_query.message.message_id
                              )
        #Create an entry in the database.

    else:
        chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]][query.data.split(':')[0][-1:]] = (-1)**(1+len(query.data.split(':')[0]))+\
            chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]][query.data.split(':')[0][-1:]]

        keyboard = [

                [InlineKeyboardButton("-", callback_data="-1:" + query.data.split(':')[1]),InlineKeyboardButton(products_map["1"] + (
                    str(chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]]["1"])),
                                     callback_data="1:" + query.data.split(':')[1])],
                [InlineKeyboardButton(products_map["2"] + (
                    "🟢" if chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]]["2"] else ""),
                                     callback_data="2:" + query.data.split(':')[1])],
                [InlineKeyboardButton("Place order.", callback_data="PO:" + query.data.split(':')[1])]
        ]


        reply_markup = InlineKeyboardMarkup(keyboard, resize_keyboard=True)

        bot.edit_message_text(text='Hey, What would you like to order today?', reply_markup=reply_markup
        , chat_id = update.callback_query.message.chat.id, message_id = update.callback_query.message.message_id)





