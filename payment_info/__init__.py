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
        return dict(
            payoff=self.participant.payoff,  # total bonus from all apps
            show_up_fee=self.session.config['participation_fee'],
            total_payment=self.participant.payoff_plus_participation_fee()
        )


page_sequence = [PaymentInfo]