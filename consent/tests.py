from otree.api import Bot, SubmissionMustFail
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield SubmissionMustFail(Consent, dict(consent=0))
        yield Consent, dict(consent=1)
