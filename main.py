"""
VPN Bot main function, that declares it's workflow, supported commands and replies
"""

import os
import gettext
import telebot

from wg import get_peer_config, user_have_config


translation = gettext.translation("messages", "trans", fallback=True)
_, ngettext = translation.gettext, translation.ngettext


try:
    token = os.environ['VPN_BOT_TOKEN']
except Exception as exc:
    print(_("Couldn't find VPN BOT token in environment variables. Please, set it!"))
    raise ModuleNotFoundError from exc

bot = telebot.TeleBot(token)


def gen_markup(keys, row_width):
    """
    Create inline keyboard of given shape with buttons specified like callback:name in dict
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = row_width
    for conf in keys:
        markup.add(telebot.types.InlineKeyboardButton(
            keys[conf], callback_data=conf))
    return markup


######################################
##          Start Message           ##
######################################

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    """
    Handler for /start command
    """

    if user_have_config(message.from_user.id) == True:
        markup = gen_markup({"send config":  _("Give me config!"),
                             "faq": _("FAQ"), "settings": _("Settings")}, 3)
    else:
        markup = gen_markup({"config":  _("Pay to get your config!"),
                             "faq": _("FAQ"), "settings": _("Settings")}, 3)

    bot.send_message(chat_id=message.chat.id,
                     text=_(
                         "Welcome to the CMC MSU bot for fast and secure VPN connection!"),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "config")
def choose_plan(call):
    """
    Give user options to choose suitable plan for him
    """
    markup = gen_markup({f"{i} month sub": ngettext("{} month", "{} month", i).format(i)
                        for i in range(1, 4)}, 3)
    bot.send_message(chat_id=call.message.chat.id,
                     text=_("Please, choose duration of your subscription"),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.find("month sub") != -1)
def payment(call):
    """
    Generate form for payment
    """
    period = int(call.data.split()[0])
    price = [telebot.types.LabeledPrice(
        label=ngettext("{} month", "{} month", period).format(period), amount=80 * (100 - 5 * (period - 1)) * period)]

    bot.send_invoice(chat_id=call.message.chat.id,
                     title=_("Subscription"),
                     description=ngettext(
                         "Please, pay for {} month of your subscription", "Please, pay for {} month of your subscription", period).format(period),
                     invoice_payload=call.message.chat.id,
                     provider_token=os.environ['PAYMENT_PROVIDER_TOKEN'],
                     currency="RUB",
                     prices=price,
                     start_parameter=call.message.chat.id)

    bot.answer_callback_query(call.id)


@bot.pre_checkout_query_handler(func=lambda call: True)
def answer_payment(call):
    """
    Send respond to users payment. To proceed to vpn config generation
    """
    bot.answer_pre_checkout_query(call.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def successful_payment(call):
    """
    If the payment of subscription was successfull, send user his config
    """
    print(call.chat)
    markup = gen_markup({"send config":  _("Get your config!")}, 1)
    bot.send_message(call.chat.id, _(
        "Thank you for choosing our VPN!"), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "send config")
def send_config(call):
    """
    Callback handler to send user his config or to tell him that he doesn't have one
    """
    doc = get_peer_config(call.from_user.id)

    if doc:
        bot.answer_callback_query(call.id, _("Your config is ready!"))
        bot.send_document(chat_id=call.message.chat.id, document=doc)
    else:
        bot.answer_callback_query(
            call.id, _("No suitable config found. Sorry!"))


def main():
    """
    Start bot
    """
    bot.infinity_polling()


if __name__ == "__main__":
    main()
