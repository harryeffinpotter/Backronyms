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
import time
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

currentpuzzle = ''
totalrounds = 3
requiredplayers = 5
skipvote = 0
rounds_length_in_seconds = 30

async def timer():
    threading.Timer(rounds_length_in_seconds, timer).start()
    

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN = "6270603273:AAHLTXrg6ozchgm--iSarxsVzQCewMlwtKM"
WAITFORANSWER, FINISH, CONT = range(3)

async def cont(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global requiredplayers
    global skipvote
    user = update.effective_chat.id
    context.bot_data[update.effective_chat.id]['roundtype']='voting'
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global requiredplayers
    global skipvote
    user = update.effective_chat.id
    await update.message.reply_text(
            replytext
        )
    

    
async def setplayers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global requiredplayers
    user = update.effective_chat.id
    text=str(update.effective_message.text)
    text=text.replace('/setplayers', '')
    text=text.strip()
    requiredplayers=int(text)
    replytext=f"Required players count changed to {requiredplayers}"
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
    global currentpuzzle
    unwanted_chars = "xzqk"
    chars=''
    for x in range(y):
        chars+=random.choice([s for s in string.ascii_lowercase if s not in unwanted_chars and s not in chars])
    currentpuzzle=chars.upper()
    return currentpuzzle

async def lwf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts new round of Letters With Friends."""
    global currentpuzzle 
    global requiredplayers
    user=update.effective_user
    if update.effective_chat.id not in context.bot_data:
        context.bot_data[update.effective_chat.id]={}

   
    if 'players' in context.bot_data[update.effective_chat.id]:
        if len(context.bot_data[update.effective_chat.id]['players']) == requiredplayers:
            await update.message.reply_text(
                "Sorry, the current round is full, each round only lasts a few mintues so be ready to join the next one!\nDon't forget to /setplayers NUMBER to increase the maxium players!", reply_markup=ReplyKeyboardRemove()
            )
        if user.id in context.bot_data[update.effective_chat.id]['players']:
            if context.bot_data['players'][user.id]['round']>context.bot_data[update.effective_chat.id]['round']:
                return WAITFORANSWER
        else:
             context.bot_data[update.effective_chat.id]['players'][user.id]={'name': user.full_name, 'score': 0, 'round': 0, 'answer': ''}
    else:
        context.bot_data[update.effective_chat.id]['players']={user.id: {'chat': update.effective_chat.id, 'name': user.full_name, 'score': 0, 'round': 0, 'answer': ''}}
        context.bot_data[update.effective_chat.id]['round']=0
    
    
    if len(context.bot_data[update.effective_chat.id]['players']) == requiredplayers:
        text=f"BACKRONYMS - Make funny acronyms from random sets of letters!\n\n{len(context.bot_data[update.effective_chat.id]['players'])}/{requiredplayers} players have joined.\nMax players reached...\n\nStarting game!"
        await update.message.reply_text(
            text
        )
        time.sleep(3)
        replytext=""
        currentpuzzle=random_char(3)
        replytext=f"Write an acronym that starts with these the following 3 characters!\n\n{currentpuzzle}"
        await update.message.reply_text(
            replytext, reply_markup=ReplyKeyboardRemove()
        )
        context.bot_data[update.effective_chat.id]['players'][user.id]['round']=1
        context.bot_data[update.effective_chat.id]['round']=1
        return WAITFORANSWER
    else: 
        playertext=f"BACKRONYMS - Make funny acronyms from random sets of letters!\n\n{len(context.bot_data[update.effective_chat.id]['players'])}/{requiredplayers} players have joined\nWaiting for more to join...\n\nPlayers:"
        text=''
        for player in context.bot_data[update.effective_chat.id]['players']:
            playertext += f"\n{context.bot_data[update.effective_chat.id]['players'][player]['name']}"
        await update.message.reply_text(
            playertext
        )
        context.bot_data[update.effective_chat.id]['players'][user.id]['round']=1
        return WAITFORANSWER


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends answers users submitted."""
    global currentpuzzle
    questions=[]
    for key in context.bot_data[update.effective_chat.id]['players']:
        questions+=[context.bot_data[update.effective_chat.id]['players'][key]['answer']]
    message = await context.bot.send_poll(
        update.effective_chat.id,
        f"Choose the best answer for the acronym {currentpuzzle}:",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
        open_period=30,
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
    global totalrounds
    global skipvote
    context.bot_data[update.effective_chat.id]['roundtype']='voting'
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
    for key in context.bot_data[answered_poll['chat_id']]['players']:
        if answer_string == context.bot_data[answered_poll['chat_id']]['players'][key]['answer']:
            context.bot_data[answered_poll['chat_id']]['players'][key]['score'] += 1
    if user.id in context.bot_data[answered_poll['chat_id']]['players']:
        context.bot_data[answered_poll['chat_id']]['players'][user.id]['round'] += 1
        answered_poll["answers"] += 1
    if context.bot_data[answered_poll['chat_id']]['players'][user.id]['answer'] == answer_string:
        await context.bot.send_message(
            answered_poll["chat_id"],
            f"{context.bot_data[answered_poll['chat_id']]['players'][user.id]['name']} just voted for themeselves!\n\nDue to TG limitations we cannot remove votes from polls, so we leave this decision to your competion!\n\nsend /boo before at any time until another person votes for themselves to remove the point!\n\nNOTE: For example of when to NOT send /boo would be if you simply answered gibberish and their answer made sense as a sentence while yours did not whatsoever, etc."
        )
        context.bot_data[answered_poll['chat_id']]['forshame']=user.id

         
   
    # Close poll after three participants voted
    if answered_poll["answers"] == len(context.bot_data[answered_poll['chat_id']]['players']):
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
        if context.bot_data[answered_poll['chat_id']]['round'] < totalrounds:

            await context.bot.send_message(
                answered_poll["chat_id"],
                f"Next round:\n\n{random_char(context.bot_data[answered_poll['chat_id']]['round']+3)}"
            )
            context.bot_data[answered_poll['chat_id']]['round'] += 1
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
    return

async def waitforanswer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Waits for text input from players"""
    global currentpuzzle
    user=update.effective_user
    if 'players' in context.bot_data['update.effectve_chat.id']:
        if user.id not in context.bot_data[update.effective_chat.id]['players']:
            await update.message.reply_text(
                f"Sorry {user.full_name}, you're not in the player list, you'll have to wait until next game!"
            )  
        return
    response = update.message.text
    await update.effective_message.delete()
   

    username=user.full_name
    context.bot_data[update.effective_chat.id]['roundtype']='waiting'
    if context.bot_data[update.effective_chat.id]['round']<context.bot_data[update.effective_chat.id]['players'][user.id]['round']:
        print("oi settle down then m8 yoo too early m8")
        return
    user = update.effective_user
   



    response = response.strip()
    while '  ' in response:
        response = response.replace('  ', ' ')
    currentnum=0
    replytext=""
    chatid = update.effective_chat.id
    if 'nigger' in response:
        await update.message.reply_text(
                f"{user.full_name}, please be a racist piece of shit elsewhere, somewhere that doesn't potentially get this channel banned, thanks."
            )  
    if 'faggot' in response:
        await update.message.reply_text(
           f"{user.full_name}, please be a biggoted piece of shit elsewhere, somewhere that doesn't potentially get this channel banned, thanks."
        )
            
    for respon in response.split():
        if currentnum == len(currentpuzzle):
            continue
        if list(currentpuzzle)[currentnum].lower() == list(respon)[0].lower():
            if len(list(respon)) == 1:
                if respon.lower().strip() in "iuryac":
                    currentnum+=1
                else:
                    print(f"ERROR: generic answer given in Backronym(letter {currentpuzzle[currentnum]} doesn't match)")
            else:
              currentnum+=1
        else:
            print("ERROR:Non matching acronym!")
            return
    
    if currentnum == len(currentpuzzle):
        await update.effective_message.delete()
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
        context.bot_data[update.effective_chat.id]['players'][user.id]['round']+=1
          
    if len(context.bot_data[update.effective_chat.id]['answers'])==len(context.bot_data[update.effective_chat.id]['players']):
        context.bot_data[update.effective_chat.id]['answers'].clear()
        await poll(update, context)
        return
    return

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ADD FINISH SHIT
    context.bot_data[update.effective_chat].Clear()
    await update.effective_message(
        "Game finished! Enter /lwf again to start a new one!\n\nHint: Want to change max players?\nSend \"/setplayers x\" with x being the number of players, without the quotes, before joining the next round!"
    )
    return

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text (
    "Cancelled round! Use /lwf to start over."
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
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.run_polling()

if __name__ == "__main__":
    main()