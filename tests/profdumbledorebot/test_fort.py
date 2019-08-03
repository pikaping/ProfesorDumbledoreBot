import random
from unittest import TestCase
from unittest.mock import patch, MagicMock

import profdumbledorebot.sql.support as support
import profdumbledorebot.supportmethods as supportmethods
from profdumbledorebot import fort


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class TestFort(TestCase):

    def setUp(self):
        self.chat_id = random.randint(-10000, 0)
        self.chat_type = 'supergroup'
        self.user_id = random.randint(1, 10001)
        self.text = '/fort blabla'
        self.obj_message = {
            'message_id': random.randint(1, 10000),
            'date': 1564825321,
            'chat': {
                'id': self.chat_id,
                'type': self.chat_type
            },
            'text': self.text,
            'from': {
                'id': self.user_id,
                'is_bot': False,
                'language_code': 'en'
            }
        }
        self.message = Struct(**self.obj_message)

    def x(self):
        pass

    @patch("telegram.bot.Bot")
    @patch("telegram.update.Update")
    def test_fortress_starts_correctly(self, mock_bot, mock_update):
        bot = mock_bot()
        update = mock_update()
        supportmethods.extract_update_info = MagicMock(return_value=[self.chat_id, self.chat_type, self.user_id, self.text, self.message])
        supportmethods.delete_message = MagicMock(return_value=True)
        support.are_banned = MagicMock(return_value=False)

        fort.start(bot, update)

        support.are_banned.assert_called_with(self.user_id, self.chat_id)

    @patch("telegram.bot.Bot")
    @patch("telegram.update.Update")
    def test_user_banned_then_message_is_queued(self, mock_bot, mock_update):
        global message_queue
        banned_message = "El usuario ha sido baneado y no puede realizar esta acción."
        bot = mock_bot()
        update = mock_update()
        supportmethods.extract_update_info = MagicMock(
            return_value=[self.chat_id, self.chat_type, self.user_id, self.text, self.message])
        supportmethods.delete_message = MagicMock(return_value=True)
        support.are_banned = MagicMock(return_value=True)

        fort.start(bot, update)

        support.are_banned.assert_called_with(self.user_id, self.chat_id)
        TestCase.assertIn(self, banned_message, message_queue)
