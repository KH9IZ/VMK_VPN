from telegram import *
from telegram.ext import *
from requests import *


conf = "config"


def getPeerConfig(update: Update, context: CallbackContext):
    print(update._effective_user.id)
    print(update.callback_query.data)
    if conf in update.callback_query.data:
        conf_name = str(update._effective_user.id)+".conf"
        f = open(conf_name, 'wb')
        f.write(b"Good job!")
        f.close()

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your config is ready!")
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=open(conf_name, 'rb'), 
                                  filename=conf_name)
