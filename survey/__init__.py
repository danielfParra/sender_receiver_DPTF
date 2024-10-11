from otree.api import *

class Constants(BaseConstants):
    name_in_url = 'survey'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # Demographics
    age = models.IntegerField(label='Age', min=13, max=125)

    gender = models.IntegerField(
        label='Gender',
        choices=[[0, 'Male'], [1, 'Female'], [2, 'Rather not say'], [3, 'Other']]
    )
    gender_add = models.StringField(blank=True, label='')
    education = models.IntegerField(
        choices=[[0, 'Less than High School'],
                 [1, 'High School'],
                 [2, 'Some College'],
                 [3, 'Associate Degree'],
                 [4, 'Bachelor\'s Degree'],
                 [5, 'Advanced or Professional Degree']
                 ],
        label='What is your highest level of education?'
    )
    student = models.IntegerField(
        label='Are you currently enrolled in college?',
        choices=[[0, 'No'], [1, 'Yes']]
    )
    experiments = models.IntegerField(
        label='Please give a rough estimate about the number of experiments you have participated in before',
        blank=True
    )

    reasoning = models.LongStringField(
        label='Please give a concise explanation of how you took your decisions in the experiment',
        blank=True
    )

    chosen_role = models.IntegerField(
        choices=[[1, 'Sender'],
                 [2, 'Receiver'],
                 [0, 'Indifferent'],
                 ],
        label='Imagine you were to play the same game again and had a choice, would you rather be Sender or Receiver'
    )

    

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender',  'education', 'student', 'experiments', 'reasoning', 'chosen_role']


page_sequence = [Demographics]