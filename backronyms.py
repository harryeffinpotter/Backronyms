#!/home/becky/python-telegram-bot/venv/bin python
# pylint: disable = unused-argument, wrong-import-position
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
from datetime import datetime
import logging
import random
import time
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

from telegram import (
    ReplyKeyboardRemove,
    Update,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    PicklePersistence,
    ConversationHandler,
    MessageHandler,
    filters,
    PollAnswerHandler,
)


# Enable logging
now = datetime.now()
now = now.strftime('%H_%M_%d_%m_%Y.log')
logging.basicConfig(
    encoding='utf-8', level=logging.INFO
)
tokenfile = open("bot.token", "r")
TOKEN = tokenfile.read()
WAITFORANSWER, FINISH = range(2)


async def nfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatid = update.effective_chat.id
    if chatid not in context.bot_data:
        await update.message.reply_text("No settings found./")
        return
    basedict = context.bot_data[chatid]
    await update.message.reply_text(
        f"*{basedict['requiredplayers']}* `/players` (default: 3, max 20)\n"
        f"*{basedict['totalrounds']}* `/rounds` (default: 3, max 20)\n"
        f"*{basedict['timelimit']}* `/timelimit` (in seconds, default: 45, max 6000)",
        parse_mode="Markdown"
    )


async def rep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = str(update.effective_message.text)
    text = text.replace('/rep', '')
    text = text.replace("@backronyms_bot", "")
    text = text.strip()
    user = update.effective_user
    if user.id in context.bot_data:
        replytext = f"{user.full_name}'s reputation score is {context.bot_data[user.id]['rep']}!"
        await update.message.reply_text(
            replytext
        )
    else:
        replytext = f"{user.full_name} has no reputation!"
        await update.message.reply_text(
            replytext
        )


async def timelimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatid = update.effective_chat.id
    text = str(update.effective_message.text)
    text = text.replace('/timelimit', '')
    text = text.replace("@backronyms_bot", "")
    text = text.strip()
    if int(text) < 5 or int(text) > 6000:
        if int(text) > 6000:
            replytext = (
                f"{int(text)} is too many seconds, 6000"
                "(60 minutes/1 hour) is the maximum allowed!"
            )
        if int(text) < 5:
            replytext = f"{int(text)} is too few seconds, 5 is the minimum allowed!"
        await update.message.reply_text(
            replytext
        )
        return
    if 'timelimit' not in context.bot_data[chatid]:
        context.bot_data[chatid]['timelimit'] = int(text)
    else:
        context.bot_data[chatid]['timelimit'] = int(text)
    replytext = f"Time limit changed to {text} seconds"
    await update.message.reply_text(
        replytext
    )


async def players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set required number of players to start game."""
    chatid = update.effective_chat.id
    text = str(update.effective_message.text)
    # Remove /commandname@botname from command.
    text = text.replace('/players', '')
    text = text.replace("@backronyms_bot", "")
    text = text.strip()
    # Remove any spaces from the front and back of the supplied message
    if int(text) < 2 or int(text) > 20:
        if int(text) > 20:
            replytext = f"{int(text)} is too many players, 20 is the maximum allowed!"
        if int(text) < 2:
            replytext = f"{int(text)} is too few players, 2 is the minimum allowed!"
        await update.message.reply_text(
            replytext
        )
        return
    if chatid not in context.bot_data:
        context.bot_data[chatid] = {}
    context.bot_data[chatid]['requiredplayers'] = int(text)
    requiredplayers = context.bot_data[chatid]['requiredplayers']
    replytext = f"Required players count changed to {requiredplayers}"
    await update.message.reply_text(
        replytext
    )


async def rounds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatid = update.effective_chat.id
    user = update.effective_user
    text = str(update.effective_message.text)
    text = text.replace('/rounds', '')
    text = text.replace("@backronyms_bot", "")
    text = text.strip()
    if int(text) < 2 or int(text) > 20:
        if int(text) > 20:
            replytext = f"{int(text)} is too many rounds, 20 is the maximum allowed!"
        if int(text) < 2:
            replytext = f"{int(text)} is too few rounds, 2 is the minimum allowed!"
        await update.message.reply_text(
            replytext
        )
        return
    if user.id not in context.bot_data:
        context.bot_data[chatid] = {}
    context.bot_data[chatid]['totalrounds'] = int(text)
    totalrounds = context.bot_data[chatid]['totalrounds']
    replytext = f"Total rounds set to {totalrounds}"
    await update.message.reply_text(
        replytext
    )


async def make_puzzle(chatid, context: ContextTypes.DEFAULT_TYPE):
    basedict = context.bot_data[chatid]
    players = basedict['players']
    for key in players.keys():
        players[key]['answer'] = ''
    time.sleep(3)
    basedict['currentpuzzle'] = await random_char(basedict['round'] + 3)
    basedict['round'] += 1
    formattedpuzzle = basedict['currentpuzzle'].replace("", "     ")[1: -1]
    extrasymbol = "="
    for x in range(basedict['round'] * 3):
        extrasymbol += "="
    replytext = f"MAKE A BACKRONYM FOR:\n\n========{extrasymbol}\n*{formattedpuzzle}*\n{extrasymbol}========"
    if 'tiebreaker' in basedict:
        await set_timer(chatid, context)
    await botmsg(replytext, chatid, context)


async def random_char(y) -> str:
    char = ''
    letterstouse = (
        "abcdefghijklmnopqrstuvwy"
        "abcdefhilmnoprstw"
        "abcfhimopstw"
        "aciost"
    )
    for x in range(y):
        char += random.choice([s for s in letterstouse])
    char = char.upper()
    return char


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""
    user = update.effective_user
    chatid = update.effective_chat.id
    if chatid not in context.bot_data:
        context.bot_data[chatid] = {
            'round': 0,
            'totalrounds': 3,
            'requiredplayers': 3,
            'rtype': 'answering',
            'answers': [],
            'players': {},
            'pollvoted': 0
        }
        basedict = context.bot_data[chatid]
    else:
        basedict = context.bot_data[chatid]
    basedict = context.bot_data[chatid]
    basedict['pollvoted'] = 0
    oldpolls = []
    for key in context.bot_data:
        if 'questions' in context.bot_data[key]:
            oldpolls.append(key)
    for polldata in oldpolls:
        del context.bot_data[polldata]
    requiredplayers = basedict["requiredplayers"]
    if 'players' in basedict:
        players = basedict['players']
        if len(players) >= requiredplayers:
            await update.message.reply_text(
                (
                    "Sorry, the current round is full, each round only lasts a "
                    "few mintues so be ready to join the next one!\n"
                    "Don't forget to send `/players` # to increase the maximum players!"
                )
            )
            return
        if user.id in players:
            return
        players[user.id] = {
            'name': user.full_name,
            'score': 0,
            'answer': ''
        }
    else:
        basedict['players'] = {
            user.id: {
                'name': user.full_name,
                'score': 0,
                'answer': ''
            }
        }
    if len(players) == requiredplayers:
        basedict['round'] = 0
        text = (
            f"{user.full_name} has joined!\n\n"
            f"{len(players)}/{requiredplayers} players joined."
            "\nStarting game!."
        )

        await update.message.reply_text(
            text,
            parse_mode='Markdown'
        )
        await make_puzzle(chatid, context)
    else:
        if len(context.bot_data[chatid]['players']) == 1:
            basedict['started'] = 0
            playertext = (
                "Acronyms - a `set of letters that represent specific words.`\n"
                "*BACKRONYMS* - `a set of words that represent specific letters.`\n\n"
                "*Example:*\n=========="
                "\n*T F L M T P*\n"
                "(*T*)he (*F*)irst (*L *)etters (*M*)atch (*T*)he (*P*)rompt\n"
                "==========\nPrompt: TFLMTP\n"
                "Answer: The First Letters Match The Prompt\n\n"
                "Notes:\n-Audience member votes are equal to player votes!\n\n"
                "Change # of players:\n`/players`\n"
                "Change # of rounds:\n`/rounds`\n"
                "Change time limit (# of seconds):\n"
                "`/timelimit`\n\n"
                f"{len(players)}/{requiredplayers} | Rounds: {basedict['totalrounds']}\n\n"
                f"Started by:\n{user.full_name}\n"
                "Click to join -> /join"
            )
        else:
            playertext = (
                f"{user.full_name} has joined the game!\n\n"
                f"{len(players)}/{requiredplayers} players joined."
            )

        await context.bot.send_message(
            chatid,
            playertext,
            parse_mode='Markdown'
        )
    basedict['rtype']='answering'
    return WAITFORANSWER


async def botmsg(msg, chatid, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chatid,
        msg,
        parse_mode="Markdown"
    )


async def waitforanswer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Waits for text
    input from players"""
    chatid = update.effective_chat.id
    basedict = context.bot_data[chatid]
    players = basedict['players']
    if basedict['round'] == 0:
        return
    user = update.effective_user
    username = user.full_name
    currentpuzzle = basedict['currentpuzzle']
    if basedict['rtype'] != 'answering':
        return
    response = update.message.text.strip()
    if user.id not in basedict['players']:
        return
    answers = basedict['answers']
    while '  ' in response:
        response = response.replace('  ', ' ')
    currentnum = 0
    replytext = ""
    if 'nigge' in response:
        msg = (
            f"{user.full_name}, "
            "please be a racist pos elsewhere,"
            "somewhere that doesn't potentially get this channel banned, thanks."
        )
        await botmsg(msg, chatid, context)
    if 'faggo' in response:
        msg = (
            f"{user.full_name}, please be a biggoted pos elsewhere,"
            "somewhere that doesn't potentially get this channel banned, thanks."
        )
        await botmsg(msg, chatid, context)

    for word in response.split():
        if currentnum == len(currentpuzzle):
            continue
        if list(currentpuzzle)[currentnum].lower() == list(word)[0].lower():
            if len(list(word)) == 1:
                if word.lower().strip() in list("iumonryac"):
                    currentnum += 1
                else:
                    msg = (
                        "ERROR: generic answer given in Backronym:"
                        f"do something better for the letter: {word}"
                    )
                    await botmsg(msg, chatid, context)
            else:
                currentnum += 1
        else:
            print("ERROR:Non matching acronym!")
            return

    if currentnum == len(currentpuzzle):
        await update.message.delete()
        if user.full_name in answers:
            msg = (
                f"Sorry *{user.full_name}*, you have already submitted an answer!",
            )
            await botmsg(msg, chatid, context)
            return

        for key in players.keys():
            if players[key]['answer'].lower() == response.lower():
                replytext = (
                    "Great minds think alike!\n"
                    "Unfortunately this answer has already been submitted,"
                    "please submit a different response!'"
                )
                await botmsg(replytext, chatid, context)
                return
        players[user.id]['answer'] = response
        chatanswers = basedict['answers']
        chatanswers += [user.full_name]
        if 'tiebreaker' not in basedict and len(basedict['answers']) == 1:
            await set_timer(chatid, context)
        replytext = f"{username} has submitted their answer!"
        await botmsg(replytext, chatid, context)

    if len(basedict['answers']) == len(basedict['players']):
        basedict['rtype'] = 'voting'
        basedict['answers'].clear()
        if 'tiebreaker' in basedict:
            await set_timer(chatid, context)
        else:
            await remove_jobs(context)
        basedict['rtype'] = 'voting'
        await poll(chatid, context)


async def poll(chatid, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends answers users submitted."""
    questions = []
    for key in context.bot_data[chatid]['players'].keys():
        if len(context.bot_data[chatid]['players'][key]['answer']) == 0:
            continue
        questions += [context.bot_data[chatid]['players'][key]['answer']]
    message = await context.bot.send_poll(
        chatid,
        f"Choose the best answer for the acronym {context.bot_data[chatid]['currentpuzzle']}:",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": chatid,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ POLL ANSWERS
    Receive votes from users
    in the form of poll answers."""
    user = update.effective_user
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    chatid = answered_poll['chat_id']
    basedict = context.bot_data[chatid]
    players = basedict['players']
    if user.id in basedict['players']:
        basedict['pollvoted'] += 1
        if basedict['pollvoted'] == 1:
            if 'tiebreaker' not in basedict:
                await set_timer(chatid, context)
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
    if user.id in players.keys():
        for key in players.keys():
            if answer_string == players[key]['answer']:
                if players[user.id]['answer'] != answer_string:
                    players[key]['score'] += 1
    else:
        for key in players.keys():
            if answer_string == players[key]['answer']:
                best = key
        players[best]['score'] += 1
    if basedict['pollvoted'] >= len(players):
        await remove_jobs(context)
        await parse_votes(chatid, context)


async def parse_votes(chatid, context: ContextTypes.DEFAULT_TYPE) -> bool:
    basedict = context.bot_data[chatid]
    players = basedict['players']
    basedict['pollvoted'] = 0
    polllist = []
    for key in context.bot_data:
        if 'questions' in context.bot_data[key]:
            polly = context.bot_data[key]['message_id']
            if context.bot_data[key]['chat_id'] == chatid:
                await context.bot.stop_poll(chatid, polly)
                polllist.append(key)
    for pollid in polllist:
        del context.bot_data[pollid]
    basedict['rtype'] = 'answering'
    if basedict['round'] < basedict['totalrounds']:
        await make_puzzle(chatid, context)
    if basedict['round'] >= basedict['totalrounds']:
        await findwinner(chatid, context)


async def findwinner(chatid, context: ContextTypes.DEFAULT_TYPE):
    basedict = context.bot_data[chatid]

    players = basedict['players']
    for pkey in basedict['players'].keys():
        if pkey in context.bot_data:
            context.bot_data[pkey]['rep'] += basedict['players'][pkey]['score']
        else:
            context.bot_data[pkey] = {'rep': basedict['players'][pkey]['score']}
    highestscore = 0
    highestplayers = {'id': 0, 'name': ""}
    if 'tiebreaker' in basedict:
        del basedict['tiebreaker']
        await announce_winners(True, chatid, context)
        return ConversationHandler.END
    else:
        for key in basedict['players'].keys():
            if int(players[key]['score']) > highestscore:
                highestplayers.clear()
                highestplayers.update({key: players[key]['name']})
                highestscore = int(players[key]['score'])
            elif int(players[key]['score']) == highestscore:
                highestplayers.update({key: players[key]['name']})
        if len(highestplayers.keys()) > 1:
            await tiebreaker(highestplayers, chatid, context)
        else:
            await announce_winners(False, chatid, context)


async def announce_winners(Skip: False, chatid, context: ContextTypes.DEFAULT_TYPE):
    basedict = context.bot_data[chatid]
    players = basedict['players']
    totalscores = ''
    for player in players.keys():
        totalscores += (
            f"{players[player]['name']} - {players[player]['score']} "
            f"({context.bot_data[player]['rep']})\n"
        )
    if 'tiebreaker' in basedict:
        messagetext = 'SUDDEN DEATH '
        del basedict['tiebreaker']
    else:
        messagetext = ''
    messagetext += (
        f"TOTALS\n{totalscores}\n\n\n"
        "Start new game:\n`/join`\n\n"
        "Change # of players:\n`/players` #\n\n"
        "Change # of rounds:\n`/rounds` #\n\n"
        "Change time limit (# of seconds):\n"
        "/`settime` #"
    )
    if 'tiebreaker' in basedict:
        basedict['totalrounds'] = basedict['storedtotalrounds']
        del basedict['tiebreaker']
    await botmsg(messagetext, chatid, context)
    return ConversationHandler.END

async def set_timer(chatid, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = chatid
    try:
        # args[0] should contain the time for the timer in seconds
        timelimit = 45
        if chat_id in context.bot_data:
            if 'timelimit' not in context.bot_data[chat_id]:
                context.bot_data[chat_id]['timelimit'] = 45
            else:
                timelimit = context.bot_data[chat_id]['timelimit']
        await remove_jobs(context)
        due = float(timelimit)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)
    except (EnvironmentError, ValueError):
        print("Couldn't set timer.")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    chatid = job.chat_id
    basedict = context.bot_data[chatid]
    players = basedict['players']
    if 'tiebreaker' in basedict:
        await set_timer(chatid, context)
    anscount = 0
    storeduser = 0
    if basedict['rtype'] == 'voting':
        if 'pollvoted' in basedict:
            if basedict['pollvoted'] > 1:
                polllist = []
                for key in context.bot_data:
                    if 'questions' in context.bot_data[key]:
                        polly = context.bot_data[key]['message_id']
                        if context.bot_data[key]['chat_id'] == chatid:
                            await context.bot.stop_poll(chatid, polly)
                            polllist.append(key)
                for pollid in polllist:
                    del context.bot_data[pollid]
        await parse_votes(chatid, context)
    else:
        basedict['answers'].clear()
        for key in players.keys():
            if len(players[key]['answer']) > 0:
                anscount += 1
                storeduser = key
        if anscount > 1:
            basedict['rtype'] = 'voting'
            await poll(chatid, context)
            return
        else:
            if anscount == 1:
                players[storeduser]['score'] += 1
                msg = (
                    "Only one player submitted an answer,"
                    " automatically giving them the round!"
                    "\n\nHere's what their answer was:"
                    f"\n{players[storeduser]['answer']}"
                )
                await botmsg(msg, chatid, context)
        if basedict['round'] >= basedict['totalrounds']:
            await findwinner(chatid, context)
        else:
            await make_puzzle(chatid, context)


async def tiebreaker(tiebreakcontestants, chatid, context: ContextTypes.DEFAULT_TYPE):
    basedict = context.bot_data[chatid]
    basedict['timelimit'] = 15
    marked = []
    players = basedict['players']
    for key in players.keys():
        if 'key' not in tiebreakcontestants:
            marked.append(key)
    for value in basedict['marked']:
        del basedict['players'][value]
    suddendeathpeople = []
    for key in basedict['players'].keys():
        suddendeathpeople.append(basedict['players'][key]['name'])
    await context.bot.send_message(
        chatid,
        (
            "THESE PLAYERS HAVE TIED FOR THE WIN:\n"
            f"{', '.join(list(suddendeathpeople))}\n\n\n"
            "\nSUDDEN MF'N DEATH!\n\n"
            "Sudden death will begin in 10 SECONDS.\n\nSudden death consists of"
            " 3 rapid fire rounds lasting 15 seconds each!"
        )
    )
    time.sleep(10)
    basedict['storedtotalrounds'] = basedict['totalrounds']
    basedict['round'] = 0
    basedict['totalrounds'] = 3
    basedict['tiebreaker'] = True
    await make_puzzle(chatid, context)
    await remove_jobs(context)
    await set_timer(chatid, context)


async def remove_jobs(context: ContextTypes.DEFAULT_TYPE):
    for job in context.job_queue.jobs():
        job.schedule_removal()


async def unset(chatid, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    remove_jobs(context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    chatid = update.effective_chat.id
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    context.bot_data[chatid] = {}
    return ConversationHandler.END


async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    chatid = update.effective_chat.id
    if chatid in context.bot_data.keys():
        basedict = context.bot_data[chatid]
    else:
        context.bot_data[chatid] = {}
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Reset all settings and restarting bot! Use /join to start over."
    )
    basedict['round'] = 0
    basedict['answers'] = []
    basedict['pollvoted'] = 0
    basedict['rtype'] = ''
    if 'tiebreaker' in basedict:
        del basedict['tiebreaker']
    if 'storedtotalrounds' in basedict:
        basedict['totalrounds'] = basedict['storedtotalrounds']
    if 'players' in basedict:
        basedict['players'].clear()
    basedict['round'] = 0
    if 'tiebreakcontestants' in basedict:
        basedict['tiebreakcontestants'].clear()
    return


async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """On receiving polls,
    reply to it by a closed poll
    copying the received poll"""
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
    persistence = PicklePersistence(filepath="backronymsnbot")
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(TOKEN)
        .concurrent_updates(False)
        .arbitrary_callback_data(True)
        .persistence(persistence=persistence)
        .build()

    )

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("join", join),
            CommandHandler("reboot", reboot),
            CommandHandler("players", players),
            CommandHandler("rounds", rounds),
            CommandHandler("timelimit", timelimit),
            CommandHandler("nfo", nfo),
            CommandHandler("rep", rep)
            ],
        states={
            WAITFORANSWER: [MessageHandler(filters.TEXT, waitforanswer)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_user=False,
        per_chat=True,
        per_message=False,

    )
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
