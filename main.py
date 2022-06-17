"""VPN Bot main function, that declares it's workflow, supported commands and replies."""

import os
import gettext
import logging
import telebot
import flag  # pip install emoji-country-flag

from wg import get_peer_config
from models import QuestionAnswer, User

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('MainScript')


translations = {lang: gettext.translation("messages", "trans", fallback=True, languages=[lang])
                for lang in ('ru', 'en')}

def get_message_in_lang(text: str, lang:str = 'ru') -> str:
    """Translate message with language."""
    return translations[lang].gettext(text)

_ = get_message_in_lang


try:
    token = os.environ['vpn_bot_token']
except Exception as exc:
    print(_("Couldn't find VPN BOT token in environment variables. Please, set it!"))
    raise ModuleNotFoundError from exc

bot = telebot.TeleBot(token)

def gen_markup(keys: dict, row_width: int):
    """Create inline keyboard of given shape with buttons specified like callback:name in dict."""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = row_width
    for conf_data, conf_text in keys.items():
        markup.add(telebot.types.InlineKeyboardButton(
            conf_text, callback_data=conf_data))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Menu for /start command."""
    lang = "ru" if (user := User.get_or_none(User.id == message.chat.id)) is None else user.lang
    markup = gen_markup({"config":  _("Get your config!", lang),
                         "faq": _("FAQ", lang),
                         "settings": _("Settings", lang)}, 1)
    bot.send_message(chat_id=message.chat.id,
                     text=_(
                         "Welcome to the CMC MSU bot for fast and secure VPN connection!", lang),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "config")
def config_query(call):
    """Send user his config or to tell him that he doesn't have one."""
    # pylint: disable = unspecified-encoding
    lang = ("ru" if (user := User.get_or_none(User.id == call.message.chat.id)) is None
            else user.lang)
    if (doc := get_peer_config(call.from_user.id)):
        bot.answer_callback_query(call.id, _("Your config is ready!", lang))
        with open(doc, 'r') as config_file:
            bot.send_document(chat_id=call.message.chat.id, document=config_file)
    else:
        bot.answer_callback_query(
            call.id, _("No suitable config found. Sorry!", lang))


@bot.callback_query_handler(func=lambda call: call.data == 'faq')
def faq_menu_query(call):
    """Handle FAQ menu."""
    lang = ("ru" if (user := User.get_or_none(User.id == call.message.chat.id))
            is None else user.lang)
    config: dict = {}
    for question in QuestionAnswer.select():
        config["faq_question_" + str(question.id)] = question.question
    config["back_to_main_menu"] = _(" « Back", lang)
    bot.edit_message_text(_("Frequently asked questions", lang), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))


@bot.callback_query_handler(func=lambda call: call.data == 'settings')
def settings_menu_query(call):
    """Handle settings menu."""
    lang = ("ru" if (user := User.get_or_none(User.id == call.message.chat.id))
            is None else user.lang)
    bot.edit_message_text(_("Settings", lang), call.message.chat.id,
                          call.message.message_id,
                          reply_markup=gen_markup({"change_language": _("Select language", lang),
                                                   "back_to_main_menu": _(" « Back", lang)}, 1))


@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def change_language_menu_query(call):
    """Handle change language settings menu."""
    lang = ("ru" if (user := User.get_or_none(User.id == call.message.chat.id))
            is None else user.lang)
    config: dict = {}
    for lang_name, flag_name in {"ru": "ru", "en": "gb"}.items():
        config["change_lang_to_" + lang_name] = f"{flag.flag(flag_name)} {lang_name}"
    config["settings"] = _(" « Back", lang)
    bot.edit_message_text(_("Select your language:", lang), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_lang_to_"))
def change_user_language(call):
    """Change user language."""
    old_lang: str = None
    new_lang: str = call.data.removeprefix("change_lang_to_")
    if (user := User.get_or_none(User.id == call.message.chat.id)) is None:
        old_lang = 'ru'  # Default one.
        username = str(call.from_user.first_name + ' ' + call.from_user.last_name)
        logger.info("Insert in user table new record with username: %s", username)
        User.create(id=int(call.message.chat.id), username=username,
                    lang=new_lang)
    elif user.lang != new_lang:
        old_lang = user.lang
        user.lang = new_lang
        logger.info("User table updated: %d", user.save())
    bot.answer_callback_query(call.id, _("Language was changed to ", new_lang) + new_lang)
    # Cant just call it: Telegram raise exception when you try to change text to the same one.
    if old_lang is not None and old_lang != new_lang:
        change_language_menu_query(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_question_"))
def faq_question_query(call):
    """Handle FAQ question button."""
    lang = ("ru" if (user := User.get_or_none(User.id == call.message.chat.id))
            is None else user.lang)
    question_id = int(call.data.removeprefix("faq_question_"))
    query = QuestionAnswer.get_by_id(question_id)
    message_text = f"**{query.question}**\n\n{query.answer}"
    bot.answer_callback_query(call.id, _("See your answer:", lang))
    bot.edit_message_text(message_text, call.message.chat.id,
                          call.message.message_id,
                          reply_markup=gen_markup({"faq": _(" « Back", lang)}, 1),
                          parse_mode="MARKDOWN")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
def back_to_main_menu_query(call):
    """Handle back to main menu button."""
    lang = ("ru" if (user := User.get_or_none(User.id == call.message.chat.id)) is None else
            user.lang)
    markup = gen_markup({"config":  _("Get your config!", lang),
                         "faq": _("FAQ", lang),
                         "settings": _("Settings", lang)}, 1)
    bot.edit_message_text(_("Welcome to the CMC MSU bot for fast and secure VPN connection!", lang),
                          call.message.chat.id,
                          call.message.message_id, reply_markup=markup)


def main():
    """Start bot."""
    bot.infinity_polling()


if __name__ == "__main__":
    main()
