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
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup 
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Join", callback_data="1"),
            InlineKeyboardButton("Leave", callback_data="2"),
        ],
        [InlineKeyboardButton("Rules/FAQ", callback_data="3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("\nL  W  F \nLubricaed Wank Fest\nLitle Whiny Fuck\nLMAO What Friends?!\nLego Wrecks Foot\nLetters With Friends!", reply_markup=reply_markup)

async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    if "1" == query.data:
        await parse(update, context)


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()