"""VPN Bot main function, that declares it's workflow, supported commands and replies."""

import os
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
import telebot
import telebot.types as tg_types
from collections import namedtuple

# from wg import get_peer_config
from middlewares.i18n_middleware import I18N
from utils import generate_share_link
from api import API

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('MainScript')


i18n = I18N(translations_path='i18n', domain_name='chauss_vpn')
_, ngettext = i18n.gettext, i18n.ngettext

# TODO use docker secrets
token = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(token, use_class_middlewares=True, threaded=False)
api = API()


def gen_markup(keys: dict, row_width: int = 1):
    """
    Create inline keyboard of given shape with buttons specified like callback:name in dict.

    :param keys: Buttons in 'callback_data: name' format
    :type keys: dict
    :param row_width: Width of rows in buttons (default: 1)
    :type row_width: int
    :rtype: :class:`tg_types.InlineKeyboardMarkup`
    """
    markup = tg_types.InlineKeyboardMarkup(row_width=row_width)
    for conf_data, conf_text in keys.items():
        markup.add(tg_types.InlineKeyboardButton(
            conf_text, callback_data=conf_data))
    return markup


######################################
##          Start Message           ##
######################################

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    """Menu for /start command."""
    # user, created = api.get_or_create_user
    user, created = message.from_user, True
    if created:
        logger.info("user %d created", user.id)

    if False and user.is_subscribed():
        markup = gen_markup({"config":  _("Give me config!"),
                             "faq": _("FAQ"),
                             "settings": _("Settings")})
    else:
        markup = gen_markup({"pay":  _("Pay to get your config!"),
                             "faq": _("FAQ"),
                             "settings": _("Settings")})

    bot.send_message(chat_id=message.chat.id,
                     text=_("Greetings, {first_name}! \nIn this bot, you can buy a subscription " \
                            "to a VPN service organized by students " \
                            "of the CMC MSU.").format(first_name=message.from_user.first_name),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
def back_to_main_menu_query(call):
    """Handle back to main menu button."""
    # user = api.get_user
    if False and user.is_subscribed():
        markup = gen_markup({"config":  _("Give me config!"),
                             "faq": _("FAQ"),
                             "settings": _("Settings")})
    else:
        markup = gen_markup({"pay":  _("Pay to get your config!"),
                             "faq": _("FAQ"),
                             "settings": _("Settings")})
    bot.edit_message_text(text=_("Greetings, {first_name}! \nIn this bot, you can buy a subscription " \
                            "to a VPN service organized by students " \
                            "of the CMC MSU.").format(first_name=call.message.chat.first_name),
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)
    bot.answer_callback_query(call.id)


######################################
##             Payment              ##
######################################

@bot.callback_query_handler(func=lambda call: call.data == "pay")
def choose_plan(call):
    """Give user options to choose suitable plan for him."""
    mp_raw = {f"sub_duration_{i}": ngettext("{} month", "{} months", i).format(i) for i in range(1, 4)}
    mp_raw["back_to_main_menu"] = _(" « Back")
    bot.edit_message_text(text=_("Please, choose duration of your subscription"),
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=gen_markup(mp_raw))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_pay")
def back_to_choose_plan(call):
    """Delete payment message and send payment plans."""
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.id)
    mp_raw = {f"sub_duration_{i}": ngettext("{} month", "{} months", i).format(i) for i in range(1, 4)}
    mp_raw["back_to_main_menu"] = _(" « Back")
    bot.send_message(text=_("Please, choose duration of your subscription"),
                          chat_id=call.message.chat.id,
                          reply_markup=gen_markup(mp_raw))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("sub_duration"))
def payment(call):
    """Generate form for payment."""
    period = int(call.data.removeprefix("sub_duration_"))
    price = [tg_types.LabeledPrice(
                    label=ngettext("{} month", "{} month", period).format(period),
                    amount=80 * (100 - 5 * (period - 1)) * period)]
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.id)
    markup = tg_types.InlineKeyboardMarkup(row_width=1)
    markup.add(
            tg_types.InlineKeyboardButton(_("Pay"), pay=True),
            tg_types.InlineKeyboardButton(_(" « Back"), callback_data="back_to_pay"),
    )

    bot.send_invoice(chat_id=call.message.chat.id,
                     title=_("Subscription"),
                     description=ngettext("Please, pay for {} month of your subscription",
                                          "Please, pay for {} months of your subscription",
                                          period).format(period),
                     invoice_payload=call.message.chat.id,
                     provider_token=os.environ['BOT_PAYMENT_PROVIDER_TOKEN'],
                     currency="RUB",
                     prices=price,
                     start_parameter=call.message.chat.id,
                     reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.pre_checkout_query_handler(func=lambda call: True)
def answer_payment(call):
    """Send response to users payment. To proceed to vpn config generation."""
    bot.answer_pre_checkout_query(call.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def successful_payment(msg):
    """If the payment of subscription was successfull, send user his config."""
    resp = api.add_user(email=str(msg.from_user.id))
    share_link = generate_share_link(resp['uuid'], host=os.environ['BOT_HOST'])
    bot.send_message(text=f'`{share_link}`', chat_id=msg.chat.id, parse_mode='markdown')
    send_welcome(msg)


@bot.callback_query_handler(func=lambda call: call.data == "config")
def send_config(call):
    """Send user his config or tell him that he doesn't have one."""
    if False:  # (doc := get_peer_config(call.from_user.id)):
        bot.answer_callback_query(call.id, _("Your config is ready!"))
        with open(doc.get(), 'r') as config_file:
            bot.send_document(chat_id=call.message.chat.id, document=config_file)
    else:
        bot.answer_callback_query(
            call.id, _("No suitable config found. Sorry!"))


@bot.callback_query_handler(func=lambda call: call.data == 'faq')
def faq_menu_query(call):
    """Handle FAQ menu."""
    config: dict = {}
    config["back_to_main_menu"] = _(" « Back")
    bot.edit_message_text(_("Frequently asked questions"), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'settings')
def settings_menu_query(call):
    """Handle settings menu."""
    bot.edit_message_text(_("Settings"), call.message.chat.id, call.message.message_id,
                          reply_markup=gen_markup({"change_language": _("Select language"),
                                                   "back_to_main_menu": _(" « Back")}, 1))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def change_language_menu_query(call):
    """Handle change language settings menu."""
    config: dict = {}
    for lang_name, flag_symbol in {"ru": "\U0001f1f7\U0001f1fa", "en": "\U0001f1ec\U0001f1e7"}.items():
        config["change_lang_to_" + lang_name] = flag_symbol + ' ' + lang_name
    config["settings"] = _(" « Back")
    bot.edit_message_text(_("Select your language:"), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_lang_to_"))
def change_user_language(call):
    """Change user language."""
    new_lang: str = call.data.removeprefix("change_lang_to_")
    # user = api.get_user
    # пока нет базы просто свапаем ру и ен
    lang_change_faker = {'ru': 'en', 'en': 'ru'}
    user_lang = lang_change_faker[new_lang]
    old_lang = user.lang
    if old_lang != new_lang:
        user.lang = new_lang
    bot.answer_callback_query(call.id, _("Language was changed to ", lang=new_lang) + new_lang)
    # Cant just call it: Telegram raise exception when you try to change text to the same one.
    if old_lang != new_lang:
        i18n.switch(new_lang)
        change_language_menu_query(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_question_"))
def faq_question_query(call):
    """Handle FAQ question button."""
    question_id = int(call.data.removeprefix("faq_question_"))
    message_text = f"*Как какать?*\n\nОчень просто"
    bot.answer_callback_query(call.id, _("See your answer:"))
    bot.edit_message_text(message_text, call.message.chat.id,
                          call.message.message_id,
                          reply_markup=gen_markup({"faq": _(" « Back")}, 1),
                          parse_mode="MARKDOWN")


def send_notification_remain_days(user, days_num: int):
    """Send notification to user that he have days_num days left."""
    i18n.switch(user.lang)
    bot.send_message(user.id, ngettext("You have {} day remaining.", "You have {} days remaining.",
                                       num=days_num).format(days_num),
                     reply_markup=gen_markup({"pay": _("Extend subscription")}, 1))


def send_notification_subscribe_is_out(user):
    """Send notification to user that his subscription is out."""
    i18n.switch(user.lang)
    bot.send_message(user.id, _("Your subscription has run out."),
                     reply_markup=gen_markup({"pay": _("Extend subscription")}, 1))


def main():
    """Start bot."""
    bot.setup_middleware(i18n)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
