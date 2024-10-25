from otree.api import *

doc = """PaymentInfo"""


class Constants(BaseConstants):
    name_in_url = 'payment_info'
    players_per_group = None
    num_rounds = 1
    BONUS_AMOUNT = Currency(5000)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

class PaymentInfo(Page):

    def vars_for_template(self):
        payoff = self.participant.payoff
        return dict(
            payoff=Currency(payoff),
        )
#
# class Redirect(Page):
#     pass


page_sequence = [PaymentInfo]