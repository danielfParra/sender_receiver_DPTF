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


class Subsession(BaseSubsession):
    pass


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
    group.secret_number = random.randint(1, 6)

    sender = group.get_player_by_id(1)
    receiver = group.get_player_by_id(2)

    # Calculate probabilities
    sender_prob = 1 - (1 - group.sender_message) ** 2  # revisar
    receiver_prob = 1 - (group.secret_number - group.receiver_guess) ** 2  # revisar

    # Determine if players win the bonus
    sender_wins = sender_prob > 0.5
    receiver_wins = receiver_prob < 0.5

    # 24 rondas, 12 pago (relevantes), 12 no pago (no relevantes)

    # Set payoffs
    sender.payoff = Constants.BONUS_AMOUNT if sender_wins else Currency(0)
    receiver.payoff = Constants.BONUS_AMOUNT if receiver_wins else Currency(0)

    # revisar los pagos


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


class WaitForSender(WaitPage):
    pass


class ReceiverGuess(Page):
    form_model = 'group'
    form_fields = ['receiver_guess']

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2

    timeout_seconds = 30

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


page_sequence = [instructions1, instructions2, instructions3, role_info, start_page, Round_number, SenderMessage, WaitForSender, ReceiverGuess,
                 ResultsWaitPage, Results]
