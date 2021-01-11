# -*- coding: UTF-8 -*-
import os

import requests

from TamTamBot import CallbackButtonCmd, UpdateCmn, ChatExt
from TamTamBot.utils.lng import get_text as _
from TamTamBotDj.TamTamBotDj import TamTamBotDj
from openapi_client import BotCommand, Intent, ChatType, ChatAdminPermission, LinkButton, FileAttachment, UploadType, NewMessageLink, MessageLinkType, NewMessageBody, SimpleQueryResult


class TtbFileToAudio(TamTamBotDj):

    @property
    def token(self):
        # type: () -> str
        return os.environ.get('TT_BOT_API_TOKEN')

    @property
    def description(self):
        # type: () -> str
        return 'Этот бот создаёт (при возможности) сообщения с типом "аудио" на основе новых файлов, прикрепляемых в ваших чатах. ' \
               'Вам нужно добавить бота в качестве администратора с разрешениями «Читать сообщения» и "Писать, редактировать и удалять сообщения".\n' \
               'Чтобы открыть меню, введите /menu.\n\n' \
               'This bot creates, if possible, messages of type "audio" based on new files attached to your chats. ' \
               'You need to add the bot to it as an administrator with the "Read all messages" and "Write, edit and delete messages" permissions.\n' \
               'To open the menu, type /menu.'

    @property
    def about(self):
        # type: () -> str
        return self.description

    def get_commands(self):
        # type: () -> [BotCommand]
        commands = [
            BotCommand('start', 'начать (о боте) | start (about bot)'),
            BotCommand('menu', 'показать меню | display menu'),
            # BotCommand('list_all_chats', 'список всех чатов | list all chats'),
            # BotCommand('view_chats_available', 'доступные чаты | available chats'),
            # BotCommand('subscriptions_mng', 'управление подписками | managing subscriptions'),
            # BotCommand('view_chats_attached', 'подключенные чаты | attached chats'),
            # BotCommand('view_buttons_test', 'тест кнопок | buttons test'),

        ]
        if len(self.languages_dict) > 1:
            commands.append(BotCommand('set_language', 'изменить язык | set language'))
        return commands

    @property
    def main_menu_buttons(self):
        # type: () -> []
        buttons = [
            [CallbackButtonCmd(_('About bot'), 'start', intent=Intent.POSITIVE)],
            [LinkButton(_('Chat to discuss the bot'), 'https://tt.me/asvbkr_sup')],
        ]
        if len(self.languages_dict) > 1:
            buttons.append([CallbackButtonCmd('Изменить язык / set language', 'set_language', intent=Intent.DEFAULT, bot_username=self.username)])

        return buttons

    # Определяет разрешённость чата
    def chat_is_allowed(self, chat_ext, user_id=None):
        # type: (ChatExt, int) -> bool
        if isinstance(chat_ext, ChatExt):
            if user_id:
                pass
            ap = chat_ext.admin_permissions.get(self.user_id)
            return ap and ChatAdminPermission.WRITE in ap and ChatAdminPermission.READ_ALL_MESSAGES in ap

    def cmd_handler_view_chats_available(self, update):
        # type: (UpdateCmn) -> bool
        return bool(self.view_buttons_for_chats_available_direct(
            'Выберите/Select:', 'view_selected_chat_info', update.user_id, update.chat_id, {'type': 'доступный/available'}, update.link, update.update_current, True)
        )

    def cmd_handler_view_chats_attached(self, update):
        # type: (UpdateCmn) -> bool
        return bool(
            self.view_buttons_for_chats_attached(
                'Выберите/Select:', 'view_selected_chat_info', update.user_id, update.chat_id, {'type': 'подключенный/attached'}, update.link, update.update_current, True)
        )

    def cmd_handler_view_selected_chat_info(self, update):
        # type: (UpdateCmn) -> bool
        if not (update.chat_type in [ChatType.DIALOG]):
            return False

        if not (update.chat_id or update.user_id):
            return False

        if not update.this_cmd_response:  # Обрабатываем только саму команду
            if update.cmd_args:
                is_close = update.cmd_args.get('is_close')
                if is_close:
                    return True
                chat_id = update.cmd_args.get('chat_id')
                if chat_id is None:
                    parts = update.cmd_args.get('c_parts') or []
                    if parts and parts[0]:
                        chat_id = parts[0][0]
                if chat_id:
                    chat_ext = ChatExt(self.chats.get_chat(chat_id), self.title)
                    chat_type = update.cmd_args.get('type')
                    self.send_notification(
                        update,
                        f'chat_type: {chat_type}; chat_id={chat_id}; подключен/attached? {self.chat_is_attached(chat_ext.chat_id)}; {chat_ext.chat_name_ext}'
                    )
        return False

    def cmd_handler_view_buttons_test(self, update):
        lt = []
        for i in range(CallbackButtonCmd.MAX_ROWS * 20):
            lt.append([])
            for j in range(5):
                s = '%0.2d_%0.2d' % (i + 1, j + 1)
                # s = '+'
                lt[-1].append(CallbackButtonCmd(s, s, intent=Intent.DEFAULT, bot_username=self.username))

        self.view_buttons('Test', lt, user_id=update.user_id, add_close_button=True, add_info=True)

    def receive_message(self, update):  # type: (UpdateCmn) -> bool
        create_link = False
        delete_source = True
        if update and update.message and update.message.body:
            update.message.body.attachments = update.message.body.attachments or []
            ats = []
            names = []

            for attachment in update.message.body.attachments:
                if isinstance(attachment, FileAttachment):
                    self.lgz.debug('(%s).' % attachment)
                    url = attachment.payload.url
                    name = attachment.filename
                    if name:
                        name_l = name.split('.')
                        if len(name_l) > 1:
                            name = '.'.join(name_l[:-1])
                    names.append(name)
                    r = requests.get(url)
                    if r.status_code == 200:
                        ats.extend(self.attach_contents([(r.content, UploadType.AUDIO)]))
            if ats:
                if create_link:
                    link = NewMessageLink(MessageLinkType.REPLY, update.message.body.mid)
                else:
                    link = None
                mb = NewMessageBody(attachments=ats, link=link)
                mb.text = '; '.join(names)
                try:
                    self.send_message(mb, chat_id=update.chat_id)
                except Exception as e:
                    self.lgz.warning(e)
                else:
                    self.lgz.debug(f'it\'s all right!')
                    if delete_source:
                        self.lgz.debug(f'try delete source with id={update.message.body.mid}')
                        try:
                            res_d = self.msg.delete_message(update.message.body.mid)
                            if isinstance(res_d, SimpleQueryResult):
                                self.lgz.debug(f'result delete source with id={update.message.body.mid}: {res_d.success}-{res_d.message}')
                        except Exception as e:
                            self.lgz.warning(e)
        return True
