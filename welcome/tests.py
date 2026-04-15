from otree.api import Bot, Submission
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(ComputerPage, {'computer_number': 1}, check_html=False)
        yield Welcome
