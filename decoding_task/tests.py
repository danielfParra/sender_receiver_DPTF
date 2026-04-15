from otree.api import Bot, Submission
from . import *


class PlayerBot(Bot):
    def play_round(self):
        # DecodingTask appears once in page_sequence; all 6 task cycles are JS-driven.
        # We submit a single page with simulated values.
        yield DecodingInstructions
        yield DecodingStart
        yield Submission(DecodingTask, {'decoding_answer': 3, 'correct_answers': 3}, check_html=False)
        yield DecodingTaskResults

