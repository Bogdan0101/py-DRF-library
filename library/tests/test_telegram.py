from unittest.mock import patch
from django.test import TestCase
from library.telegram import send_telegram_message


class TelegramTests(TestCase):

    @patch("library.telegram.requests.post")
    def test_send_telegram_message(self, mock_post):
        mock_post.return_value.ok = 200
        result = send_telegram_message("test")
        self.assertTrue(result)
        mock_post.assert_called_once()
