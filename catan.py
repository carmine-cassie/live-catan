from textual.app import App, ComposeResult
from textual.containers import (
    HorizontalGroup,
    VerticalGroup,
    HorizontalScroll,
    Container,
)
from textual.widgets import Footer, Header, Button, ProgressBar, RichLog, Label

from playsound import playsound

import random
import argparse

TURN_DURATION = 20

# Ascii Dice
dice = [
    "     \n     \n     ",
    "     \n  ■  \n     ",
    "    ■\n     \n■    ",
    "    ■\n  ■  \n■    ",
    "■   ■\n     \n■   ■",
    "■   ■\n  ■  \n■   ■",
    "■   ■\n■   ■\n■   ■",
]

"""
Numbers using Terrace font from https://patorjk.com/software/taag/
  ░██    ░██████   ░██████     ░████   ░████████  ░██████  ░█████████  ░██████   ░██████    ░████   
░████   ░██   ░██ ░██   ░██   ░██ ██   ░██       ░██   ░██ ░██    ░██ ░██   ░██ ░██   ░██  ░██ ░██  
  ░██         ░██       ░██  ░██  ██   ░███████  ░██             ░██  ░██   ░██ ░██   ░██ ░██ ░████ 
  ░██     ░█████    ░█████  ░██   ██         ░██ ░███████       ░██    ░██████   ░███████ ░██░██░██ 
  ░██    ░██            ░██ ░█████████ ░██   ░██ ░██   ░██     ░██    ░██   ░██       ░██ ░████ ░██ 
  ░██   ░██       ░██   ░██      ░██   ░██   ░██ ░██   ░██     ░██    ░██   ░██ ░██   ░██  ░██ ░██  
░██████ ░████████  ░██████       ░██    ░██████   ░██████      ░██     ░██████   ░██████    ░████   
"""
big_numbers = [
    "",
    "  ░██   \n░████   \n  ░██   \n  ░██   \n  ░██   \n  ░██   \n░██████ ",
    " ░██████  \n░██   ░██ \n      ░██ \n  ░█████  \n ░██      \n░██       \n░████████ ",
    " ░██████  \n░██   ░██ \n      ░██ \n  ░█████  \n      ░██ \n░██   ░██ \n ░██████  ",
    "   ░████   \n  ░██ ██   \n ░██  ██   \n░██   ██   \n░█████████ \n     ░██   \n",
    "░████████ \n░██       \n░███████  \n      ░██ \n░██   ░██ \n░██   ░██ \n ░██████  ",
    " ░██████  \n░██   ░██ \n░██       \n░███████  \n░██   ░██ \n░██   ░██ \n ░██████  ",
    "░█████████ \n░██    ░██ \n      ░██  \n     ░██   \n    ░██    \n    ░██    \n    ░██    ",
    " ░██████  \n░██   ░██ \n░██   ░██ \n ░██████  \n░██   ░██ \n░██   ░██ \n ░██████  ",
    " ░██████  \n░██   ░██ \n░██   ░██ \n ░███████ \n      ░██ \n░██   ░██ \n ░██████  ",
    "  ░██     ░████   \n░████    ░██ ░██  \n  ░██   ░██ ░████ \n  ░██   ░██░██░██ \n  ░██   ░████ ░██ \n  ░██    ░██ ░██  \n░██████   ░████   ",
    "  ░██     ░██   \n░████   ░████   \n  ░██     ░██   \n  ░██     ░██   \n  ░██     ░██   \n  ░██     ░██   \n░██████ ░██████ ",
    "  ░██    ░██████  \n░████   ░██   ░██ \n  ░██         ░██ \n  ░██     ░█████  \n  ░██    ░██      \n  ░██   ░██       \n░██████ ░████████ ",
]


class GameContainer(Container):
    """Contains the entire game"""


class BigNumber(Label):
    """A Large ASCII Number"""


class Dice(Label):
    """An ASCII Dice"""


class Player(Label):
    """Contains a single player's name"""


class GameInfo(VerticalGroup):
    """
    Information about what number has just been rolled.
    Contains two dice and a big number.
    Also shows the player names in the game.
    """

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            VerticalGroup(Dice(dice[0], id="dice-1"), Dice(dice[0], id="dice-2")),
            BigNumber(big_numbers[0]),
        )
        yield HorizontalScroll(
            *[
                Player(player)
                for player in self.parent.parent.parent.parent.parent.players
            ],
        )


class GameLog(VerticalGroup):
    """
    A log of events, above a button to interact with the game state.
    """

    def compose(self) -> ComposeResult:
        yield RichLog(auto_scroll=True, wrap=True)
        yield HorizontalGroup(Button("Begin", id="log-button"))


class CatanApp(App):
    """A Textual app to manage Live-Catan."""

    CSS_PATH = "livecatan.tcss"
    BINDINGS = []

    timer = None

    players = []

    # Perhaps a little quick-and-dirty. This is how we manage the game's state.
    # There are three states:
    # - Begin: the game is yet to begin
    # - Resume: we're waiting for the robber to be placed
    # - Quit: the game is happily in motion
    log_button = "Begin"

    def on_mount(self) -> None:
        self.title = "Live-Catan"
        self.theme = "gruvbox"

    def compose(self) -> ComposeResult:
        yield Header()
        yield GameContainer(
            VerticalGroup(
                ProgressBar(total=TURN_DURATION, show_percentage=False, show_eta=False),
                HorizontalGroup(GameInfo(), GameLog()),
            )
        )
        yield Footer(show_command_palette=False)

    def roll_dice(self):
        """
        Roll the dice!
        If we roll a 7, await the robber being placed.
        Otherwise, begin waiting to roll the dice again after TURN_DURATION seconds.
        """
        bar = self.query_one(ProgressBar)
        dice1 = self.query_one("#dice-1")
        dice2 = self.query_one("#dice-2")
        big_number = self.query_one(BigNumber)
        log = self.query_one(RichLog)

        # Reset the progress bar
        bar.progress = 0

        # Roll our dice
        result1 = random.randint(1, 6)
        result2 = random.randint(1, 6)

        # Update UI elements appropriately
        log.write(f"{result1}+{result2}={result1+result2}")
        dice1.update(dice[result1])
        dice2.update(dice[result2])
        big_number.update(big_numbers[result1 + result2])

        if result1 + result2 == 7:
            # If we rolled 7, choose a player to place the robber, and await input
            log.write(
                f"{self.players[random.randint(0, len(self.players) - 1)]} places the robber..."
            )
            self.log_button = "Resume"
            button = self.query_one("#log-button")
            button.label = self.log_button
        else:
            # Otherwise, set a timer to roll the dice again in TURN_DURATION seconds
            self.timer = self.set_interval(1, self.tick_progress, repeat=TURN_DURATION)

        # Play a sound effect to notify players that the dice have been rolled
        playsound("dice.mp3", block=False)

    def tick_progress(self):
        """
        Tick the progress bar forward. Triggered once a second between turns.
        If enough time has elapsed, roll the dice.
        """
        bar = self.query_one(ProgressBar)
        bar.advance(1)

        if bar.progress > TURN_DURATION:
            self.roll_dice()

    def on_ready(self) -> None:
        log = self.query_one(RichLog)
        log.write('Click "Begin" to start!')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle state interactions via a button being pressed.
        """
        button = event.button
        if self.log_button == "Begin" or self.log_button == "Resume":
            # Roll the dice and update button state
            self.roll_dice()
            self.log_button = "Quit"
            button.label = self.log_button
        elif self.log_button == "Quit":
            # Quit the App
            exit()


if __name__ == "__main__":
    # Create an argparser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--turn-duration",
        help="the time between automatic dice rolls",
        default=20,
        type=int,
    )
    parser.add_argument("player", help="the name of each player", nargs="+")

    # Parse args
    args = parser.parse_args()
    TURN_DURATION = args.turn_duration

    # Run the app
    app = CatanApp()
    app.players = args.player
    app.run()
