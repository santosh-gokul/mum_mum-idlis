from uuid import uuid4

from fastapi import FastAPI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Invoice, LabeledPrice
import telegram
from app.core.config import settings

app = FastAPI()
bot = telegram.Bot(token="5037044076:AAEc8BFWgcVDZa5pRFLaTt1FkN89xnnmsDg")

products_map = {"1": 'Single plate idlis (set of 5pcs)', "2": 'Family pack (set of 25pcs)'}
chat_data = {}


@app.post(f"/{settings.TOKEN}")
def respond(payload: dict) -> None:
    update = telegram.Update.de_json(payload, bot)
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    print("Chat id: ", chat_id, " Message id: ", msg_id)

    query = update.callback_query
    if query is not None:
        button(update)
    else:
        if str(update.message.chat_id) in chat_data.keys():
            if (update.message.text == 'order'):
                start(update, chat_data)
            else:
                pass
        elif (update.message.text == 'order'):
            start(update, chat_data)
        else:
            bot.send_message(update.message.chat_id, text="Sorry, I don't uderstand!")


def start(update,chat_data) -> None:
    """Sends a message with three inline buttons attached."""
    key = str(uuid4())
    keyboard = [
        [
            InlineKeyboardButton("Single plate idlis (set of 5pcs)", callback_data="1:" + key),
            InlineKeyboardButton("Family pack (set of 25pcs)", callback_data="2:" + key),
            InlineKeyboardButton("Place order.", callback_data="PO:" + key)
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_data[update.message.chat_id] = {}
    chat_data[update.message.chat_id][key] = {"1": False, "2": False}
    bot.sendMessage('Hey!, What would you like to order?:', reply_markup=reply_markup,
                     chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id)


def button(update) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    if str(query.data).startswith("PO"):
        invoice_handler = Invoice("a", "a", "a", "a", 100)
        bot.edit_message_text("Thankyou for placing the order, find the invoice below")
        bot.send_invoice("Purchase Summary", "Total order for the day", "Idk",
                         "284685063:TEST:ODAyNjg0MWVhNmVl", "INR",
                         [LabeledPrice('Idli', 100000)])

    else:
        chat_data[update.effective_chat.id][query.data.split(':')[1]][query.data.split(':')[0]] = not \
            chat_data[update.effective_chat.id][query.data.split(':')[1]][query.data.split(':')[0]]

        keyboard = [
            [
                InlineKeyboardButton(products_map["1"] + (
                    "✔️" if chat_data[update.effective_chat.id][query.data.split(':')[1]]["1"] else ""),
                                     callback_data="1:" + query.data.split(':')[1]),
                InlineKeyboardButton(products_map["2"] + (
                    "✔️" if chat_data[update.effective_chat.id][query.data.split(':')[1]]["2"] else ""),
                                     callback_data="2:" + query.data.split(':')[1]),
                InlineKeyboardButton("Place order.", callback_data="PO:" + query.data.split(':')[1])
            ],
        ]

        print(chat_data)
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.edit_message_text('Hey, What would you like to order today?', reply_markup=reply_markup,
                              chat_id=update.message.chat_id, message_id=update.message.message_id)


@app.get('/set_webhook')
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=settings.URL, HOOK=settings.TOKEN))
    if not s:
        return "webhook setup failed"
    else:
        return "webhook setup ok"
