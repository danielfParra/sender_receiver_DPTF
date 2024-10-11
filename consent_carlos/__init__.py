from otree.api import *

doc = """
Consent
"""


class Constants(BaseConstants):
    name_in_url = 'consent_carlos'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.IntegerField(label = '''I have read the data protection
    information and I consent_carlos to participation in the experiment and the stated
    processing of data:''',
    choices = [[0, 'No'], [1, 'Yes']])

    consent2 = models.IntegerField(label = '''Can you be in front of the screen for the 
    next 15 minutes?''',
    choices = [[0, 'No'], [1, 'Yes']])

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent_carlos']

    def consent_error_message(self, value):
        if value != 1:
            return '''If you do not agree, you cannot participate in today\'s
            experiment. In this case, you can close the window and contact the
            experimenters.'''

class Consent2(Page):
    form_model = 'player'
    form_fields = ['consent2']

    def consent2_error_message(self, value):
        if value != 1:
            return '''If you do not have the time now, you cannot participate in today\'s
            experiment. In this case, you can close the window and contact the
            experimenters.'''


page_sequence = [Consent, Consent2]