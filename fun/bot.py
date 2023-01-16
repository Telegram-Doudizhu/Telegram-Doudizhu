from uuid import uuid4
from asyncio import sleep
from cls.error import InternalError
from cls.room import Room
from fun.rooms import *
from fun.robot import *
from cls.cards import Cards
from fun.cards import split_cardstr

import logging
logger = logging.getLogger(__name__)

from telegram import Message, InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, Update
from telegram import InlineQueryResultArticle, InlineQueryResultCachedSticker, Sticker
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ChosenInlineResultHandler, ContextTypes

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
    
def CON_CBD(roomid: str, msg: str, msg1:str = ''):
    '''
        Construct callback data for a button
    '''
    return f"{roomid}|{msg}|{msg1}"

def DES_CBD(data: str):
    '''
        Destruct callback data
    '''
    return data.split('|')

async def GEN_KBD(room: Room) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for room management
    '''
    keyboard = [
        [ InlineKeyboardButton(room.owner.name, callback_data = CON_CBD(room.id, Button.User1)), ],
        [ InlineKeyboardButton("Click to join" if room.user1 is None else room.user1.name, callback_data = CON_CBD(room.id, Button.User2)), ],
        [ InlineKeyboardButton("Click to join" if room.user2 is None else room.user2.name, callback_data = CON_CBD(room.id, Button.User3)), ],
        [ InlineKeyboardButton("Settings", callback_data = CON_CBD(room.id, Button.Settings)), ],
        [ InlineKeyboardButton("Start!", callback_data = CON_CBD(room.id, Button.Start)), ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def GEN_KBD_HARD(room: Room, parent: str) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for hard mode selection
    '''
    keyboard = []
    for i, name in enumerate(Room.Robot.hard_list):
        keyboard.append([ InlineKeyboardButton(name, callback_data = CON_CBD(room.id, parent, chr(Button.nHHard + i))), ])
    keyboard.append([ InlineKeyboardButton("Back", callback_data = CON_CBD(room.id, parent, Button.HBack)), ])
    return InlineKeyboardMarkup(keyboard)

async def GEN_KBD_DLORD(room: Room) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for lord decision
    '''
    keyboard = [
        [
            InlineKeyboardButton("Bid", callback_data = CON_CBD(room.id, Button.DBid)),
            InlineKeyboardButton("Pass", callback_data = CON_CBD(room.id, Button.DPass)),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


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

    roomid, msg, msg1 = DES_CBD(query.data)
    room = Room.from_roomid(roomid)
    if room is None:
        await query.edit_message_text(text = "This room has been destroyed.")
        await query.answer()
        return
    
    async def start_bid(room: Room, last: Message):
        await sleep(1) # telegram api limitations
        room.reset(); room.start() # a simple restart
        while type(room.user) is Room.Robot: # at least one real player
            await sleep(1)
            bid = will_robot_bid(room)
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
                            logger.info(f"Room started: {room.id}.")
                            await query.edit_message_text(text = "This room has started.")
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
                        if (ret:=room.bids(bid)) is True:
                            logger.info(f"User {txt} lord, {room.user.name} in room {room.id}.")
                            func = query.edit_message_text if not bot else last.reply_text
                            last = await func(text = f"{room.user.name} {txt} in this round.")
                            if room.lord is not False:
                                assert(room.decide_lord(room.lord) is True) # no reason to fail here
                                await sleep(1)
                                await last.reply_text(f"Lord decided. Give {room.user.name} in pos:{pos+1} three cards.\n" + repr(room.lord_cards))
                                break
                            if room.next_bid() is False:
                                await sleep(1)
                                last = await last.reply_text("Nobody bids. Starting a new round.")
                                await start_bid(room, last)
                            else:
                                if type(room.user) is Room.Robot:
                                    bid = will_robot_bid(room)
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
    results = list()
    query = update.inline_query.query
    user = update.inline_query.from_user
    room = Room.from_userid(user.id)
    if room is None:
        results.append(
            InlineQueryResultArticle(
                id = str(uuid4()),
                title = "You are not in any room.",
                input_message_content = InputTextMessageContent(
                    'You are not in any room. Use /new to create a room or '
                    'click the join button in other rooms to join the game.'
                )
            )
        )
        await update.inline_query.answer(results)
        return
    match room.state:
        case Room.STATE_JOINING:
            results.append(
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title = "Waiting for the room owner to start game.",
                    input_message_content = InputTextMessageContent("Waiting for the room owner to start game.")
                )
            )
        case Room.STATE_DECIDING:
            results.append(
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title = "Waiting for the lord to be decided.",
                    input_message_content = InputTextMessageContent("Waiting for the lord to be decided.")
                )
            )
        case Room.STATE_PLAYING:
            user_cards = room.all_cards(idx = room.user_index(user.id))
            if type(user_cards) is str:
                raise InternalError(user_cards)
            cards_result = ""
            card_suit = {"S": "♠", "H": "♥", "C": "♣", "D": "♦"}
            for c in user_cards.cards:
                card = repr(c)
                if card == 'R' or card == 'B':
                    cards_result += card
                else:
                    cards_result += card[:-1] + card_suit[card[-1]]
            if query != "" and room.cur == room.user_index(user.id):
                query = split_cardstr(query)
                if type(query) is bool:
                    results.append(
                        InlineQueryResultArticle(
                            id = str(uuid4()),
                            title = "Play",
                            input_message_content = InputTextMessageContent("You can't play these cards.")
                        )
                    )
                else:
                    logger.info(query)
                    play_cards = Cards.from_cardlist(query, user_cards)
                    if type(play_cards) is bool:
                        results.append(
                            InlineQueryResultArticle(
                                id = str(uuid4()),
                                title = "Play ❌",
                                input_message_content = InputTextMessageContent("You can't play these cards.")
                            )
                        )
                    else:
                        if room.playable(play_cards):
                            results.append(
                                InlineQueryResultArticle(
                                    id = "PlayCards:" + repr(play_cards),
                                    title = "Play ✔",
                                    input_message_content = InputTextMessageContent(
                                        f"Player {user.name} play {play_cards}.")
                                )
                            )
                        else:
                            results.append(
                                InlineQueryResultArticle(
                                    id = str(uuid4()),
                                    title = "Play ❌",
                                    input_message_content = InputTextMessageContent("You can't play these cards.")
                                )
                            )
            if room.cur == room.user_index(user.id):
                results.append(
                    InlineQueryResultArticle(
                        id = "Pass",
                        title = "PASS",
                        input_message_content = InputTextMessageContent("You passed.")
                    )
                )
            results.append(
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title = cards_result,
                    input_message_content = InputTextMessageContent("Please type the card you want to play in the textbox.")
                )
            )
    await update.inline_query.answer(results, 0)

async def chosen_result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chosen_inline_result.from_user
    room = Room.from_userid(user.id)
    if room is None:
        return
    result = update.chosen_inline_result.result_id.split(":")[0]
    cards = update.chosen_inline_result.result_id.split(":")[-1]
    match result:
        case "None":
            return
        case "PlayCards":
            if Cards.from_cardlist(cards) is False:
                return
            room.play(Cards.from_cardlist(cards))
        case "Pass":
            room.next()
        case _:
            pass
    

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
