from otree.api import *
import random
import math


class Constants(BaseConstants):
    name_in_url = 'sender_receiver_game'
    players_per_group = 2
    num_rounds = 24
    BONUS_AMOUNT = Currency(5000)
    SENDER_ROLE = 'Player A'
    RECEIVER_ROLE = 'Player B'
    TIME_PER_ROUND = 20

# Predefined lists of payoff-relevant rounds for senders and receivers
# These vectors should be 12 rounds out of the total 24, for each role
PREDEFINED_SENDER_ROUNDS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
PREDEFINED_RECEIVER_ROUNDS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]

class Subsession(BaseSubsession):
    def creating_session(self):
        # Assign the predefined payoff-relevant rounds to each participant based on their role
        for p in self.session.get_participants():
            if p.role == 'sender':
                p.sender_payoff_rounds = PREDEFINED_SENDER_ROUNDS
            else:  # Receiver
                p.receiver_payoff_rounds = PREDEFINED_RECEIVER_ROUNDS


class Group(BaseGroup):
    secret_number = models.IntegerField(min=1, max=6)

    sender_message = models.IntegerField(
        choices=[
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
        ]
    )


    receiver_guess = models.FloatField(min=0, max=6)


class Player(BasePlayer):
    pass


def set_payoffs(group: Group):
    # Randomly select a secret number between 1 and 6
    group.secret_number = random.randint(1, 6)

    # Get the sender and receiver players
    sender = group.get_player_by_id(1)
    receiver = group.get_player_by_id(2)

    # Calculate the probability of winning based on guessed number
    # Linear probability: P(win bonus) = (guessed number - 1) / 5

    # Sender probability based on receiver guess
    if group.receiver_guess == 0:
        sender_prob = 1
    elif group.sender_message == 0:
        sender_prob = 0
    else:
        sender_prob = (group.receiver_guess - 1) / 5  # Linear increase in probability based on receiver's guess

    # Calculate the receiver's probability based on the given quadratic formula
    if group.receiver_guess == 0:
        receiver_prob = 0
    else:
        receiver_prob = 1 - (1 / 25) * (group.secret_number - group.receiver_guess) ** 2

    # Determine if players win the bonus using a binomial draw
    sender_wins = random.random() < sender_prob  # Random binomial trial based on sender's win probability
    receiver_wins = random.random() < receiver_prob  # Random binomial trial based on receiver's win probability

    # Set payoffs: BONUS_AMOUNT if the player wins, otherwise 0
    sender.payoff = Constants.BONUS_AMOUNT if sender_wins else Currency(0)
    receiver.payoff = Constants.BONUS_AMOUNT if receiver_wins else Currency(0)

# pages.py

class instructions1(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}


class instructions2(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}


class instructions3(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}

class instructions4(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}


class Round_number(Page):
    timeout_seconds = 3
    timer_text = 'The next round starts in:'


class role_info(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}


class start_page(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}

class SenderMessage(Page):
    form_model = 'group'
    form_fields = ['sender_message']

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1

    timeout_seconds = 20

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.group.sender_message = 0


class WaitForSender(WaitPage):
    pass


class ReceiverGuess(Page):
    form_model = 'group'
    form_fields = ['receiver_guess']

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2

    timeout_seconds = 20

    @staticmethod
    def vars_for_template(player: Player):
        # Fetch sender message from the group model
        sender_message = player.group.sender_message

        return dict(
            sender_message=sender_message  # Pass the sender's message to the template
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            max_guess=6,  # Maximum allowed guess
            min_guess=1  # Minimum allowed guess
        )
    def before_next_page(player, timeout_happened):
        player.group.receiver_guess = 0


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(self):
        return {
            'secret_number': self.group.secret_number,
            'sender_message': self.group.sender_message,
            'receiver_guess': self.group.receiver_guess,
            'sender_payoff': self.group.get_player_by_role('Player A').payoff,
            'receiver_payoff': self.group.get_player_by_role('Player B').payoff,
        }

    timeout_seconds = 15


page_sequence = [instructions1, instructions2, instructions3, instructions4, role_info, start_page, Round_number, SenderMessage, WaitForSender, ReceiverGuess,
                 ResultsWaitPage, Results]
