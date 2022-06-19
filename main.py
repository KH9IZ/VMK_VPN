"""VPN Bot main function, that declares it's workflow, supported commands and replies."""

import os
import logging
import typing
import telebot
import flag  # pip install emoji-country-flag

from telebot.formatting import mbold
from telebot.types import Message, CallbackQuery
from wg import get_peer_config
from models import QuestionAnswer, User
from i18n_base_midddleware import I18N

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('MainScript')


class I18NMiddleware(I18N):
    """Dynamic i18n."""

    def process_update_types(self) -> list:
        """List of update types which you want to be processed."""
        return ['message', 'callback_query']

    def get_user_language(self, obj: typing.Union[Message, CallbackQuery]):
        """Language will be used in 'pre_process' method of parent class."""
        user_id = obj.from_user.id
        lang = "ru" if (user := User.get_or_none(User.id == user_id)) is None else user.lang
        return lang

i18n = I18NMiddleware(translations_path='trans', domain_name='messages')
_ = i18n.gettext


try:
    token = os.environ['vpn_bot_token']
except Exception as exc:
    print(_("Couldn't find VPN BOT token in environment variables. Please, set it!"))
    raise ModuleNotFoundError from exc

bot = telebot.TeleBot(token, use_class_middlewares=True)


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
    markup = gen_markup({"config":  _("Get your config!"),
                         "faq": _("FAQ"),
                         "settings": _("Settings")}, 1)
    bot.send_message(chat_id=message.chat.id,
                     text=_(
                         "Welcome to the CMC MSU bot for fast and secure VPN connection!"),
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "config")
def config_query(call):
    """Send user his config or tell him that he doesn't have one."""
    if (doc := get_peer_config(call.from_user.id)):
        bot.answer_callback_query(call.id, _("Your config is ready!"))
        with open(doc, 'r') as config_file:
            bot.send_document(chat_id=call.message.chat.id, document=config_file)
    else:
        bot.answer_callback_query(
            call.id, _("No suitable config found. Sorry!"))


@bot.callback_query_handler(func=lambda call: call.data == 'faq')
def faq_menu_query(call):
    """Handle FAQ menu."""
    config: dict = {}
    for question in QuestionAnswer.select():
        config["faq_question_" + str(question.id)] = question.question
    config["back_to_main_menu"] = _(" « Back")
    bot.edit_message_text(_("Frequently asked questions"), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))


@bot.callback_query_handler(func=lambda call: call.data == 'settings')
def settings_menu_query(call):
    """Handle settings menu."""
    bot.edit_message_text(_("Settings"), call.message.chat.id,
                          call.message.message_id,
                          reply_markup=gen_markup({"change_language": _("Select language"),
                                                   "back_to_main_menu": _(" « Back")}, 1))


@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def change_language_menu_query(call):
    """Handle change language settings menu."""
    if hasattr(call, 'new_lang'):
        # You can manually set language by setting the attribute.
        i18n.switch(call.new_lang)
    config: dict = {}
    for lang_name, flag_name in {"ru": "ru", "en": "gb"}.items():
        config["change_lang_to_" + lang_name] = f"{flag.flag(flag_name)} {lang_name}"
    config["settings"] = _(" « Back")
    bot.edit_message_text(_("Select your language:"), call.message.chat.id,
                              call.message.message_id, reply_markup=gen_markup(config, 1))


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_lang_to_"))
def change_user_language(call):
    """Change user language."""
    new_lang: str = call.data.removeprefix("change_lang_to_")
    if (user := User.get_or_none(User.id == call.message.chat.id)) is None:
        old_lang = 'ru'  # Default one.
        username = str(call.from_user.first_name + ' ' + call.from_user.last_name)
        logger.info("Insert in user table new record with username: %s", username)
        User.create(id=int(call.message.chat.id), username=username,
                    lang=new_lang)
    else:
        old_lang = user.lang
        if user.lang != new_lang:
            user.lang = new_lang
            logger.info("User table updated: %d", user.save())
    bot.answer_callback_query(call.id, _("Language was changed to ", lang=new_lang) + new_lang)
    # Cant just call it: Telegram raise exception when you try to change text to the same one.
    if old_lang != new_lang:
        setattr(call, 'new_lang', new_lang)
        change_language_menu_query(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_question_"))
def faq_question_query(call):
    """Handle FAQ question button."""
    question_id = int(call.data.removeprefix("faq_question_"))
    query = QuestionAnswer.get_by_id(question_id)
    message_text = f"{mbold(query.question)}\n\n{query.answer}"
    bot.answer_callback_query(call.id, _("See your answer:"))
    bot.edit_message_text(message_text, call.message.chat.id,
                          call.message.message_id,
                          reply_markup=gen_markup({"faq": _(" « Back")}, 1),
                          parse_mode="MARKDOWN")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
def back_to_main_menu_query(call):
    """Handle back to main menu button."""
    markup = gen_markup({"config":  _("Get your config!"),
                         "faq": _("FAQ"),
                         "settings": _("Settings")}, 1)
    bot.edit_message_text(_("Welcome to the CMC MSU bot for fast and secure VPN connection!"),
                          call.message.chat.id,
                          call.message.message_id, reply_markup=markup)


def main():
    """Start bot."""
    bot.setup_middleware(i18n)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
