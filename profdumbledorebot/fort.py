import profdumbledorebot.globals
import profdumbledorebot.sql.support as support
import profdumbledorebot.supportmethods as supportmethods


def start(bot, update):
    """Start fortress"""
    chat_id, chat_type, user_id, text, message = supportmethods.extract_update_info(update)
    supportmethods.delete_message(chat_id, message.message_id, bot)

    if support.are_banned(user_id, chat_id):
        profdumbledorebot.globals.message_queue.append("El usuario ha sido baneado y no puede realizar esta acción.")
        return
