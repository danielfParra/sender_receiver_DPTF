from otree.api import *
import random
import math


class Constants(BaseConstants):
    name_in_url = 'welcome'
    players_per_group = None
    num_rounds = 1
    BONUS_AMOUNT = Currency(4000)
    SHOW_UP_FEE = Currency(5000)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    payoff_relevant_list = models.LongStringField(blank=True, default='')
    computer_number = models.IntegerField(
        label='Introduce el número del computador en el que estás sentado '
              '(es el mismo número que te dimos en la llave para guardar tu celular)',
        min=1,
        max=50,
    )

class ComputerPage(Page):
    form_model = 'player'
    form_fields = ['computer_number']

    def before_next_page(player: Player, timeout_happened):
        # Overwrite participant.label with the PC number
        player.participant.label = str(player.computer_number)

    def is_displayed(player: Player):

        return player.round_number == 1    

class Welcome(Page):

    def is_displayed(player: Player):

        return player.round_number == 1

    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        # In the new 1-player architecture, EVERYONE is Player B
        player.participant.role = 'Player B'
        
        # Assign treatment from session config
        # Valid treatments: ExpertRep, Belief, FixBelief, NoUncertainty
        player.participant.treatment = player.session.config['treatment']
        

        
    # form_model = 'player'
    # form_fields = ['Prolific_ID']



page_sequence = [ComputerPage, Welcome]
