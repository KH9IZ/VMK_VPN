#from copyreg import dispatch_table
#from numpy import disp
#from telegram import KeyboardButton, ReplyKeyboardMarkup
#from telegram.ext.updater import Updater
#from telegram.update import Update
#from telegram.ext.callbackcontext import CallbackContext
#from telegram.ext.commandhandler import CommandHandler
#from telegram.ext.messagehandler import MessageHandler
#from telegram.ext.filters import Filters

from telegram import *
from telegram.ext import *
from requests import *

from wg import *


conf = "config"
button1 = [InlineKeyboardButton(text="Get your config!", callback_data=conf)]
keyboard_inline = InlineKeyboardMarkup([button1])


def startCommand(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the CMC MSU bot for fast and secure VPN connection!",
                             reply_markup=keyboard_inline)


def main():
    updater = Updater(token="5477394676:AAEJnw4NxfWY1EoM95arKoW3bdCN02iLCtQ")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", startCommand))
    dp.add_handler(CallbackQueryHandler(getPeerConfig))
    #dp.add_handler(MessageHandler(Filters.text, getConfig))

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
