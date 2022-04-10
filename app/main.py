"""
    Try to provide services for every client with the same file. Maybe isolate based on 
    token value. 

    Graph services are all same using the same client variable.

"""

from http.client import HTTPResponse
from uuid import uuid4

from fastapi import FastAPI, Path, Depends, Request
from fastapi.staticfiles import StaticFiles
from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
import telegram
from app.core.config import settings
from app.core.graphdb import get_session
from app.core.constants import RESERVED_COMMANDS
from app.utilities.bot_handler import resolve_query

app = FastAPI()

products_map = {"1": 'Single plate idlis (set of 5pcs)', "2": 'Family pack (set of 25pcs)'}
chat_data = {}

app.mount("/ui/", StaticFiles(directory="frontend/"), name="static")

@app.get("/place_order", response_class=HTTPResponse)
async def main(request: Request):
    print(f"Hello from - {request.headers}")
    with open('frontend/index.html') as f:
        data = f.read()
    return data

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
    sp_info = list(graph_driver.run(f'MATCH (SP:ServiceProvider) where SP.token="{token}" RETURN SP'))[0]['SP']

    update = telegram.Update.de_json(payload, bot)
    query = update.callback_query

    if query is not None:
        button(bot, update)

    elif str(update.message.text).lower() in RESERVED_COMMANDS:
        return_text = resolve_query(str(update.message.text).lower(), sp_info['name'])
        bot.send_message(update.message.chat_id, text=return_text)

    else:
        if str(update.message.chat_id) in chat_data.keys():
            if (str(update.message.text).lower() == 'order'):
                start(bot, update, chat_data)
            else:
                pass
        elif (str(update.message.text).lower() == 'order'):
            start(bot, update, chat_data)
        else:
            bot.send_message(update.message.chat_id, text="Sorry, I don't understand!")


def start(bot, update,chat_data) -> None:
    """Sends a message with three inline buttons attached."""

    """
        Thinking of developing 'host-my-menu' as a service, and it can called here.

    """

    key = str(uuid4())
    keyboard = [

            [InlineKeyboardButton("-", callback_data="1:" + key),InlineKeyboardButton("Single plate idlis (set of 5pcs)", callback_data="1:" + key)],
            [InlineKeyboardButton("Family pack (set of 25pcs)", callback_data="2:" + key)],
            [InlineKeyboardButton("Place order.", callback_data="PO:" + key)]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_data[update.message.chat_id] = {}
    chat_data[update.message.chat_id][key] = {"1": 0, "2": 0}
    bot.sendMessage(text='Hey!, What would you like to order?:', reply_markup=reply_markup,
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





