# -*- coding: UTF-8 -*-
import os

import requests

from TamTamBot import UpdateCmn, CallbackButtonCmd
from TamTamBot.utils.lng import get_text as _, set_use_django
from TamTamBotDj.TamTamBotDj import TamTamBotDj
from openapi_client import NewMessageBody, UploadType, FileAttachment, NewMessageLink, MessageLinkType, MessageCreatedUpdate, CallbackButton, LinkButton, Intent, BotCommand


class BotFileToAudio(TamTamBotDj):

    @property
    def about(self):
        # type: () -> str
        return _('This bot creates, if possible, messages of type "audio" based on new files attached to your chats.\n'
                 'You need to add the bot to it as an administrator with the "Read all messages" and "Write, edit and delete messages" permissions.\n'
                 'To open the menu, type /menu.')

    @property
    def main_menu_buttons(self):
        # type: () -> []
        buttons = [
            [CallbackButtonCmd(_('About bot'), 'start', intent=Intent.POSITIVE)],
            # [CallbackButton(_('All chat bots'), '/list_all_chats', Intent.POSITIVE)],
            [LinkButton(_('Message to the developer'), 'mailto:asvbkr_bots@bk.ru')],
            [LinkButton(_('Chat to discuss the bot'), 'https://tt.me/FileToAudioChat')],
        ]
        if len(self.languages_dict) > 1:
            buttons.append([CallbackButtonCmd('Изменить язык / set language', 'set_language', intent=Intent.DEFAULT)])

        return buttons

    @property
    def description(self):
        # type: () -> str
        return 'Этот бот создаёт, по возможности, сообщения с типом "аудио" на основе новых файлов, прикрепляемым в ваших чатах.' \
               'Вам нужно добавить бота в качестве администратора с разрешениями «Читать сообщения» и "Писать, редактировать и удалять сообщения".\n\n' \
               'This bot creates, if possible, messages of type "audio" based on new files attached to your chats.' \
               'You need to add the bot to it as an administrator with the "Read all messages" and "Write, edit and delete messages" permissions.'

    def get_commands(self):
        # type: () -> [BotCommand]
        commands = [
            BotCommand('start', 'начать (о боте) | start (about bot)'),
            BotCommand('menu', 'показать меню | display menu'),
            BotCommand('set_language', 'изменить язык | set language'),
        ]
        return commands

    def handle_message_created_update(self, update):
        # type: (MessageCreatedUpdate) -> bool
        res = super().handle_message_created_update(update)
        if res is not None:
            return res

        update = UpdateCmn(update)
        if update and update.message and update.message.body:
            update.message.body.attachments = update.message.body.attachments or []
            ats = []
            names = []

            for attachment in update.message.body.attachments:
                if isinstance(attachment, FileAttachment):
                    self.lgz.debug('(%s).' % attachment)
                    url = attachment.payload.url
                    name = attachment.filename
                    names.append(name)
                    r = requests.get(url)
                    if r.status_code == 200:
                        ats.extend(self.attach_contents([(r.content, UploadType.AUDIO)]))
            if ats:
                mb = NewMessageBody(attachments=ats, link=NewMessageLink(MessageLinkType.REPLY, update.message.body.mid))
                mb.text = '; '.join(names)
                try:
                    self.send_message(mb, chat_id=update.chat_id)
                except Exception as e:
                    self.lgz.warning(e)

    @property
    def token(self):
        # type: () -> str
        token = os.environ.get('TT_BOT_API_TOKEN')
        return token


if __name__ == '__main__':
    set_use_django(False)
    bot = BotFileToAudio()
    bot.polling_sleep_time = 0
    bot.polling()
