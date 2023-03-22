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
import logging
import string
import random

from telegram import __version__ as TG_VER
import time, threading



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


skipvote = 0
rounds_length_in_seconds = 30

def timer():
    print(time.ctime())
    threading.Timer(rounds_length_in_seconds, timer).start()
    

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN = "5898007528:AAE6bcp1ueln3fNtEp94cwXM5RPRJ6JbMkE"
WAITFORANSWER, FINISH, CONT = range(3)




async def cont(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_chat.id
    context.bot_data[update.effective_chat.id]['roundtype']='voting'
    
    
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_chat.id
    replytext=""
    await update.message.reply_text(
            replytext
        )
    

    
async def setplayers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_chat.id
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
    user = update.effective_chat.id
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
    
    
async def boo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in context.bot_data:
        return
    if 'forshame' in context.bot_data[update.effective_chat.id]:
        if context.bot_data[update.effective_chat.id]['forshame'] != 0:
            shameID=context.bot_data[update.effective_chat.id]['forshame']
            await update.message.reply_text(
                "Masturbatory point removed!"
            )
            context.bot_data[update.effective_chat.id]['forshame']=0
            context.bot_data[update.effective_chat.id]['players'][shameID]['score']-=1
    
    
    
def random_char(y) -> str:
    unwanted_chars = "xzqk"
    chars=''
    for x in range(y):
        chars+=random.choice([s for s in string.ascii_lowercase if s not in unwanted_chars and s not in chars])
    chars=chars.upper()
    return chars



async def lwf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""

    user=update.effective_user
    if update.effective_chat.id not in context.bot_data:
        context.bot_data[update.effective_chat.id]={}
        
    if 'totalrounds' not in context.bot_data[update.effective_chat.id]:
        context.bot_data[update.effective_chat.id]['totalrounds']=3
        
    if 'required' not in context.bot_data[update.effective_chat.id]:
        context.bot_data[update.effective_chat.id]['required']=3
    
    if 'players' in context.bot_data[update.effective_chat.id]:
        if len(context.bot_data[update.effective_chat.id]['players']) == context.bot_data[update.effective_chat.id]['required']:
            await update.message.reply_text(
                "Sorry, the current round is full, each round only lasts a few mintues so be ready to join the next one!\nDon't forget to /setplayers NUMBER to increase the maxium players!", reply_markup=ReplyKeyboardRemove()
            )
        if user.id in context.bot_data[update.effective_chat.id]['players']:
            if context.bot_data[update.effective_chat.id]['players'][user.id]['round']>context.bot_data[update.effective_chat.id]['round']:
                return
        else:
             context.bot_data[update.effective_chat.id]['players'][user.id]={'name': user.full_name, 'score': 0, 'round': 0, 'answer': ''}
    else:
        context.bot_data[update.effective_chat.id]['players']={user.id: {'chat': update.effective_chat.id, 'name': user.full_name, 'score': 0, 'round': 0, 'answer': '', 'id': user.id}}
        context.bot_data[update.effective_chat.id]['round']=0
    
    if len(context.bot_data[update.effective_chat.id]['players']) == context.bot_data[update.effective_chat.id]['required']:
        text=f"{user.full_name} has joined!\n\n{len(context.bot_data[update.effective_chat.id]['players'])}/{context.bot_data[update.effective_chat.id]['required']} players joined.\nStarting game!."
        await update.message.reply_text(
            text, parse_mode= 'Markdown'
        )
        time.sleep(3)
        replytext=""
        context.bot_data[update.effective_chat.id]['currentpuzzle']=random_char(3)
        formattedpuzzle=context.bot_data[update.effective_chat.id]['currentpuzzle'].replace("", "     ")[1: -1]
        replytext=f"Make a Brackonym for:\n\n============\n*{formattedpuzzle}*\n============"
        
        await update.message.reply_text(
            replytext, parse_mode= 'Markdown'
        )
        context.bot_data[update.effective_chat.id]['roundtype']='waiting'
        context.bot_data[update.effective_chat.id]['players'][user.id]['round']=1
        context.bot_data[update.effective_chat.id]['round']=1
        context.bot_data[update.effective_chat.id]['first']=True
        return WAITFORANSWER
    else: 

        if len(context.bot_data[update.effective_chat.id]['players'])==1:
            playertext=f"Acronyms - a set of letters that represent specific words.\n*Backronyms - a set of words that represent specific letters.*\n\n*Example:*\n====================================\n                *-=* `T  F  L  M  T  P `*=-*\n(*T*)he (*F*)irst (*L *)etters (*M*)atch (*T*)he (*P*)rompt\n====================================\nPrompt: TFLMTP\nAcceptable answer: The First Letters Match The Prompt\n\nNotes:\n-Audience member votes are equal to player votes!\n-Each round has a 60 second timer that starts as soon as the first move of the round is made.\n-Sentences that makes sense > low effort answers.\n-Change total players with /setplayers\n-Change total rounds with /setrounds\n\n{len(context.bot_data[update.effective_chat.id]['players'])}/{context.bot_data[update.effective_chat.id]['required']} | Rounds: {context.bot_data[update.effective_chat.id]['toralrounds']}\n\nStarted by:\n{user.full_name}"
        else: 
            playertext=f"{user.full_name} has joined the game!\n\n{len(context.bot_data[update.effective_chat.id]['players'])}/{context.bot_data[update.effective_chat.id]['required']} players joined."
        await update.message.reply_text(
            playertext, parse_mode= 'Markdown'
        )
        context.bot_data[update.effective_chat.id]['players'][user.id]['round']=1



async def waitforanswer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Waits for text 
    input from players"""
    if context.bot_data[update.effective_chat.id]['roundtype']!='waiting':
        return
    user=update.effective_user
    username=user.full_name
    if user.id not in context.bot_data[update.effective_chat.id]['players']:
        await update.message.reply_text(
            f"Sorry {user.full_name}, you're not in the player list, you'll have to wait until next game!"
        )  
        return
    chatid = update.message.chat_id
    response = update.message.text
    response = response.strip()
    while '  ' in response:
        response = response.replace('  ', ' ')
    currentnum=0
    replytext=""
  
    if 'nigger' in response:
        await update.message.reply_text(
                f"{user.full_name}, please be a racist piece of shit elsewhere, somewhere that doesn't potentially get this channel banned, thanks."
            )  
    if 'faggot' in response:
        await update.message.reply_text(
           f"{user.full_name}, please be a biggoted piece of shit elsewhere, somewhere that doesn't potentially get this channel banned, thanks."
        )
            
    for respon in response.split():
        if currentnum == len(context.bot_data[update.effective_chat.id]['currentpuzzle']):
            continue
        if list(context.bot_data[update.effective_chat.id]['currentpuzzle'])[currentnum].lower() == list(respon)[0].lower():
            if len(list(respon)) == 1:
                if respon.lower().strip() in "iuryac":
                    currentnum+=1
                else:
                    print(f"ERROR: generic answer given in Backronym(letter {context.bot_data[update.effective_chat.id]['currentpuzzle']/currentnum} doesn't match)")
            else:
              currentnum+=1
        else:
            print("ERROR:Non matching acronym!")
            return
    
    if currentnum == len(context.bot_data[update.effective_chat.id]['currentpuzzle']):
        await update.message.delete()
        if 'answers' in context.bot_data[update.effective_chat.id]:
            if user.full_name in context.bot_data[update.effective_chat.id]['answers']:
                await update.message.reply_text(
                    f"Sorry {user.full_name}, you have already submitted an answer!"
                )  
                return

        for key in context.bot_data[update.effective_chat.id]['players']:
            if context.bot_data[update.effective_chat.id]['players'][key]['answer'].lower() == response.lower():
                replytext='Great minds think alike!\nUnfortunately this answer has already been submitted, please submit a different response!'
                await context.bot.send_message(
                    chatid,
                    replytext
                )
                return
        context.bot_data[update.effective_chat.id]['players'][user.id]['answer'] = response
        if 'answers' in context.bot_data[update.effective_chat.id]:
            context.bot_data[update.effective_chat.id]['answers'] += [user.full_name]
        else:
            context.bot_data[update.effective_chat.id]['answers'] = [user.full_name]
        await context.bot.send_message(
                chatid,
                f"{username} has submitted their answer!"
            )
        if context.bot_data[update.effective_chat.id]['first']==True:
            context.bot_data[update.effective_chat.id]['first']=False
            await set_timer(update.effective_chat.id, context) 
        context.bot_data[update.effective_chat.id]['players'][user.id]['round']+=1
          
    if len(context.bot_data[update.effective_chat.id]['answers'])==len(context.bot_data[update.effective_chat.id]['players']):
        context.bot_data[update.effective_chat.id]['first']=True
        context.bot_data[update.effective_chat.id]['roundtype']='voting'
        remove_job_if_exists(update.effective_chat.id, context)
        context.bot_data[update.effective_chat.id]['answers'].clear()
        await poll(update.effective_chat.id, context)
        return
    return



async def poll(chatid, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends answers users submitted."""
    
    questions=[]
    for key in context.bot_data[chatid]['players']:
        if len(context.bot_data[chatid]['players'][key]['answer'].strip()) == 0:
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
    user = update.effective_user
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
  
    context.bot_data[answered_poll['chat_id']]['poll']=answered_poll
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
    for key in context.bot_data[answered_poll['chat_id']]['players']:
        if answer_string == context.bot_data[answered_poll['chat_id']]['players'][key]['answer']:
            if context.bot_data[answered_poll['chat_id']]['players'][user.id]['answer'] == answer_string:
                context.bot_data[answered_poll['chat_id']]['players'][key]['score'] += 1
    if user.id in context.bot_data[answered_poll['chat_id']]['players']:
        context.bot_data[answered_poll['chat_id']]['players'][user.id]['round'] += 1
        answered_poll["answers"] += 1
    if answered_poll["answers"]==1:
        if context.bot_data[answered_poll["chat_id"]]['first']==True:
            context.bot_data[answered_poll["chat_id"]]['first']=False
            await set_timer(answered_poll['chat_id'], context)
    # Close poll after three participants voted
    answered_poll["answers"] == 0
    if answered_poll["answers"] == len(context.bot_data[answered_poll['chat_id']]['players']):
        context.bot_data[answered_poll["chat_id"]]['first']=True
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
        context.bot_data[answered_poll['chat_id']]['roundtype']='waiting'
        if context.bot_data[answered_poll['chat_id']]['round'] <   context.bot_data[answered_poll['chat_id']]['totalrounds']:
            newpuzzle=random_char(context.bot_data[answered_poll['chat_id']]['round']+3)
            context.bot_data[answered_poll['chat_id']]['currentpuzzle']=newpuzzle
            betterspace=newpuzzle.replace("", "    ")[1: -1]
            await context.bot.send_message(
                answered_poll["chat_id"],
                f"NEXT ROUND!!!:\n\n=============\n*{betterspace}*\n=============", parse_mode= 'Markdown'
            )
            
            context.bot_data[answered_poll['chat_id']]['round'] += 1
            await set_timer(answered_poll['chat_id'], context)
            for key in context.bot_data[answered_poll['chat_id']]['players'].keys():
                context.bot_data[answered_poll['chat_id']]['players'][key]['answer']=''
            return WAITFORANSWER
        highest = 0
        MessageText=''
        winrar = ''
        tiemembers=''
        tie=0
        for key in context.bot_data[answered_poll['chat_id']]['players']:
            if int(context.bot_data[answered_poll['chat_id']]['players'][key]['score']) > highest:
                highest = int(context.bot_data[answered_poll['chat_id']]['players'][key]['score'])
                winrar = context.bot_data[answered_poll['chat_id']]['players'][key]['name']
                tiemembers = winrar
            elif highest == int(context.bot_data[answered_poll['chat_id']]['players'][key]['score']):
                tie=1
                tiemembers += f"\n{context.bot_data[answered_poll['chat_id']]['players'][key]['name']}"
            if tie==1:
                pretext = f"TIE GAME WINNERS:\n{tiemembers}\n\n"
            else:
                pretext=f"WINNER:\n{winrar}\n\n"
        for key in context.bot_data[answered_poll['chat_id']]['players']: 
            MessageText += f"\n{context.bot_data[answered_poll['chat_id']]['players'][key]['name']} - {context.bot_data[answered_poll['chat_id']]['players'][key]['score']}"
        await context.bot.send_message(
            answered_poll["chat_id"],
            f"{pretext}TOTALS:{MessageText}\n\nSend /lwf to start another round.\nHINT: If you want to change the maximum player setting type:\n/setplayers NUMBER"
        )
        context.bot_data[answered_poll['chat_id']] = {}
        remove_job_if_exists(answered_poll['chat_id'], context)
        return ConversationHandler.END
    return



async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ADD FINISH SHIT
    context.bot_data[update.effective_chat].Clear()
    update.effective_message(
        "Game finished! Enter /lwf again to start a new one!\n\nHint: Want to change max players?\nSend \"/setplayers x\" with x being the number of players, without the quotes, before joining the next round!"
    )
    return



async def set_timer(chatID, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = chatID
    try:
        # args[0] should contain the time for the timer in seconds
 
        remove_job_if_exists(str(chat_id), context)
        due = float(60.0)
        context.job_queue.run_once(timelimit, due, chat_id=chat_id, name=str(chat_id), data=due)
    except (IndexError, ValueError):
        print("Couldn't set timer.")



async def timelimit(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    
    job = context.job
    totalrounds=context.bot_data[job.chat_id]['totalrounds']
    if context.bot_data[job.chat_id]['roundtype']=='waiting':     
        context.bot_data[job.chat_id]['roundtype']='voting'
        context.bot_data[job.chat_id]['first']=True
        anscount=0
        storeduser=0
        for key in context.bot_data[job.chat_id]['players'].keys():
            if len(context.bot_data[job.chat_id]['players'][key]['answer'].strip())!=0:
                anscount+=1
                storeduser=key
        if anscount>1:
            await poll(job.chat_id, context)
        elif anscount==1:
            context.bot_data[job.chat_id]['players'][storeduser]['score']+=1
            Update.message.chat_id("Only one player submitted an answer, automatically giving them the round!")
        elif anscount==0:
            print("the fuck dude")
        context.bot_data[job.chat_id]['answers'].clear()
        return 
    if context.bot_data[job.chat_id]['roundtype']=='voting':
        context.bot_data[job.chat_id]['first']=True
        answered_poll=context.bot_data[job.chat_id]['poll']
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
        for key in context.bot_data[answered_poll['chat_id']]['players'].keys():
            context.bot_data[answered_poll['chat_id']]['players'][key]['answer']=''
        if context.bot_data[answered_poll['chat_id']]['round'] < 3:
            newpuzzle=random_char(context.bot_data[answered_poll['chat_id']]['round']+3)
            context.bot_data[job.chat_id]['currentpuzzle']=newpuzzle
            betterspace=newpuzzle.replace("", "   ")[1: -1]
            await context.bot.send_message(
                answered_poll["chat_id"],
                f"MAKE AN ACRONYM FOR:\n\n=================\n{betterspace}\n=================", parse_mode= 'Markdown'
            )
            context.bot_data[answered_poll['chat_id']]['round'] += 1
            context.bot_data[job.chat_id]['roundtype']='waiting'
            return WAITFORANSWER
        highest = 0
        MessageText=''
        winrar = ''
        tiemembers=''
        tie=0
        for key in context.bot_data[answered_poll['chat_id']]['players']:
            if int(context.bot_data[answered_poll['chat_id']]['players'][key]['score']) > highest:
                highest = int(context.bot_data[answered_poll['chat_id']]['players'][key]['score'])
                winrar = context.bot_data[answered_poll['chat_id']]['players'][key]['name']
                tiemembers = winrar
            elif highest == int(context.bot_data[answered_poll['chat_id']]['players'][key]['score']):
                tie=1
                tiemembers += f"\n{context.bot_data[answered_poll['chat_id']]['players'][key]['name']}"
            if tie==1:
                pretext = f"TIE GAME WINNERS:\n{tiemembers}\n\n"
            else:
                pretext=f"WINNER:\n{winrar}\n\n"
        for key in context.bot_data[answered_poll['chat_id']]['players']: 
            MessageText += f"\n{context.bot_data[answered_poll['chat_id']]['players'][key]['name']} - {context.bot_data[answered_poll['chat_id']]['players'][key]['score']}"
        await context.bot.send_message(
            answered_poll["chat_id"],
            f"{pretext}TOTALS:{MessageText}\n\nSend /lwf to start another round.\nHINT: If you want to change the maximum player setting type:\n/setplayers NUMBER"
        )
        context.bot_data[answered_poll['chat_id']] = {}
        return ConversationHandler.END



def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True



async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    remove_job_if_exists(str(chat_id), context)



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    context.bot_data[update.effective_chat.id]= {}
    return ConversationHandler.END



async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text (
    "Reset all settings aned restarting bot! Use /lwf to start over(after a few conds, obviously!)."
    )
    context.bot_data[update.effective_chat.id]= {}
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
            WAITFORANSWER: [MessageHandler(filters.TEXT, waitforanswer)],
            FINISH: [MessageHandler(filters.TEXT, finish)],
            CONT: [CommandHandler("cont", cont)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_user=False,
        per_chat=True,
        per_message=False
    )
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("boo", boo))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("setplayers", setplayers))
    application.add_handler(CommandHandler("setrounds", setrounds))
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.run_polling()

if __name__ == "__main__":
    main()