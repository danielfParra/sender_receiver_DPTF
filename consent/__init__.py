from otree.api import *

author = 'Daniel Parra'
doc = """
Consent
"""


class Constants(BaseConstants):
    name_in_url = 'consent'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.IntegerField(
        label='''He leído la información sobre
    de datos y doy mi consentimiento para participar en el experimento y en el
    tratamiento de datos:''',
        choices=[[0, 'No'], [1, 'Sí']],
    )
    # consent2 = models.IntegerField(
    #     label='''Can you be in front of the screen for the
    # next 15 minutes?''',
    #     choices=[[0, 'No'], [1, 'Yes']],
    # )


# FUNCTIONS
# PAGES
class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']


def consent_error_message(player, value):
    if value != 1:
        return '''Si no está de acuerdo, no puede participar en el experimento de hoy.
        En este caso, puede cerrar la ventana y ponerse en contacto con los
        experimentadores.'''


# class Consent2(Page):
#     form_model = 'player'
#     form_fields = ['consent2']
#
#     @staticmethod
#     def consent2_error_message(player: Player, value):
#         if value != 1:
#             return '''If you do not have the time now, you cannot participate in today\'s
#             experiment. In this case, you can close the window and contact the
#             experimenters.'''


page_sequence = [Consent]
