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
import string
import random

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
from telegram import     (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PollAnswerHandler,
    PollHandler,
    PicklePersistence
)
answerssubmitted=0
currentPuzzle=''
playingDict = {}
scoreDict = {}
partyleader=''
roundstarted=0
answerDict={}
totalrounds=3
currentround=1
votedList=[]
leaderkey=0
totalplaying=0
usedchars=[]
requiredplayers=2
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN="6270603273:AAHLTXrg6ozchgm--iSarxsVzQCewMlwtKM"
STARTGAME, WAITFORANSWER, VOTINGROUND, FINISH = range(4)

async def setplayers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global totalplaying
    global requiredplayers
    user = update.message.from_user
    requiredplayers=int(update.message.text.replace("/setplayers ", "").strip())
    replytext=f"Required players count changed to {requiredplayers}"
    await update.message.reply_text(
            replytext
        )


def random_char(y):
    global usedchars
    unwanted_chars=f"{usedchars}x"
    onlyonce_chars="vzqk"
    generation=''.join(random.choice([s for s in string.ascii_letters.lower() if s not in unwanted_chars]) for x in range(y))
    reroll=''
    lettertoadd=''
    for letter in list(generation):
        if letter in onlyonce_chars:
            if letter in usedchars:
                lettertoadd+=random.choice(string.ascii_letters.lower())
            else:
                usedchars+=letter
                lettertoadd+=letter
        else:
            lettertoadd+=letter
    return lettertoadd

async def lwf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""
    global totalplaying
    global requiredplayers
    if "New match" in update.message.text or "Rematch" in update.message.text:
        reply_keyboard = [["Join game"], ["Quit"], ["How to play"], ["Additional options."]]
        return STARTGAME
    else:
        reply_keyboard = [["Join game", "Force start"], ["Quit", "Set max players"], ["How to play", "Other options"]]
    await update.message.reply_text(
        "Whatup dude? click \"Join game\" to join the game!\n"
        "If you don't want to see these messages click \"No thanks.\"",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,selective=true, input_field_placeholder="Join game!"
        ),
    )
    print("about to hit up startgame)")
    return STARTGAME

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Users join the game until total player count is met."""
    global totalplaying
    global playingDict
    global requiredplayers
    global currentPuzzle
    replytext=""
    user = update.message.from_user
    if "Rematch" in update.message.text:
        replytext = update.message.text
    elif "Quit" in update.message.text:
        quitgame()
    elif "Join" in update.message.text:
        playingDict.update({user.id: user.first_name})
        totalplaying=totalplaying+1
        if totalplaying==requiredplayers:
            text=f"Players: {totalplaying}/{requiredplayers}\nStarting game!"
        else:
            text=f"Players: {totalplaying}/{requiredplayers}\nWaiting for more to join..."
        playertext=""
        current=0
        for key in playingDict.keys():
            if current!=0:
                playertext += f"\n{playingDict[key]}"
            else:
                current=1
                playertext = f"{playingDict[key]}"
        replytext=f"{text}\n\nPlayers:\n{playertext}"
    if totalplaying==requiredplayers:
        currentPuzzle=random_char(3)
        replytext=f"Write an acronym that starts with these the following {len(currentPuzzle)} characters!\n\n{currentPuzzle.upper()}"
        await update.message.reply_text(
            replytext, reply_markup=ReplyKeyboardRemove()
        )
        return WAITFORANSWER
    else:
        await update.message.reply_text(
            text, reply_markup=ReplyKeyboardRemove()
        )
        return

def quitgame():
    playingDict.clear()
    totalplaying.clear()
    answerDict.clear()
    scoreDict.clear()
    votedList.clear()
    usedchars.clear()
    currentPuzzle=''


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE, question='', answers=[]) -> None:
    """Sends answers users submitted."""
    questions=answers.copy()
    message = await context.bot.send_poll(
        update.effective_chat.id,
        question,
        questions,
        is_anonymous=True,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)

async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reveal the votes!"""
    global totalplaying
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    try:
        questions = answered_poll["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    await context.bot.send_message(
        answered_poll["chat_id"],
        f"{update.effective_user.mention_html()} feels {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    answered_poll["answers"] += 1
    # Close poll after three participants voted
    if answered_poll["answers"] == totalplaying:
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
        return VOTINGROUND

async def waitforanswer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Waits for text input from players"""
    global answerDict
    global currentPuzzle
    global totalplaying
    global requiredplayers
    global answerssubmitted
    global playingDict
    if totalplaying < requiredplayers:
        return
    user = update.effective_user
    if user.id not in playingDict:
        print("User not in player list.")
        return
    if user.id in answerDict:
        print("User already submitted")
        return
    response = update.message.text
    response = response.strip()
    while '  ' in response:
        response = response.replace('  ', ' ')
    currentnum=0
    replytext=""
    for respon in response.split():
        if list(currentPuzzle)[currentnum].lower() == list(respon)[0].lower():
            if len(list(respon)) == 1:
                if respon.lower().strip() in "iuryac":
                    currentnum+=1
                else:
                    print(f"ERROR: generic answer given in Bacronym(letter {curentPuzzle[currentnum]})")
            else:
              currentnum+=1
        else:
            print("ERROR:Non matching acronym!")
            return
    if currentnum == len(currentPuzzle):
        answerssubmitted+=1
        answerDict.update({user.id: response})
        curr=0
        for key in answerDict.keys():
            if curr==0:
                replytext+=f"Submitted:\n{playingDict[key]}"
                curr+=1
            else:
                replytext+=f"\n{playingDict[key]}"
        await update.message.reply_text(
            replytext
        )
    if answerssubmitted==len(playingDict):
        values=[]
        for keyfer in answerDict.keys():
            values.append(str(answerDict[keyfer]))
        await poll(update, context, str(currentPuzzle), values)
    return

async def votinground(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global scoreDict
    global votedNumber
    global playingDict
    global votedList
    global currentround
    global currentPuzzle
    global totalrounds
    global answerssubmitted
    user = update.message.effective_user
    if user.id in votedList:
        return
    validname=0
    for key in playingDict.keys():
        if update.effective_message.text == playingDict[user.id]:
            print("You can't vote for yourself!")
            if answerssubmitted==len(playingDict):
                nameList=[]
                replytext='Submissions:'
                for keyy in playingDict.keys():
                    if keyy != user.id:
                        nameList.append(playingDict[keyy])
                        replytext+=f"\n{playingDict[keyy]}: {answerDict[key]}"
                await update.effective_message(
                    replytext,
                    reply_markup=ReplyKeyboardMarkup(
                        [nameList], resize_keyboard=True, one_time_keyboard=False ,selective=True, input_field_placeholder="DONT TYPE BEFORE VOTING!"
                    ),
                )
        if update.message.text in playingDict[key]:
            if key in scoreDict:
                validname=1
                score=int(scoreDict[key])+1
                scoreDict.update({key: score})
            else:
                validname=1
                score=1
                scoreDict.update({key: score})
    if validname==0:
        return VOTINGROUND
    votedList.append(user.id)
    replytext='Totals:'
    if len(votedList) ==  len(playingDict):
        for key in scoreDict.keys():
            replytext+=f"\n{playingDict[key]}: {scoreDict[key]}"
        await update.effective_message(
            replytext,
        )
        if currentround < totalrounds:
            currentPuzzle=random_char(3+int(currentround))
            currentround+=1
            replytext=f"Write an acronym that starts with these the following {len(currentPuzzle)} characters!\n\n{currentPuzzle.upper()}"
            await update.message.reply_text(
                replytext,
                reply_markup=ReplyKeyboardRemove(),
            )
            answerDict.clear()
            votedList.clear()
            answerssubmitted=0
            return WAITFORANSWER
        if currentround==totalrounds:
            highestnumber=0
            champion=''
            tie=False
            dupes=0
            replytext="THAT'S IT! FINAL SCORES:"
            for key in scoreDict.keys():
                replytext+=f"\n{playingDict[key]} - {scoreDict[key]}"
                if int(scoreDict[key])==highestnumber:
                    dupes+=1
                if int(scoreDict[key]) > highestnumber:
                    dupes=0
                    highestnumber=int(scoreDict[key])
                    champion=playingDict[key];
            for key in scoreDict.keys():
                if champion!=key:
                    if highestnumber==scoreDict[key]:
                        tie=True
            if dupes==0:
                replytext+=f"\n\n\nWinner - {champion}"
            else:
                replytext+="\n\n\nTIE B-B-B-B-BRAKER"
                replytext+=f"\n\nWhoops, not ready yet. For now lets just say that whoever had {highestnumber} points won! Share the victory dammnit!"
                #TODO: DEAL WITH TIE BREAKER
                reply_keyboard = [["Rematch", "New match", "Quit game"]]
                replytext+= "\n\nSo - what next, lil bitch?"
                await update.message.reply_text(
                    replytext,
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True, input_field_placeholder="What next?!"
                    ),
                )
                currentround=0
                scoreDict.clear()
                return FINISH

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ADD FINISH SHIT
    global answerDict
    global scoreDict
    global votedList
    global usedchars
    global currentPuzzle
    global playingDict
    text=update.message.text
    if "Rematch" in text:
        answerDict.clear()
        scoreDict.clear()
        votedList.clear()
        usedchars.clear()
        currentPuzzle=''
        return STARTGAME
    elif "New match" in text:
        playingDict.clear()
        answerDict.clear()
        totalplaying.clear()
        scoreDict.clear()
        votedList.clear()
        usedchars.clear()
        currentPuzzle=''
        return STARTGAME
    elif "Quit game" in text:
        playingDict.clear()
        totalplaying.clear()
        answerDict.clear()
        scoreDict.clear()
        votedList.clear()
        usedchars.clear()
        currentPuzzle=''
        await update.message.reply_text(
            "Rock on! If you want to start a game later just type /lwf!", reply_markup=ReplyKeyboardRemove()
         )
        return ConversationHandler.END
    print("game over")
    return

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
    persistence = PicklePersistence(filepath="LFWpickle")
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(TOKEN)
        .concurrent_updates(False)
        .arbitrary_callback_data(True)
        .build()
    )
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("lwf", lwf)],
        states={
            STARTGAME: [MessageHandler(filters.Regex("^(Join game|No thanks|Start game|New match|Rematch|Quit)$"), startgame)],
            WAITFORANSWER: [MessageHandler(filters.TEXT, waitforanswer)],
            VOTINGROUND: [MessageHandler(filters.TEXT, votinground)],
            FINISH: [MessageHandler(filters.TEXT, finish)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_user=False,
        per_chat=True,
        per_message=False
    )
    application.add_handler(CommandHandler("setplayers", setplayers))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("poll", poll))
    application.run_polling()
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))

if __name__ == "__main__":
    main()