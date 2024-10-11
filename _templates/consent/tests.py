from otree.api import Currency as cu, currency_range
from . import *
from otree.api import Bot, SubmissionMustFail



class PlayerBot(Bot):
    def play_round(self):
        yield SubmissionMustFail(Consent, dict(consent=0))
        yield Consent, dict(consent=1)
        # yield SubmissionMustFail(Consent2, dict(consent2=0))
        # yield Consent2, dict(consent2=1)
