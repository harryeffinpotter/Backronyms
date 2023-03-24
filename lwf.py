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
from datetime import datetime
import logging
import random

from telegram import __version__ as TG_VER
import time



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
from examples.timerbot import remove_job_if_exists



# Enable logging
now=datetime.now()
now=now.strftime('%H_%M_%d_%m_%Y.log')
logging.basicConfig(
    encoding='utf-8', level=logging.INFO
    )

TOKEN = "5898007528:AAE6bcp1ueln3fNtEp94cwXM5RPRJ6JbMkE"
WAITFORANSWER, FINISH = range(2)

async def settimelimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=str(update.effective_message.text)
    text=text.replace('/settimelimit', '')
    text=text.strip()
    if update.effective_chat.id not in context.bot_data:
        context.bot_data[update.effective_chat.id]={}
    context.bot_data[update.effective_chat.id]['required']=int(text)
    timelimit = context.bot_data[update.effective_chat.id]['timelimit']
    replytext=f"Time limit changd to {timelimit}"
    await update.message.reply_text(
            replytext
        )
    
async def setplayers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=str(update.effective_message.text)
    text=text.replace('/setplayers', '')
    text=text.strip()
    if update.effective_chat.id not in context.bot_data:
        context.bot_data[update.effective_chat.id]={}
    context.bot_data[update.effective_chat.id]['required']=int(text)
    requiredplayers = context.bot_data[update.effective_chat.id]['required']
    replytext=f"Required players count changed to {requiredplayers}"
    await update.message.reply_text(
            replytext
        )
    
async def setrounds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=str(update.effective_message.text)
    text=text.replace('/setrounds', '')
    text=text.strip()
    if update.effective_chat.id not in context.bot_data:
        context.bot_data[update.effective_chat.id]={}
    context.bot_data[update.effective_chat.id]['totalrounds']=int(text)
    totalrounds = context.bot_data[update.effective_chat.id]['totalrounds']
    replytext=f"Total rounds set to {totalrounds}"
    await update.message.reply_text(
        replytext
    )


def random_char(y) -> str:
    char=''
    letterstouse=(
        "abcdefghijklmnopqrstuvwy"
        "abcdefhilmnoprstw"
        "abcfhimopstw"
        "aciost"
    )
    for x in range(y):
        char+=random.choice([s for s in letterstouse])
    char=char.upper()
    return char



async def lwf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""
    try:
        user=update.effective_user
        chatid=update.effective_chat.id
        if chatid not in context.bot_data:
            context.bot_data[chatid]={}
            basedict=context.bot_data[update.effective_chat.id]
            basedict['first'] = True
            basedict['started'] = 0
        else: 
            basedict=context.bot_data[update.effective_chat.id]
        basedict=context.bot_data[update.effective_chat.id]
        if 'totalrounds' not in basedict:
            totalrounds=3
            basedict['totalrounds']=3
        else:
            totalrounds=basedict['totalrounds']
        if 'round' not in basedict:
            basedict['round']=1  
        currround=context.bot_data[update.effective_chat.id]['round'] 
        if 'required' not in basedict:
            basedict['required']=3
        requiredplayers=basedict["required"]
        if 'players' in basedict:
            players=basedict['players']
            if len(players) == requiredplayers:
                await update.message.reply_text(
                    ("Sorry, the current round is full, each round only lasts a "
                    "few mintues so be ready to join the next one!\n"
                    "Don't forget to /setplayers NUMBER to increase the maximum players!")
                )
            if user.id in players:
                if players[user.id]['round']>currround:
                    return WAITFORANSWER
            else:
                players[user.id]={
                     'name': user.full_name, 
                     'score': 0, 
                     'round': 0, 
                     'answer': ''}
        else:
            basedict['players'] = { 
                user.id:
                    { 
                        'chat': chatid, 
                        'name': user.full_name,
                        'score': 0, 
                        'round': 0, 
                        'answer': '', 
                        'id': user.id
                    }   
                }
            players = basedict['players']
        if len(players) == requiredplayers and basedict['started']== 0:
            basedict['started'] = 1
            basedict['first'] = True
            text=(
                f"{user.full_name} has joined!\n\n"
                f"{len(players)}/{requiredplayers} players joined."
                "\nStarting game!."
            )

            await update.message.reply_text(
                text,
                parse_mode= 'Markdown'
            )

            time.sleep(3)
            replytext=""
            currentpuzzle=random_char(3)
            basedict['currentpuzzle'] = currentpuzzle
            for key in players.keys():
                players[key]['answer']=''
            formattedpuzzle=currentpuzzle.replace("", "     ")[1: -1]
            replytext=f"MAKE A BACKRONYM FOR:\n\n============\n*{formattedpuzzle}*\n============"

            await update.message.reply_text(
                replytext, 
                parse_mode= 'Markdown'
            )
            basedict['roundtype']='waiting'
            basedict['round']=1
            players[user.id]['round']+=1
            return WAITFORANSWER
        else: 
            if len(context.bot_data[update.effective_chat.id]['players'])==1:
                basedict['started']=0
                playertext=("Acronyms - a `set of letters that represent specific words.`\n"
                            "*BACKRONYMS* - `a set of words that represent specific letters.`\n\n"
                            "*Example:*\n===================================="
                            "\n                *-=* `T  F  L  M  T  P `*=-*\n"
                            "(*T*)he (*F*)irst (*L *)etters (*M*)atch (*T*)he (*P*)rompt\n"
                            "====================================\nPrompt: TFLMTP\n"
                            "Acceptable answer: The First Letters Match The Prompt\n\n"
                            "Notes:\n-Audience member votes are equal to player votes!\n"
                            "-Each round has a 60 sec timer after 1st move of the round is made.\n"
                            "-Sentences that makes sense > low effort answers.\n"
                            "-Change total players with /setplayers\n"
                            "-Change total rounds with /setrounds\n\n"
                            f"{len(players)}/{requiredplayers} | Rounds: {totalrounds}\n\n"
                            f"Started by:\n{user.full_name}"
                )
            else: 
                playertext=(
                    f"{user.full_name} has joined the game!\n\n"
                    f"{len(players)}/{requiredplayers} players joined."
                )

            await context.bot.send_message(
                chatid,
                playertext, 
                parse_mode= 'Markdown'
            )
            basedict['first'] = False
            players[user.id]['round'] += 1
            return WAITFORANSWER
    except Exception as e:
        logging.log(0, str(e.message))

async def waitforanswer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Waits for text 
    input from players"""
    try:
        basedict=context.bot_data[update.effective_chat.id]
        if update.effective_chat.id in context.bot_data:
            if 'roundtype' in basedict:
                if basedict['roundtype']!='waiting':
                    return WAITFORANSWER
        user=update.effective_user
        username=user.full_name

        chatid = update.message.chat_id
        response = update.message.text
        response = response.strip()
        players = basedict['players']
        if 'answers' not in basedict:
            basedict['answers']=[]
        answers = basedict['answers']
        if 'currentpuzzle' in basedict:
            currentpuzzle=basedict['currentpuzzle']
        while '  ' in response:
            response = response.replace('  ', ' ')
        currentnum=0
        replytext=""
    
        if 'nigge' in response:
            await update.message.reply_text(
                    (f"{user.full_name}, "
                    "please be a racist piece of shit elsewhere," 
                    "somewhere that doesn't potentially get this channel banned, thanks."
                    )    
                )  
        if 'faggo' in response:
            await update(
               (f"{user.full_name}, please be a biggoted pos elsewhere,"
               "somewhere that doesn't potentially get this channel banned, thanks.")
            )

        for respon in response.split():
            if currentnum == len(currentpuzzle):
                continue
            if list(currentpuzzle)[currentnum].lower() == list(respon)[0].lower():
                if len(list(respon)) == 1:
                    if respon.lower().strip() in "iuryac":
                        currentnum+=1
                    else:
                        await context.bot.send_message(
                        chatid,
                        ("ERROR: generic answer given in Backronym:" 
                         f"do something better for the letter: {respon}")
                        )
                else:
                  currentnum+=1
            else:
                print("ERROR:Non matching acronym!")
                return

        if currentnum == len(currentpuzzle):
            await update.message.delete()
            if user.full_name in answers:
                await update.message.reply_text(
                        chatid,
                        f"Sorry {user.full_name}, you have already submitted an answer!",
                        parse_mode="Markdown"
                )  
                return

            for key in players.keys():
                if players[key]['answer'].lower() == response.lower():
                    replytext=(
                        "Great minds think alike!\n"
                        "Unfortunately this answer has already been submitted,"
                        "please submit a different response!'"
                        )
                    await context.bot.send_message(
                        chatid,
                        replytext
                    )
                    return WAITFORANSWER
            players[user.id]['answer'] = response
            chatanswers=basedict['answers']
            if 'answers' in basedict:
                chatanswers += [user.full_name]
            else:
                chatanswers = [user.full_name]
            await context.bot.send_message(
                    chatid,
                    f"{username} has submitted their answer!"
                )

            basedict['players'][user.id]['round']+=1

        if len(basedict['answers'])==len(basedict['players']):
            basedict['roundtype']='voting'
            remove_jobs(context)
            basedict['answers'].clear()
            if 'tiebreaker' in basedict:
                    await set_timer(chatid, context)
            await poll(chatid, context)
            return
        else:
            if basedict['first'] is True and 'tiebreaker' not in basedict.keys():
                basedict['first']=False
                await set_timer(chatid, context) 
        return
    except Exception as e:
        logging.log(0, str(e.message))
        



async def poll(chatid, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends answers users submitted."""
    
    questions=[]
    for key in context.bot_data[chatid]['players'].keys():
        if len(context.bot_data[chatid]['players'][key]['answer']) == 0:
            continue
        questions+=[context.bot_data[chatid]['players'][key]['answer']]
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
    try:
        user = update.effective_user
        answer = update.poll_answer
        answered_poll = context.bot_data[answer.poll_id]
        chatid=answered_poll['chat_id']
        context.bot_data[chatid]['poll']=answered_poll
        basedict=context.bot_data[chatid]
        if user.id in basedict['players']:
            if 'pollvoted' not in basedict:
                basedict['pollvoted']=1
            else:
                basedict['pollvoted']+=1
            players=basedict['players']
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
        for key in players:
            if answer_string == players[key]['answer']:
                if players[user.id]['answer'] != answer_string:
                    players[key]['score'] += 1
        if user.id in players:
            players[user.id]['round'] += 1
        if basedict['pollvoted']==1:
            if 'tiebreaker' not in basedict:
                basedict['first']=False
                await set_timer(chatid, context)
        # Close poll after three participants voted
        if basedict['pollvoted'] >= len(players):
            basedict['answers'].clear()
            basedict['pollvoted']=0
            remove_jobs(context)
            basedict['first']=True
            await context.bot.stop_poll(chatid, answered_poll["message_id"])
            basedict['roundtype']='waiting'
            if basedict['round'] < basedict['totalrounds']:
                if basedict['round'] > 99:
                    number=basedict['round']-100
                else:
                    number=basedict['round']
                newpuzzle=random_char(number+3)
                for key in players.keys():
                    players[key]['answer']=''
                basedict['currentpuzzle']=newpuzzle
                betterspace=newpuzzle.replace("", "   ")[1: -1]
                await context.bot.send_message(
                    chatid,
                    (f"MAKE A BACKRONYM FOR:\n\n=================\n{betterspace}\n"
                     "================="),
                    parse_mode = 'Markdown'
                ) 
                basedict['round'] += 1
                basedict['roundtype'] = 'waiting'
                if 'tiebreaker' in basedict:
                    if basedict['tiebreaker'] is True:
                        await set_timer(chatid, context)
                return WAITFORANSWER
            highest = 0
            MessageText=''
            winrar = ''
            tiemembers=''
            tie=0
            pretext=""
            suddendeathtotal = "SUDDEN DEATH TOTALS. THESE SCORES ARE FINAL!\n\n"
            if 'tiebreaker' in basedict:
                if basedict['tiebreaker'] is True:
                    for player in basedict['players'].keys():
                        suddendeathtotal+=(f"\n{players[player]['name']}"
                                           f"- {players[player]['score']}")
                    suddendeathtotal=(
                        f"{suddendeathtotal}\n\n\n"
                        "/lwf - play again!\n"
                        "/setplayers - change required number of players.\n"
                        "/setrounds - change number of rounds.\n"
                        "/settimelimit - change round time limit (default: 60 seconds)")
                    await context.bot.send_message(
                        chatid,
                        suddendeathtotal
                    )
                    players.clear()
                    basedict['round']=0
                    basedict['tiebreakcontestants'].clear()
                    if 'storedtotal' in basedict:
                        basedict['totalrounds']=basedict['storedtotal']
                        del basedict['storedtotal']
                    basedict['answers']=[]
                    basedict['first']=True
                    basedict['started']=0 
                    del basedict['tiebreaker']
                    remove_jobs(context)
                    return
            if basedict['round']==basedict['totalrounds']:
                for key in basedict['players'].keys():
                    if int(players[key]['score']) > highest:
                        highest = int(players[key]['score'])
                        winrar = players[key]['name']
                        tiemembers = winrar
                        basedict['tiebreakcontestants']=[key]
                    elif highest !=0:
                        tie=1
                        tiemembers += f"\n{players[key]['name']}"
                        basedict['tiebreakcontestants'].append(key)
                if tie==1:
                    basedict['tiebreaker']=True
                    basedict['answers'].clear()
                    await unset(str(chatid), context)
                    await tiebreaker(chatid, context)
                    return ConversationHandler.END

            pretext=f"WINNER:\n{winrar}\n\n"
            for key in players: 
                MessageText += f"\n{players[key]['name']} - {players[key]['score']}"
            await context.bot.send_message(
                 chatid,
                (f"{pretext}TOTALS:{MessageText}\n\n"
                    "/lwf - play again!\n"
                    "/setplayers - change required number of players.\n"
                    "/setrounds - change number of rounds.\n"
                    "/settimelimit - change round time limit (default: 45 seconds)")
                )
            if 'tiebreaker' not in basedict:
                players.clear()
            basedict['round']=0
            basedict['answers']=[]
            basedict['first']=True
            basedict['started']=0
    except Exception as e:
        logging.log(0, str(e.message))

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ADD FINISH SHIT
    update.effective_message(
        update.effective_chat,
        ("Game finished! Enter /lwf again to start a new one!\n\n"
         "Hint: Want to change max players?\nSend \"/setplayers x\""
         "with x being the number of players, without the quotes, before joining the next round!"
        )
    )
    return


async def set_timer(chatID, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = chatID
    try:
        # args[0] should contain the time for the timer in seconds
        timelimit=45
        if chat_id in context.bot_data:
            if 'timelimit' not in context.bot_data[chat_id]:
                context.bot_data[chat_id]['timelimit']=45
            else:
                timelimit=context.bot_data[chat_id]['timelimit']
        remove_jobs(context)
        due = float(timelimit)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)
    except (EnvironmentError, ValueError):
        print("Couldn't set timer.")



async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""   
    try:
        job = context.job
        chatid=job.chat_id
        basedict=context.bot_data[chatid]
        basedict['pollvoted']=0
        totalrounds = basedict['totalrounds'] 
        currround = basedict['round']
        roundtype = basedict['roundtype']
        players=basedict['players']
        playerkeys=basedict['players'].keys()
        answers = basedict['answers']
        basedict['first']=True
        basedict['started']=True
        thefuck=False
        if totalrounds<currround:
            roundtype='voting'
        if roundtype=='waiting' and totalrounds+1 > currround:
            roundtype='voting'
            anscount=0
            storeduser=0

            for key in playerkeys:
                if len(players[key]['answer'])>0:
                    anscount+=1
                    storeduser=key
            if anscount>1:
                await poll(chatid, context)
            else:
                if anscount==1:
                    players[storeduser]['score']+=1
                    await context.bot.send_message(
                    chatid,
                    "Only one player submitted an answer, automatically giving them the round!"
                    )
                    thefuck=True
                roundtype="voting"
        if roundtype=='voting':
            if totalrounds != basedict['round']:
                if not thefuck:
                    for key in context.bot_data:
                        if 'questions' in context.bot_data[key]:
                            polly = context.bot_data[key]['message_id']
                            if context.bot_data[key]['chat_id']==chatid:
                                await context.bot.stop_poll(chatid, polly)
                                thefuck=False
                                return
                else:
                    thefuck=False
                for users in playerkeys:
                    players[users]['round']+=1
                if currround > 99:
                    number = currround-100
                else:
                    number = currround
                basedict['round']+=1  
                
                if 'tiebreaker' in basedict: 
                    await set_timer(chatid, context)
                for key in playerkeys:
                    players[key]['answer']=''
                newpuzzle=random_char(number+3)
                basedict['currentpuzzle']=newpuzzle
                betterspace=newpuzzle.replace("", "   ")[1: -1]
                await context.bot.send_message(
                    chatid,
                    (f"MAKE A BACKRONYM FOR:\n\n=================\n{betterspace}"
                     "\n================="),
                    parse_mode= 'Markdown'
                )  
                basedict['roundtype']='waiting'
                answers.clear()
                return WAITFORANSWER
            highest = 0
            MessageText=''
            winrar = ''
            tiemembers=''
            tie=0
            suddendeathtotal="SUDDEN DEATH TOTALS. THESE SCORES ARE FINAL!\n"
            if 'tiebreaker' in context.bot_data[chatid]:
                if basedict['tiebreaker'] is True:
                    for player in playerkeys:
                        suddendeathtotal+=(f"\n{players[player]['name']}"
                        f"- {players[player]['score']}")
                    suddendeathtotal=(
                        f"{suddendeathtotal}\n\n\n/lwf - play again!\n"
                        "/setplayers - change required number of players.\n"
                        "/setrounds - change number of rounds.\n"
                        "/settimelimit - change round time limit (default: 60 seconds)")
                    await context.bot.send_message(
                        chatid,
                        suddendeathtotal
                    )
                    players.clear()
                    basedict['round']=0
                    basedict['tiebreakcontestants'].clear()
                    if 'storedtotal' in basedict:
                        basedict['totalrounds']=basedict['storedtotal']
                        del basedict['storedtotal']
                    basedict['answers']=[]
                    basedict['first']=True
                    basedict['started']=0 
                    remove_jobs(context)
                    del basedict['tiebreaker']
                    return ConversationHandler.END
            if currround==totalrounds:
                basedict['answers'].clear()
                for key in playerkeys:
                    if int(players[key]['score']) > highest:
                        highest = int(players[key]['score'])
                        winrar = players[key]['name']
                        tiemembers = winrar
                        basedict['tiebreakcontestants']=[key]
                    elif highest !=0 and highest == int(players[key]['score']):
                        tie=1
                        tiemembers += f"\n{players[key]['name']}"
                        basedict['tiebreakcontestants'].append(key)
                    if tie==1:
                        basedict['tiebreaker']=True
                        basedict['answers'].clear()
                        await unset(str(chatid), context)
                        await tiebreaker(chatid, context)
                        return
                else:
                    pretext=f"WINNER:\n{winrar}\n\n"
                for key in players: 
                    MessageText += f"\n{players[key]['name']} - {players[key]['score']}"
                await context.bot.send_message(
                     chatid,
                    (f"{pretext}TOTALS:{MessageText}\n\n"
                        "/lwf - play again!\n"
                        "/setplayers - change required number of players.\n"
                        "/setrounds - change number of rounds.\n"
                        "/settimelimit - change round time limit (default: 45 seconds)")
                    )

                if 'tiebreaker' not in basedict:
                    players.clear()
                basedict['round']=0
                basedict['answers']=[]
                basedict['first']=True
                basedict['started']=0
    except Exception as e:
        logging.log(0, str(e.message))


async def tiebreaker(chatID, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.bot_data[chatID]['timelimit']=20
        players=context.bot_data[chatID]['players']
        for key in players.keys():
            if key not in context.bot_data[chatID]['tiebreakcontestants']:
                context.bot_data[chatID]['marked'].append(key)
            else:
                players[key]['score'] = 0
                players[key]['answer'] = ""
                players[key]['round'] = 101
        for value in context.bot_data[chatID]['marked']:
            del context.bot_data[chatID]['players'][id]
        suddendeathpeople=[]
        for key in context.bot_data[chatID]['players'].keys():
            suddendeathpeople.append[key]
        await context.bot.send_message(
            chatID,
            (
                "THESE PLAYERS HAVE TIED FOR THE WIN:"
                f"{', '.join(list(suddendeathpeople))}\n\n\n"
                "You know what that means...\nSUDDEN MF'N DEATH!\n\n"
                "Sudden death will begin in approx. 30 SECONDS.\n\nSudden death consists of"
                " 3 rapid fire rounds lasting 15 seconds each! Players and audience will only"
                "have 15 seconds to vote as well. The rounds will be 3, 4, then 5 letters and "
                "then it will end.\n\nGood night and good luck!"
            )
        )
        time.sleep(30)
        context.bot_data[chatID]['marked']=[]


        replytext=""
        currentpuzzle=random_char(30)
        context.bot_data[chatID]['currentpuzzle']=currentpuzzle
        for key in players.keys():
            players[key]['answer']=''
        formattedpuzzle=currentpuzzle.replace("", "     ")[1: -1]
        replytext=f"MAKE A BACKRONYM FOR:\n\n============\n*{formattedpuzzle}*\n============"

        await context.bot.send_message(
                chatID, replytext, parse_mode= 'Markdown',
            )
        context.bot_data[chatID]['storedtotal']=context.bot_data[chatID]['totalrounds']
        context.bot_data[chatID]['roundtype']='waiting'
        context.bot_data[chatID]['round']=101
        context.bot_data[chatID]['totalrounds'] = 103
        context.bot_data[chatID]['tiebreaker']=True
        context.bot_data[chatID]['pollvoted']=0
        remove_job_if_exists(chatID,context)
        await set_timer(chatID, context)
        return WAITFORANSWER
    except Exception as e:
        logging.log(0, str(e.message))
    

def remove_jobs(context:ContextTypes.DEFAULT_TYPE):
    for job in context.job_queue.jobs():
        job.schedule_removal()

async def unset(chatID, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    remove_jobs(context)



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    context.bot_data[update.effective_chat.id]= {}
    return ConversationHandler.END



async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    chatid = update.effective_chat.id
    if chatid in context.bot_data.keys():
        basedict=context.bot_data[chatid]
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text (
    "Reset all settings and restarting bot! Use /lwf to start over."
    )
    basedict['round']=0
    basedict['answers']=[]
    basedict['pollvoted']=0
    basedict['first']=None
    basedict['roundtype']=''
    basedict['started']=0
    basedict.clear()
    if 'players' in basedict:
            basedict['players'].clear()
    basedict['round']=0
    if 'tiebreakcontestants' in basedict:
        basedict['tiebreakcontestants'].clear()
    
    return ConversationHandler.END



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
            CommandHandler("lwf", lwf), 
            CommandHandler("reboot", reboot), 
            CommandHandler("setplayers",setplayers),
            CommandHandler("setrounds",setrounds),
            CommandHandler("settimelimit",settimelimit)
            ],
        states={
            WAITFORANSWER: [MessageHandler(filters.TEXT, waitforanswer)],
            FINISH: [MessageHandler(filters.TEXT, finish)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_user=False,
        per_chat=True,
        per_message=False,

    )
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("reboot", reboot))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("setplayers", setplayers))
    application.add_handler(CommandHandler("setrounds", setrounds))
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    
    application.run_polling()

if __name__ == "__main__":
    main()