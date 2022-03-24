"""
    Try to provide services for every client with the same file. Maybe isolate based on 
    token value. 

    Graph services are all same using the same client variable.

"""

from pydoc import describe
from uuid import uuid4

from fastapi import FastAPI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
import telegram
from app.core.config import settings
from app.core.graphdb import graph

app = FastAPI()
bot = telegram.Bot(token=settings.TGM_TOKEN)

products_map = {"1": 'Single plate idlis (set of 5pcs)', "2": 'Family pack (set of 25pcs)'}
chat_data = {}

# @app.get('/set_webhook', describe='A general API that can be called for onboarding new'+
# 'service providers')
# def set_webhook():
#     s = bot.setWebhook('{URL}{HOOK}'.format(URL=settings.HEROKU_URL, HOOK=settings.TGM_TOKEN))
#     if not s:
#         return "webhook setup failed"
#     else:
#         return "webhook setup ok"

@app.post(f"/{settings.UNIQUE_STRING}")
def place_order(payload: dict) -> None:
    print(payload)
    update = telegram.Update.de_json(payload, bot)
    query = update.callback_query
    if query is not None:
        button(update)
    else:
        chat_id = update.message.chat.id
        msg_id = update.message.message_id
        if str(update.message.chat_id) in chat_data.keys():
            if (update.message.text == 'order'):
                start(update, chat_data)
            else:
                pass
        elif (update.message.text == 'order'):
            start(update, chat_data)
        else:
            bot.send_message(update.message.chat_id, text="Sorry, I don't understand!")


def start(update,chat_data) -> None:
    """Sends a message with three inline buttons attached."""
    key = str(uuid4())
    keyboard = [

            [InlineKeyboardButton("Single plate idlis (set of 5pcs)", callback_data="1:" + key)],
            [InlineKeyboardButton("Family pack (set of 25pcs)", callback_data="2:" + key)],
            [InlineKeyboardButton("Place order.", callback_data="PO:" + key)]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_data[update.message.chat_id] = {}
    chat_data[update.message.chat_id][key] = {"1": False, "2": False}
    bot.sendMessage(text='Hey!, What would you like to order?:', reply_markup=reply_markup,
                    chat_id=update.message.chat_id)


def button(update) -> None:
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
        chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]][query.data.split(':')[0]] = not \
            chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]][query.data.split(':')[0]]

        keyboard = [

                [InlineKeyboardButton(products_map["1"] + (
                    "🟢️" if chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]]["1"] else ""),
                                     callback_data="1:" + query.data.split(':')[1])],
                [InlineKeyboardButton(products_map["2"] + (
                    "🟢" if chat_data[update.callback_query.message.chat.id][query.data.split(':')[1]]["2"] else ""),
                                     callback_data="2:" + query.data.split(':')[1])],
                [InlineKeyboardButton("Place order.", callback_data="PO:" + query.data.split(':')[1])]
        ]


        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.edit_message_text(text='Hey, What would you like to order today?', reply_markup=reply_markup
        , chat_id = update.callback_query.message.chat.id, message_id = update.callback_query.message.message_id)



