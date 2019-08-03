from unittest import TestCase

from profdumbledorebot.supportmethods import get_house_icon, get_profession_icon


class TestSupportMethods(TestCase):

    def test_get_profession_icon(self):
        expected_values = [
            (0, '❓'),
            (1, '📚'),
            (2, '🐾'),
            (3, '⚔')
        ]
        for expected_value in expected_values:
            TestCase.assertEqual(self, expected_value[1], get_profession_icon(expected_value[0]))

    def test_get_house_icon(self):
        expected_values = [
            (0, '❓'),
            (1, '❤'),
            (2, '💛'),
            (3, '💙'),
            (4, '💚')
        ]
        for expected_value in expected_values:
            TestCase.assertEqual(self, expected_value[1], get_house_icon(expected_value[0]))
