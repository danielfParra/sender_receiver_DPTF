# settings.py
from os import environ

SESSION_CONFIGS = [
    dict(
        name='sender_receiver_game_expertrep',
        display_name="Sender-Receiver Game: ExpertRep",
        num_demo_participants=4,
        app_sequence=['consent','welcome', 'decoding_task', 'N5_sender_receiver_game', 'payment_info', 'survey'],
        num_rounds=3,
        treatment='ExpertRep'
    ),
    dict(
        name='BOTs_sender_receiver_game',
        display_name="BOTS Sender-Receiver Game",
        use_browser_bots=True,
        num_demo_participants=16,
        app_sequence=['consent', 'welcome', 'N5_sender_receiver_game', 'payment_info', 'survey'],
        num_rounds=3,
        treatment='NoUncertainty'
    ),
    dict(
        name='sender_receiver_game_belief',
        display_name="Sender-Receiver Game: Belief",
        num_demo_participants=4,
        app_sequence=['consent','welcome', 'decoding_task', 'N5_sender_receiver_game', 'payment_info', 'survey'],
        num_rounds=3,
        treatment='Belief'
    ),
    dict(
        name='sender_receiver_game_fixbelief',
        display_name="Sender-Receiver Game: FixBelief",
        num_demo_participants=4,
        app_sequence=['consent','welcome', 'decoding_task', 'N5_sender_receiver_game', 'payment_info', 'survey'],
        num_rounds=3,
        treatment='FixBelief'
    ),
    dict(
        name='sender_receiver_game_nouncertainty',
        display_name="Sender-Receiver Game: NoUncertainty",
        num_demo_participants=4,
        app_sequence=['consent','welcome', 'decoding_task', 'N5_sender_receiver_game', 'payment_info', 'survey'],
        num_rounds=3,
        treatment='NoUncertainty'
    ),
    dict(
        name='survey',
        display_name="survey",
        num_demo_participants=20,
        app_sequence=['survey'],
        num_rounds=1,
    ),
]


ROOMS = [
    dict(
        name='N5_room',
        display_name='Room for sender-receiver sessions',
    ),
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=5000, doc=""
)

PARTICIPANT_FIELDS = ['role', 'sender_payoff_rounds', 'receiver_payoff_rounds', 'treatment', 'correct_answers', 'assigned_sender_code']
SESSION_FIELDS = ['treatment']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'es'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 0
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '{{ secret_key }}'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']