from otree.api import Bot, Submission
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Demographics, {
            'age': random.randint(18, 80),
            'gender': random.choice([0, 1, 2, 3]),
            'education': random.choice([0, 1, 2, 3, 4, 5]),
            'student': random.choice([0, 1]),
            'experiments': random.randint(0, 20),
            'reasoning': 'Tomé mis decisiones basándome en la información disponible.',
            'chosen_role': random.choice([0, 1, 2]),
        }, check_html=False)
        yield Submission(Redirect, check_html=False)
