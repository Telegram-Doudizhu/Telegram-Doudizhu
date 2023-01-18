from uuid import uuid4
from asyncio import sleep
from functools import wraps
from cls.error import InternalError
from cls.cards import Cards
from cls.room import Room
from fun.rooms import *
from fun.robot import *

import logging
logger = logging.getLogger(__name__)

from telegram import Bot, Message, Update, InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent
from telegram import InlineQueryResultArticle, InlineQueryResultCachedSticker, Sticker
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ChosenInlineResultHandler, ContextTypes

def awaitify(sync_func):
    '''
        Wrap a synchronous callable to allow `await`ing it
    '''
    @wraps(sync_func)
    async def async_func(*args, **kwargs):
        return sync_func(*args, **kwargs)
    return async_func

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Start command handler
    '''
    await update.message.reply_text("Started.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Help command handler
        show detailed usage of the bot
    '''
    await update.message.reply_text("Use /start to test this bot.")


# buttons for callback query
class Button:
    (
        User1,
        User2,
        User3,
        Settings,
        Start,
    ) = map(chr, range(0x41, 0x46))
    nHHard = 0x50; HBack = chr(0x60)
    (
        DBid,
        DPass,
    ) = map(chr, range(0x61, 0x63))

class Operation:
    (
        Play,
        Pass
    ) = map(chr, range(0x71, 0x73))
    
def CON_CBD(room: Room, msg: str, msg1:str = '', data:list[str] = [], actionid:str = None):
    '''
        Construct callback data
        generate a unique actionid in room.roomdata, which should be used to identify callback
    '''
    if actionid is None:
        actionid = str(uuid4())[:8]
    room.roomdata = [actionid] + data
    return f"{room.id}|{actionid}|{msg}|{msg1}"

def DES_CBD(data: str):
    '''
        Destruct callback data
    '''
    return data.split('|')

async def GEN_KBD(room: Room) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for room management
    '''
    aid = str(uuid4())[:8]
    keyboard = [
        [ InlineKeyboardButton(room.owner.name, callback_data = CON_CBD(room, Button.User1, actionid = aid)), ],
        [ InlineKeyboardButton("Click to join" if room.user1 is None else room.user1.name, callback_data = CON_CBD(room, Button.User2, actionid = aid)), ],
        [ InlineKeyboardButton("Click to join" if room.user2 is None else room.user2.name, callback_data = CON_CBD(room, Button.User3, actionid = aid)), ],
        [ InlineKeyboardButton("Settings", callback_data = CON_CBD(room, Button.Settings, actionid = aid)), ],
        [ InlineKeyboardButton("Start!", callback_data = CON_CBD(room, Button.Start, actionid = aid)), ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def GEN_KBD_HARD(room: Room, parent: str) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for hard mode selection
    '''
    aid = str(uuid4())[:8]
    keyboard = []
    for i, name in enumerate(Room.Robot.hard_list):
        keyboard.append([ InlineKeyboardButton(name, callback_data = CON_CBD(room, parent, chr(Button.nHHard + i), actionid = aid)), ])
    keyboard.append([ InlineKeyboardButton("Back", callback_data = CON_CBD(room, parent, Button.HBack, actionid = aid)), ])
    return InlineKeyboardMarkup(keyboard)

async def GEN_KBD_DLORD(room: Room) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for lord decision
    '''
    aid = str(uuid4())[:8]
    keyboard = [
        [
            InlineKeyboardButton("Bid", callback_data = CON_CBD(room, Button.DBid, actionid = aid)),
            InlineKeyboardButton("Pass", callback_data = CON_CBD(room, Button.DPass, actionid = aid)),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def GEN_KBD_PLAY(text:str = "Click to play") -> InlineKeyboardMarkup:
    '''
        Generate keyboard for next player to make choice
    '''
    keyboard = [
        [InlineKeyboardButton(text, switch_inline_query_current_chat = '')],
    ]
    return InlineKeyboardMarkup(keyboard)


def cards_string(cards: Cards) -> str:
    '''
        Generate a more readable cards string
    '''
    suit = {"S": "♠", "H": "♥", "C": "♣", "D": "♦"}
    cards_str = repr(cards)
    for k, v in suit.items():
        cards_str = cards_str.replace(k, v)
    return cards_str

async def next_play_cards(bot: Bot, room: Room):
    '''
        Play cards until a real user
        including room ending workflow
    '''
    while True:
        await sleep(1)
        if room.win is not False:
            break
        msg = ''
        if not room.is_first:
            msg += f"Last player pos:{room.lastcur+1} has {room.lastcards.length} cards left.\n"
        if type(room.users[room.cur]) is Room.Robot:
            cards = await awaitify(what_robot_play)(room)
            assert(room.playable(cards))
            msg += f"{room.user.name} [{'LORD' if room.lord == room.cur else 'FARM'}] pos:{room.cur+1} chose "
            if len(cards) == 0:
                msg += 'to skip this round.'
                logger.info(f"Robot skipped pos:{room.cur} {room.user.name} in room {room.id}")
            else:
                msg += f"{cards_string(cards)}"
                logger.info(f"Robot played ({repr(cards)}) pos:{room.cur} {room.user.name} in room {room.id}")
            await bot.send_message(room.chatid, msg)
            assert(room.play(cards) is True)
        else:
            msg += f"{room.user.name} [{'LORD' if room.lord == room.cur else 'FARM'}], it's your turn:"
            await bot.send_message(room.chatid, msg, reply_markup = await GEN_KBD_PLAY())
            return
    winner = room.win
    loser1 = (winner + 1) % 3
    loser2 = (winner + 2) % 3
    await bot.send_message(room.chatid, f"Winner determined, room base multiplier 501x\n"
                                f"{room.users[winner].name} [{'LORD' if room.lord == winner else 'FARM'}] points += 0\n"
                                f"{room.users[loser1].name} [{'LORD' if room.lord == loser1 else 'FARM'}] points -= 0\nleft cards {cards_string(room.user_cards(loser1))}\n"
                                f"{room.users[loser2].name} [{'LORD' if room.lord == loser2 else 'FARM'}] points -= 0\nleft cards {cards_string(room.user_cards(loser2))}\n")
    await sleep(1)
    logger.info(f"Room restarted: {room.id}, last winner int:{winner}.")
    room.reset()
    await bot.send_message(room.chatid, "A new room has been created for you.", reply_markup = await GEN_KBD(room))


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        /new command handler
        create a new room, with the caller as the owner (first player)
        replied with buttons:
            - users: three buttons with representing users (updated when joining)
            - - join: join in this place
            - - add a robot: add a robot in this place
            - - leave: leave this room (destroy the room when the owner exits)
            - settings: trigger /settings inline query
            - start: start the game (available when three players joined)
    '''
    room = Room.create(update.message.chat_id, Room.User(update.effective_user.id, f"User @{update.effective_user.username}"))
    if room is False:
        await update.message.reply_text("You are already in a room.")
        return
    logger.info(f"Room created: {room.id}, owner: {room.owner.name}")
    reply_markup = await GEN_KBD(room)
    await update.message.reply_text("A new room has been created for you.", reply_markup = reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Callback handler
        used in room management
    '''
    query = update.callback_query
    
    async def error(msg: str):
        logging.critical(InternalError(msg), exc_info = True)
        await query.edit_message_text(text = "Internal error has occurred.\n" + msg)

    roomid, actionid, msg, msg1, = DES_CBD(query.data)
    room = Room.from_roomid(roomid)
    if room is None:
        await query.edit_message_text(text = "This room has been destroyed.")
        await query.answer()
        return
    
    if actionid != room.actionid:
        await query.answer(text = "This action is either duplicated or expired.")
        return

    async def start_bid(room: Room, last: Message):
        # relating workflow should be reimplement
        await sleep(1) # telegram api limitations
        room.reset(); room.start() # a simple restart
        logger.info(f'Room deck reset, id: {room.id}, cards: ({repr(room.user_cards(0))}), ({repr(room.user_cards(1))}), ({repr(room.user_cards(2))})')
        while type(room.user) is Room.Robot: # at least one real player
            await sleep(1)
            bid = await awaitify(will_robot_bid)(room)
            txt = "bidded" if bid else "passed"
            assert(room.bids(bid) is True) # no reason to fail here
            logger.info(f"User {txt} lord, {room.user.name} in room {room.id}.")
            last = await last.reply_text(text = f"{room.user.name} {txt} in this round.") 
            assert(room.next_bid() is True) # no reason to fail here
        markup = await GEN_KBD_DLORD(room)
        await last.reply_text(f"{room.user.name}, make your choice:", reply_markup = markup)

    text = None
    match room.state:
        
        case Room.STATE_JOINING:
            match msg:
                case Button.User1:
                    if query.from_user.id == room.owner.id:
                        logger.info(f"Room destroyed: {room.id}, owner: {room.owner.name} left")
                        room.destroy(); del room
                        await query.edit_message_text(text = "The owner has left the room.")
        
                case Button.User2 | Button.User3:
                    pos = 2 if msg == Button.User2 else 3
                    occupied = bool(room.users[pos - 1] is not None)
                    join = room.join1 if msg == Button.User2 else room.join2
                    leave = room.leave1 if msg == Button.User2 else room.leave2
                    refresh = False
                    if not occupied and query.from_user.id == room.owner.id:
                        match msg1:
                            case '':
                                reply_markup = await GEN_KBD_HARD(room, msg)
                                await query.edit_message_text(text = "Select a hard mode for the robot.", reply_markup = reply_markup)
                            case Button.HBack:
                                refresh = True
                            case msg1 if msg1 in map(chr, range(Button.nHHard, Button.nHHard + len(Room.Robot.hard_list))):
                                robot = Room.Robot(ord(msg1) - Button.nHHard)
                                leave() # force leave
                                if (ret:=join(robot)) is True:
                                    refresh = True
                                    logger.info(f"Robot {robot.name} joined in room {room.id}, pos:{pos}")
                                    text = f"Robot {robot.name} joined in pos:{pos}."
                                else:
                                    text = ret  
                            case _:
                                await error(f"Invalid button ({msg}) pressed.")
                    elif msg1 != '':
                        pass
                    elif occupied and query.from_user.id == room.owner.id:
                        refresh = True
                        name = room.users[pos - 1].name
                        if (ret:=leave()) is True:
                            logger.info(f"Kick user {name} from room {room.id}, pos:{pos}")
                            text = f"Kicked user {name} from room."
                        else:
                            text = ret
                    elif occupied and (query.from_user.id == room.users[pos - 1].id):
                        refresh = True
                        name = room.users[pos - 1].name
                        if (ret:=leave()) is True:
                            logger.info(f"User left {name}, room {room.id}, pos:{pos}")
                            text = "You have left the room."
                        else:
                            text = ret
                    elif not occupied:
                        refresh = True
                        if (ret:=join(Room.User(query.from_user.id, f"User @{query.from_user.username}"))) is True:
                            logger.info(f"User joined {room.users[pos - 1].name}, room {room.id}, pos:{pos}")
                            text = f"You have joined the room in pos:{pos}."
                        else:
                            text = ret
                    else:
                        text = "This place is occupied."
                    if refresh:
                        reply_markup = await GEN_KBD(room)
                        await query.edit_message_text(text = "A new room has been created for you.", reply_markup = reply_markup)
        
                case Button.Settings:
                    if query.from_user.id == room.owner.id:
                        text = "NOT IMPLEMENTED" # TODO
                    else:
                        text = "You are not the owner."
        
                case Button.Start:
                    if query.from_user.id == room.owner.id:
                        if (ret:=room.start()) is True:
                            room.roomdata = None # stop accepting any actions
                            logger.info(f"Room started: {room.id}.")
                            await query.edit_message_text(text = "This room has started.", reply_markup = await GEN_KBD_PLAY("Click to view your cards"))
                            await start_bid(room, query.message)
                        else:
                            text = ret
                    else:
                        text = "You are not the owner."
                case _:
                    await error(f"Invalid button ({msg}) pressed.")
        
        case Room.STATE_DECIDING:
            match msg:
                case Button.DBid | Button.DPass:
                    bid = bool(msg == Button.DBid)
                    txt = "bidded" if bid else "passed"
                    pos = room.user_index(query.from_user.id)
                    last = query.message; bot = False
                    while pos == room.cur: # continue for robots
                        room.roomdata = None # stop accepting any actions
                        if (ret:=room.bids(bid)) is True:
                            logger.info(f"User {txt} lord pos {room.cur}, {room.user.name} in room {room.id}.")
                            func = query.edit_message_text if not bot else last.reply_text
                            last = await func(text = f"{room.user.name} {txt} in this round.")
                            if room.lord is not False:
                                assert(room.decide_lord(room.lord) is True) # no reason to fail here
                                await sleep(1)
                                logger.info(f"Room lord decided, id: {room.id}, pos: {room.lord}, cards: {repr(room.lord_cards)}")
                                await last.reply_text(f"Lord decided. Give {room.user.name} in pos:{room.cur+1} three cards.\n" + cards_string(room.lord_cards)
                                                        ,disable_notification = True)
                                await sleep(3)
                                await next_play_cards(update.get_bot(), room)
                                break
                            if room.next_bid() is False:
                                await sleep(1)
                                last = await last.reply_text("Nobody bids. Starting a new round.", reply_markup = await GEN_KBD_PLAY("Click to view your cards"))
                                await start_bid(room, last)
                            else:
                                if type(room.user) is Room.Robot:
                                    bid = await awaitify(will_robot_bid)(room)
                                    txt = "bidded" if bid else "passed"
                                    pos = room.cur
                                    bot = True
                                    await sleep(1)
                                    continue
                                markup = await GEN_KBD_DLORD(room)
                                last = await last.reply_text(f"{room.user.name}, make your choice:", reply_markup = markup)
                        else:
                            text = ret
                        break
                    else:
                        text = "It's not your turn yet."
                case _:
                    await error(f"Invalid button ({msg}) pressed.")
            
        case _:
            await error(f"Invalid room state int:{room.state} for this action.")

    await query.answer(text)

async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Inline query handler
        used for extended card selection
    '''
    query = update.inline_query.query
    user = update.inline_query.from_user
    
    results = list()
    def result_append(title: str, chosen_text: str = None, tid: str = None, reply_markup: InlineKeyboardMarkup = None):
        chosen_text = title if chosen_text is None else chosen_text
        if tid is None:
            tid = str(uuid4())
        results.append(InlineQueryResultArticle(tid, title, InputTextMessageContent(chosen_text), reply_markup = reply_markup))

    room:Room = Room.from_userid(user.id)
    if room is None:
        result_append("You are not in any room.",
                    "You are not in any room. Use /new to create a room or join other rooms")
        await update.inline_query.answer(results, 0, True)
        return

    def parse_name(name: str) -> str:
        '''
            Disable notification of username
        '''
        return name.replace('@', '')

    room_string = f"Room {room.id}: (state int:{room.state})\n"
    room_string += f"Owner: {room.owner.name}, points: 501\n"
    room_string += f"User2: {room.user1.name}, points: 501\n"
    room_string += f"User3: {room.user2.name}, points: 501\n"
    left_string = ''
    left_string += f"Owner [{'LORD' if room.lord == 0 else 'FARM'}]: {room.owner.name}, cards: {room.user_cards(0).length} left\n"
    left_string += f"User2 [{'LORD' if room.lord == 1 else 'FARM'}]: {room.user1.name}, cards: {room.user_cards(1).length} left\n"
    left_string += f"User3 [{'LORD' if room.lord == 2 else 'FARM'}]: {room.user2.name}, cards: {room.user_cards(2).length} left\n"

    match room.state:
        case Room.STATE_JOINING:
            result_append("This room has not started.")
        case Room.STATE_DECIDING:
            result_append("The lord is being decided.", room_string)
            user_cards = room.user_cards(idx = room.user_index(user.id))
            if type(user_cards) is str:
                results.clear()
                result_append("Internal error has occurred.", user_cards)
            else:
                result_append(cards_string(user_cards), left_string)
        case Room.STATE_PLAYING:
            user_cards = room.user_cards(idx = room.user_index(user.id))
            if type(user_cards) is str:
                results.clear()
                result_append("Internal error has occurred.", user_cards)
            else:
                if room.cur == room.user_index(user.id):
                    aid = str(uuid4())[:8] # notice that data and actionid are both overridden by the last CON_CBD()
                    play_cards = Cards.from_cardlist(query, user_cards)
                    if len(query.strip()) == 0:
                        if room.lastplayed.length == 0:
                            if room.lastvcards.length != 0:
                                result_append(f"Last last played: {repr(room.lastvcards)}", f"Last last played: {cards_string(room.lastvcards)}")
                        else:
                            result_append(f"Last played: {repr(room.lastplayed)}", f"Last played: {cards_string(room.lastplayed)}")
                    elif play_cards is False or len(play_cards) == 0 or not room.playable(play_cards):
                        result_append(f"Illegal card combination")
                    else:
                        result_append(
                            f"PLAY {repr(play_cards)}",
                            f"Play {cards_string(play_cards)}",
                            tid = CON_CBD(room, Operation.Play, data = [play_cards], actionid = aid),
                        )
                    if room.must is False:
                        result_append("PASS", "Skip this round.", tid = CON_CBD(room, Operation.Pass, data = [play_cards], actionid = aid))
                else:
                    result_append("It's not your turn yet.", left_string)
                result_append(cards_string(user_cards), left_string)
        case _:
            result_append("Internal error has occurred.", f"Invalid room state int:{room.state} for this action.")
    await update.inline_query.answer(results, 0, True)

async def chosen_result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
        Chosen inline result handler
        used for players' operation
    '''
    userid = update.chosen_inline_result.from_user.id
    if len(des:=DES_CBD(update.chosen_inline_result.result_id)) < 3:
        return
    roomid, actionid, msg, _ = des
    room = Room.from_roomid(roomid)
    roomdata = room.roomdata
    if room is None or actionid != room.actionid or room.cur != room.user_index(userid):
        await update.get_bot().send_message(room.chatid, f"Invalid request made by @{update.chosen_inline_result.from_user.username}.\n"
                                                        f"This incident will be reported.\n"
                     "Detailed information: " + "None" if room is None else f"{actionid} != {room.actionid} or {room.cur} != {room.user_index(userid)}",
                     disable_notification = True)
        return
    room.roomdata = None # stop accepting any actions
    match msg:
        case Operation.Play:
            logger.info(f"User played {repr(roomdata[1])} pos:{room.cur} {room.user.name} in room {room.id}")
            room.play(roomdata[1])
        case Operation.Pass:
            logger.info(f"User skipped pos:{room.cur} {room.user.name} in room {room.id}")
            room.play(Cards([]))
        case _:
            raise InternalError(f"Invalid operation ({msg}).")
    await next_play_cards(update.get_bot(), room)
    

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    '''
        Remove job with given name.
        clear timeout counting
    '''
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {repr(job.data)} seconds are over! {repr(context.user_data)}")
    keyboard = [
        [
            InlineKeyboardButton("f", callback_data="f"),
            InlineKeyboardButton("b", callback_data="b"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await job.data.edit_text(
        text=f"Edited whatever", reply_markup=reply_markup
    )

def start_bot(token:str, proxy:str = '') -> None:
    '''
        Start the bot (main entrance)
    '''
    token,proxy = token.strip(),proxy.strip()
    logger.info("Telegram bot preparing to start")
    
    app = Application.builder().token(token)
    if len(proxy) > 0:
        app = app.proxy_url(proxy)
    app = app.build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(InlineQueryHandler(inline_handler))
    app.add_handler(ChosenInlineResultHandler(chosen_result_handler))

    logger.warning("Telegram bot has started")
    app.run_polling()

__all__ = ('start_bot', )
