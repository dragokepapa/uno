#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext
from functools import wraps

from locales import available_locales
from pony.orm import db_session
from user_setting import UserSetting
from shared_vars import gm

GETTEXT_DOMAIN = 'unobot'
GETTEXT_DIR = 'locales'


class _Underscore(object):
    """Class to emulate flufl.i18n behaviour, but with plural support"""

    def __init__(self):
        # ✅ FIXED PART (no crash now)
        self.translators = {
            locale: gettext.translation(
                GETTEXT_DOMAIN,
                localedir=GETTEXT_DIR,
                languages=[locale],
                fallback=True  # 🔥 prevents crash
            )
            for locale in available_locales.keys()
            if locale != 'en_US'
        }
        self.locale_stack = []

    def push(self, locale):
        self.locale_stack.append(locale)

    def pop(self):
        if self.locale_stack:
            return self.locale_stack.pop()
        return None

    @property
    def code(self):
        if self.locale_stack:
            return self.locale_stack[-1]
        return None

    def __call__(self, singular, plural=None, n=1, locale=None):
        if not locale:
            if not self.locale_stack:
                locale = 'en_US'
            else:
                locale = self.locale_stack[-1]

        if locale not in self.translators:
            return singular if n == 1 else plural

        translator = self.translators[locale]

        if plural is None:
            return translator.gettext(singular)
        else:
            return translator.ngettext(singular, plural, n)


_ = _Underscore()


def __(singular, plural=None, n=1, multi=False):
    """Translates text into all locales on the stack"""
    translations = []

    if not multi and len(set(_.locale_stack)) >= 1:
        translations.append(_(singular, plural, n, 'en_US'))
    else:
        for locale in _.locale_stack:
            translation = _(singular, plural, n, locale)
            if translation not in translations:
                translations.append(translation)

    return '\n'.join(translations)


def user_locale(func):
    @wraps(func)
    @db_session
    def wrapped(update, context, *pargs, **kwargs):
        user = _user_chat_from_update(update)[0]

        us = UserSetting.get(id=user.id)

        if us and us.lang != 'en':
            _.push(us.lang)
        else:
            _.push('en_US')

        result = func(update, context, *pargs, **kwargs)
        _.pop()
        return result

    return wrapped


def game_locales(func):
    @wraps(func)
    @db_session
    def wrapped(update, context, *pargs, **kwargs):
        user, chat = _user_chat_from_update(update)
        player = gm.player_for_user_in_chat(user, chat)

        locales = []

        if player:
            for p in player.game.players:
                us = UserSetting.get(id=p.user.id)

                if us and us.lang != 'en':
                    loc = us.lang
                else:
                    loc = 'en_US'

                if loc in locales:
                    continue

                _.push(loc)
                locales.append(loc)

        result = func(update, context, *pargs, **kwargs)

        while _.code:
            _.pop()

        return result

    return wrapped


def _user_chat_from_update(update):
    user = update.effective_user
    chat = update.effective_chat

    if chat is None and user is not None and user.id in gm.userid_current:
        chat = gm.userid_current.get(user.id).game.chat

    return user, chat