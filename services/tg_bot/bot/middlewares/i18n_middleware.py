"""Module for dynamic i18n."""
# See github.com/eternnoir/pyTelegramBotAPI/blob/master/examples/middleware/
# class_based/i18n_middleware/i18n_base_midddleware.py


import gettext
import os
import threading

from telebot.types import Message, CallbackQuery
from telebot.handler_backends import BaseMiddleware


class I18N(BaseMiddleware):
    """This middleware provides high-level tool for internationalization.

    It is based on gettext util.
    """

    context_lang = threading.local()

    def __init__(self, translations_path, domain_name: str):
        """Init inner fields and find available languages."""
        super().__init__()
        self.update_types = self.process_update_types()

        self.path = translations_path
        self.domain = domain_name
        self.translations = self.__find_translations()

    @property
    def available_translations(self):
        """Languages found in specified path."""
        return list(self.translations)

    def gettext(self, text: str, lang: str = None):
        """Singular translations."""
        if lang is None:
            lang = self.context_lang.language

        if lang not in self.translations:
            return text

        translator = self.translations[lang]
        return translator.gettext(text)

    def ngettext(self, singular: str, plural: str, lang: str = None, num=1):
        """Plural translations."""
        if lang is None:
            lang = self.context_lang.language

        if lang not in self.translations:
            if num == 1:
                return singular
            return plural

        translator = self.translations[lang]
        return translator.ngettext(singular, plural, num)

    def process_update_types(self) -> list:
        """List of update types which you want to be processed."""
        return ['message', 'callback_query']

    def get_user_language(self, obj: Message | CallbackQuery):
        """Return any update types which you want to be processed."""
        user_id = obj.from_user.id
        lang = "ru"  # if (user := User.get_or_none(User.id == user_id)) is None else user.lang
        return lang

    def pre_process(self, message, data):
        """Context language variable will be set each time when update from 'process_update_types' comes."""
        self.switch(self.get_user_language(obj=message))
        # See https://stackoverflow.com/a/20643172/15102008 for explanation about setattr.

    def switch(self, new_lang: str):
        """Manually switch language."""
        setattr(self.context_lang, 'language', new_lang)

    def post_process(self, message, data, exception):
        """Do not do anything."""
        if exception:
            raise exception

    def __find_translations(self):
        """Look for translations with passed 'domain' in passed 'path'."""
        if not os.path.exists(self.path):
            raise RuntimeError(f"Translations directory by path: {self.path!r} was not found")

        result = {}

        for name in os.listdir(self.path):
            translations_path = os.path.join(self.path, name, 'LC_MESSAGES')

            if not os.path.isdir(translations_path):
                continue

            po_file = os.path.join(translations_path, self.domain + '.po')
            mo_file = po_file[:-2] + 'mo'

            if os.path.isfile(po_file) and not os.path.isfile(mo_file):
                raise FileNotFoundError(f"Translations for: {name!r} were not compiled!")

            with open(mo_file, 'rb') as file:
                result[name] = gettext.GNUTranslations(file)

        return result
