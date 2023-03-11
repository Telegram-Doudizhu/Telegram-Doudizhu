# Telegram Doudizhu

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Description

Telegram Doudizhu is a [Telegram](https://telegram.org/) bot written in [Python3.11.1](https://www.python.org/downloads/release/python-311/) that enables Telegram users to play the popular card game "Doudizhu" in Telegram group chats. The bot is designed to respond to commands and inline requests, providing a fair and enjoyable Doudizhu gaming experience for all players.

## Features

- Uses Telegram's inline keyboard to simplify game joining and starting.
- Allows players to obtain information about their hand using inline query.
- Includes AI computer players for game.

## Installation

1. Clone the repository: `git clone https://github.com/Telegram-Doudizhu/Telegram-Doudizhu.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Fill in the `TOKEN` field with your Telegram bot token. You can obtain a token from the [BotFather](https://telegram.me/BotFather).
5. Run the bot: `python main.py`

## Usage

To start a game, simply invite the bot to your Telegram group chat and type `/new` in the chat window. The bot will create a room for the user who send the command. Players can then join the game by clicking the buttons. Once all players have joined, the room owner can click start button to start the game, and the bot will shuffle the deck and deal the cards. Players can then take turns playing cards until a winner is determined.

To play a card, click the "Make Your Choice" button and enter the cards you wish to play in the chat box. For example, you can enter "34567" or "QQQ88". It's worth noting that "B" represents the small joker and "R" represents the big joker. Once the bot has confirmed the validity of your input, it will display a "Play" option in the inline query result. Simply click "Play" to 
play your card.

| Bot Command | Description |
| --- | --- |
| /new | Create a new room. |
| /kill | Terminate the room you are in. |
| /help | Get help information. |

## TODOs
- Use a database to store user information, such as beans, historical games, etc.
- Add room modes.

## Contributors

[<img src="https://avatars.githubusercontent.com/mnihyc" width="50" height="50" alt="mnihyc" style="border-radius: 50%;">](https://github.com/mnihyc) [<img src="https://avatars.githubusercontent.com/Alkri" width="50" height="50" alt="Alkri" style="border-radius: 50%;">](https://github.com/Alkri)

## License

Telegram Doudizhu is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) - see the LICENSE file for details.
