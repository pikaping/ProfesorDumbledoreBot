import random
from unittest import TestCase
from unittest.mock import patch, MagicMock

import profdumbledorebot.sql.support as support
import profdumbledorebot.supportmethods as supportmethods
from profdumbledorebot import fort, global_vars
from profdumbledorebot.model import Professions, Houses
from profdumbledorebot.sql import user


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


    def test_fortress_message_with_people(self):
        expected_fortress_message = 'Fortaleza organizada por: @david\\_8k\n*Hora*: 20:30\n*Lugar*: en un lugar muy lejano\n\nL30⚔💙 @david\\_8k\nL45📚💛 @edCullen\nL10🐾❤ @neville\\_longbottom'
        time = '20:30'
        place = 'en un lugar muy lejano'
        dict_users = [
            {
                'alias': 'david_8k',
                'profession': Professions.AUROR.value,
                'house': Houses.RAVENCLAW.value,
                'level': 30
            },
            {
                'alias': 'edCullen',
                'profession': Professions.PROFESSOR.value,
                'house': Houses.HUFFLEPUFF.value,
                'level': 45
            },
            {
                'alias': 'neville_longbottom',
                'profession': Professions.MAGIZOOLOGIST.value,
                'house': Houses.GRYFFINDOR.value,
                'level': 10
            }
        ]
        users = [Struct(**dict_user) for dict_user in dict_users]
        dict_creator = {
            'alias': 'david_8k',
        }

        TestCase.assertEqual(self, expected_fortress_message, fort.get_fortress_message(time, place, Struct(**dict_creator), users))


    def test_fortress_message_no_people(self):
        expected_fortress_message = 'Fortaleza organizada por: @david\\_8k\n*Hora*: 20:30\n*Lugar*: en un lugar muy lejano\n\nNo hay apuntados.'
        time = '20:30'
        place = 'en un lugar muy lejano'
        users = []
        dict_creator = {
            'alias': 'david_8k',
        }

        TestCase.assertEqual(self, expected_fortress_message, fort.get_fortress_message(time, place, Struct(**dict_creator), users))


    def test_time_place_formatter(self):
        fortress_tests = [
            ('/fort 20:30 en un lugar muy lejano', '20:30', 'en un lugar muy lejano'),
            ('/fort 20:3 en un lugar muy lejano', '20:00', ':3 en un lugar muy lejano'),
            ('/fort 20 en un lugar muy lejano', '20:00', 'en un lugar muy lejano'),
            ('/fort Se nos esta yendo la 20 pinza', '20:00', 'Se nos esta yendo la pinza'),
            ('/fort Se nos esta yendo 1 pinza a las 20:30', '20:30', 'Se nos esta yendo 1 pinza a las'),
            ('/fort Una fortaleza sin nombre y sin hora', None, 'Una fortaleza sin nombre y sin hora'),
        ]

        for fortress_test in fortress_tests:
            time, place = fort.get_time_place(fortress_test[0])
            TestCase.assertEqual(self, time, fortress_test[1], msg="In test {}".format(fortress_test[0]))
            TestCase.assertEqual(self, place, fortress_test[2], msg="In test {}".format(fortress_test[0]))

    @patch("telegram.bot.Bot")
    @patch("telegram.update.Update")
    def test_fortress_starts_correctly(self, mock_bot, mock_update):
        bot = mock_bot()
        update = mock_update()
        mocked_user = {
            'alias': 'david_8k',
            'level': 30,
            'profession': 3,
            'house': 3
        }
        supportmethods.extract_update_info = MagicMock(return_value=[self.chat_id, self.chat_type, self.user_id, self.text, self.message])
        support.are_banned = MagicMock(return_value=False)
        supportmethods.delete_message = MagicMock(return_value=True)
        user.get_user = MagicMock(return_value=Struct(**mocked_user))

        fort.start(bot, update)


    @patch("telegram.bot.Bot")
    @patch("telegram.update.Update")
    def test_user_banned_then_message_is_queued(self, mock_bot, mock_update):
        banned_message = "El usuario ha sido baneado y no puede realizar esta acción."
        bot = mock_bot()
        update = mock_update()
        supportmethods.extract_update_info = MagicMock(
            return_value=[self.chat_id, self.chat_type, self.user_id, self.text, self.message])
        supportmethods.delete_message = MagicMock(return_value=True)
        support.are_banned = MagicMock(return_value=True)

        fort.start(bot, update)

        support.are_banned.assert_called_with(self.user_id, self.chat_id)
        TestCase.assertIn(self, banned_message, global_vars.message_queue)
