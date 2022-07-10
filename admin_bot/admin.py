import logging
import configparser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update 
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)

from inline import add_or_remove_option, get_ini_keyboard, get_sections_keyboard, section_details, revert
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

#configurations parsing
logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.optionxform = str
config.read('./config_files/admin_bot.ini')
BOTTOKEN = config.get('Bot', 'TOKEN')
owner_names = list(dict(config['owner']).values())

def start(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    if not update.message.from_user.username in owner_names:
        update.message.reply_text(
            "You are not authorized"
        ) 
        msg = update.message.reply_text(
            "", reply_markup=ReplyKeyboardRemove()
        )
        return 1
    update.message.reply_text(
        "Welcome, Please pick a config file to add or remove values.",
        reply_markup= get_ini_keyboard() 
    )
    return 1

def convo_entry(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    if not update.message.from_user.username in owner_names:
        update.message.reply_text(
            "You are not authorized"
        )
    msg = update.message.reply_text(
        "", reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_text(
        "Welcome, Please pick a config file to add or remove values.",
        reply_markup= get_ini_keyboard() 
    )
    return 1

def choose_section(update: Update, context: CallbackContext) -> int:
    context.user_data["file"] = update.message.text
    update.message.reply_text(
        "Now choose which section you want to operate on",
        reply_markup= get_sections_keyboard(context.user_data["file"])
    ) 
    return 2

def show_details_and_functions(update: Update, context: CallbackContext) -> int:
    context.user_data["section"] = update.message.text
    update.message.reply_text(
        "These are current values of the section you chose" + section_details(context.user_data["file"], update.message.text),
        reply_markup= InlineKeyboardMarkup([[
            InlineKeyboardButton("Add", callback_data="add"),
            InlineKeyboardButton("Remove", callback_data="remove"),
            InlineKeyboardButton("Edit", callback_data="edit"),
            ]]),
        disable_web_page_preview=True   
    )
    return 3

def handle_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == "add":
        context.user_data["operation"] = "add"
        context.bot.send_message(
            query.from_user.id,
            """ Type in the new key and value in the following form.
            key = value """
        )
    elif query.data == "remove":
        context.user_data["operation"] = "remove"
        context.bot.send_message(
            query.from_user.id,
            """ Type in the key of the row you want to remove."""
        )
    elif query.data == "edit":
        context.user_data["operation"] = "edit"
        context.bot.send_message(
                query.from_user.id,
                """Type the key you want to edit in the following form. 
                    key = new value."""
                    )
    return 4

def add_or_remove(update: Update, context: CallbackContext) -> int:
    file_name = context.user_data["file"]
    operation = context.user_data["operation"]
    section = context.user_data["section"]
    message = update.message.text
    key = message.split("=")[0]
    if "=" in message:
        value = message.split("=")[1]
    else:
        value = None
    add_or_remove_option(file_name, operation, section, key, value)
    update.message.reply_text(
        """The operation is done!.
        Send /start again to start over"""
    )
    return ConversationHandler.END

def stop_convo(update: Update, context: CallbackContext):
    return ConversationHandler.END

def undo(update: Update, context: CallbackContext):
    # read the last line
    with open('./admin_bot/undo_log.txt') as logfile:
        lines = logfile.readlines()
        last_action_log = lines[-1]
        # revert the change
        revert(last_action_log)
    # delete the last line
    with open('./admin_bot/undo_log.txt', 'w+') as logfile:
        logfile.writelines(lines[:-1])
    # reply with message
    update.message.reply_text(
            "Undo of the last action ("+ last_action_log +") complete."
            )
            

def main() -> None:
    """Run the bot."""
    updater = Updater(BOTTOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(ConversationHandler(
        entry_points= [
            CommandHandler("start", start),
            MessageHandler(Filters.regex("ssss"), convo_entry),
        ],
        states = {
            1 : [(MessageHandler(Filters.text, choose_section))],
            2 : [(MessageHandler(Filters.text, show_details_and_functions))],
            3 : [(CallbackQueryHandler(handle_callback))],
            4 : [MessageHandler(Filters.text, add_or_remove)]
        }, 
        fallbacks= [MessageHandler(Filters.regex("stop"), stop_convo)],
        allow_reentry=True,
        conversation_timeout=30,
    )),
    dispatcher.add_handler(CommandHandler("undo", undo))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()
