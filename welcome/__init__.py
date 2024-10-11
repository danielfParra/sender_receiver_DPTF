from otree.api import *
import random
import math


class Constants(BaseConstants):
    name_in_url = 'welcome'
    players_per_group = 2
    num_rounds = 1
    BONUS_AMOUNT = Currency(5000)
    SENDER_ROLE = 'Sender'
    RECEIVER_ROLE = 'Receiver'
    SHOW_UP_FEE = Currency(5000)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    payoff_relevant_list = models.LongStringField(blank=True, default='')

    
    # Whether the current round is payoff-relevant (1) or not (0)




class Welcome(Page):

    def is_displayed(player: Player):

        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        if player.id_in_group == 1:
            player.participant.role = 'Sender'
        else:
            player.participant.role = 'Receiver'

        

        
    # form_model = 'player'
    # form_fields = ['Prolific_ID']



page_sequence = [Welcome]
