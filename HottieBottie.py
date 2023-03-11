#!/home/becky/python-telegram-bot/venv/bin python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import time
import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence,
)
playingDict = {}
totalplaying=0
requiredplayers=5
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN="6270603273:AAHLTXrg6ozchgm--iSarxsVzQCewMlwtKM"
PARSE, LOCATION, BIO = range(3)

async def lwf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""
    reply_keyboard = [["Join game", "No thanks."]]
    await update.message.reply_text(
        "Whatup dude? click \"Join game\" to join the game!\n"
        "If you don't want to see these messages click \"No thanks.\"",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Want to join?!"
        ),
    )
    return PARSE

async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    global totalplaying
    replytext=""
    user = update.message.from_user
    if "Join" in update.message.text:
        playingDict.update({user.id: user.first_name})
        totalplaying=totalplaying+1
        if totalplaying==requiredplayers:
            text=f"Players: {totalplaying}/{requiredplayers}\nReady to start game!"
        else:
            text=f"Players:{totalplaying}/{requiredplayers}\nWaiting for more to join..."
        playertext=""
        current=0
        for key in playingDict:
            if current!=0:
                playertext += f"\n{playingDict[key]}"
            else:
                current=1
                playertext = f"{playingDict[key]}"
        replytext=f"{text}\n\nPlayers:\n{playertext}"
    await update.message.reply_text(
        replytext,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def buttonMashed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    print("Deez Nuts")
    query = update.callback_query
    await query.answer()
    print(query)
    # Get the data from the callback_data.
    # If you're using a type checker like MyPy, you'll have to use typing.cast
    # to make the checker get the expected type of the callback_data
    print(f"DEEZ NUTS: {query.data}")
    # we can delete the data stored for the query, because we've replaced the buttons

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .arbitrary_callback_data(True)
        .build()
    )
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("lwf", lwf)],
        states={
            PARSE: [MessageHandler(print(""), parse)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()