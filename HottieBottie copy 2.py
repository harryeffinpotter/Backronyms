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
from telegram.constants import ParseMode
answerssubmitted=0
currentPuzzle=''
totalrounds=3
players_dict= {}
roundinfo = {}
requiredplayers=2
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN="6270603273:AAHLTXrg6ozchgm--iSarxsVzQCewMlwtKM"
STARTGAME, WAITFORANSWER, VOTINGROUND, FINISH = range(4)

async def setplayers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global players_dict
    user = update.message.from_user
    players_dict.update({ user.id: {'name': user.first_name, 'answer': '', 'score': 0, 'lastround': 0}})
    requiredplayers=int(update.message.text.replace("/setplayers ", "").strip())
    replytext=f"Required players count changed to {requiredplayers}"
    await update.message.reply_text(
            replytext
        )

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

    except (IndexError, ValueError):


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


def random_char(y) -> str:
    global currentPuzzle
    unwanted_chars="xvzpqkj"
    new = ''.join(random.choice([s for s in string.ascii_lowercase if s not in unwanted_chars]) for x in range(y))
    currentPuzzle=new.upper()
    return currentPuzzle

async def lwf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""
    global totalplaying
    global requiredplayers
    playingDict.update({user.id: user.first_name})
    if totalplaying>=requiredplayers:
        return WAITFORANSWER
    elif totalplaying+1==requiredplayers:
        totalplaying=totalplaying+1
        text=f"Players: {totalplaying}/{requiredplayers}\nMax players reached...\nStarting game!"
    else:
        totalplaying=totalplaying+1
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
    return STARTGAME

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Users join the game until total player count is met."""
    global totalplaying
    global playingDict
    global requiredplayers
    global currentPuzzle
    replytext=""
    user = update.message.from_user
    if totalplaying==requiredplayers:
        currentPuzzle=random_char(3)
        replytext=f"Write an acronym that starts with these the following {len(currentPuzzle)} characters!\n\n{currentPuzzle.upper()}"
        await update.message.reply_text(
            replytext, reply_markup=ReplyKeyboardRemove()
        )
        return WAITFORANSWER
    else:
        await update.message.reply_text(
            text
        )
        return

def quitgame():
    global votedNumber
    global votedList
    global currentround
    global answerssubmitted
    global scoreDict
    global answerDict
    global totalplaying
    global requiredplayers
    global answerssubmitted
    global playingDict
    globalPuzzle=''
    playingDict.clear()
    answersubmitted.clear()
    totalplaying.clear()
    answerDict.clear()
    scoreDict.clear()
    votedList.clear()
    usedchars.clear()
    currentround=0
    votedNumber=0
    currentPuzzle=''




async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE, question='', answers=[]) -> None:
    """Sends answers users submitted."""
    questions=answers.copy()
    message = await context.bot.send_poll(
        update.effective_chat.id,
        question.upper(),
        questions,
        is_anonymous=False,
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
    global playingDict
    global currentround
    global answerDict
    global totalrounds
    global scoreDict
    user = update.effective_user
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
    for key in answerDict.keys():
        if answer_string == answerDict[key]:
            if key in scoreDict:
                scoreDict.update({key: scoreDict[key]+1})
            else:
                scoreDict.update({key: 1})
    if user.id in playingDict:
        answered_poll["answers"] += 1
    # Close poll after three participants voted
    if answered_poll["answers"] == totalplaying:
        if currentround == totalrounds:
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
            await context.bot.send_message(
                answered_poll["chat_id"],
                replytext
            )
            currentround=0
            scoreDict.clear()
            return FINISH
        else:
            await context.bot.send_message(
                answered_poll["chat_id"],
                f"NEXT BACKRONYM: {random_char(currentround+3)}"
            )
            answerDict.clear()
            currentround=currentround+1
            await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
            return WAITFORANSWER
    return WAITFORANSWER

async def waitforanswer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Waits for text input from players"""
    global answerDict
    global currentPuzzle
    global totalplaying
    global requiredplayers
    global answerssubmitted
    global playingDict
    global currentround
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
        answerssubmitted=0
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
    user = update.effective_user
    validname=0
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
            await update.effective_message(
                replytext,
            )
            currentround=0
            scoreDict.clear()
            return FINISH
    if len(votedList) ==  len(playingDict):
        for key in scoreDict.keys():
            replytext+=f"\n{playingDict[key]}: {scoreDict[key]}"


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
        quitgame()
    elif "Quit game" in text:
        quitgame()
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


async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    await update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )

def main() -> None:
    """Run the bot."""
    global roundinfo
    
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

    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(MessageHandler (filters.Regex("^(Reset Game)$"), quitgame))
    application.run_polling()

if __name__ == "__main__":
    main()