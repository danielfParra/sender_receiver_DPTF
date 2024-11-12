from otree.api import *
import random
import math


class Constants(BaseConstants):
    name_in_url = 'sender_receiver_game'
    players_per_group = 2
    num_rounds = 6
    BONUS_AMOUNT = Currency(5000)
    SENDER_ROLE = 'Player A'
    RECEIVER_ROLE = 'Player B'
    TIME_PER_ROUND = 20

    # Predefined lists of payoff-relevant rounds for senders and receivers
    # These vectors should be 12 rounds out of the total 24, for each role

    # Sender's payoff-relevant rounds
    PREDEFINED_SENDER_ROUNDS = [2, 5, 7, 9, 11, 13, 15, 16, 18, 19, 20, 23]

    # Receiver's payoff-relevant rounds
    PREDEFINED_RECEIVER_ROUNDS = [1, 3, 4, 6, 8, 10, 12, 14, 17, 21, 22, 24]


class Subsession(BaseSubsession):
        def creating_session(self):
            # Assign the predefined payoff-relevant rounds to each participant based on their role
            for p in self.session.get_participants():
                if p.role == SENDER_ROLE:
                    p.sender_payoff_rounds = PREDEFINED_SENDER_ROUNDS
                elif p.role == RECEIVER_ROLE:
                    p.receiver_payoff_rounds = PREDEFINED_RECEIVER_ROUNDS


class Group(BaseGroup):
    secret_number = models.IntegerField()

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
    is_sender_payoff_relevant = models.BooleanField(initial=False)
    is_receiver_payoff_relevant = models.BooleanField(initial=False)

def set_payoffs(group: Group):
    # Get the sender and receiver players
    sender = group.get_player_by_id(1)
    receiver = group.get_player_by_id(2)

    # Determine if the current round is payoff-relevant for the sender and receiver
    is_sender_payoff_relevant = sender.round_number in Constants.PREDEFINED_SENDER_ROUNDS
    is_receiver_payoff_relevant = receiver.round_number in Constants.PREDEFINED_RECEIVER_ROUNDS



    # Calculate the probability of winning based on guessed number
    # Linear probability: P(win bonus) = (guessed number - 1) / 5

    # Sender probability based on receiver guess
    if group.receiver_guess == 0:
        sender_prob = 1
    elif group.sender_message == 0:
        sender_prob = 0
    else:
        sender_prob = (group.receiver_guess - 1) / 5  # Linear increase in probability based on receiver's guess

    print(sender_prob)

    # Calculate the receiver's probability based on the given quadratic formula
    if group.receiver_guess == 0:
        receiver_prob = 0
    else:
        receiver_prob = 1 - (1 / 25) * (group.secret_number - group.receiver_guess) ** 2

    # Determine if players win the bonus using a binomial draw
    sender_wins = random.random() < sender_prob  # Random binomial trial based on sender's win probability
    receiver_wins = random.random() < receiver_prob  # Random binomial trial based on receiver's win probability

    # Apply special conditions for sender and receiver payoffs
    if group.sender_message == 0:
        # If sender didn't send a message, their payoff is 0
        sender.payoff = Currency(0)
    elif group.receiver_guess == 0:
        # If receiver didn't guess, their payoff is 0 and sender gets the bonus if they sent a message
        receiver.payoff = Currency(0)
        sender.payoff = Constants.BONUS_AMOUNT if group.sender_message > 0 else Currency(0)
    else:
        # Set payoffs based on win probabilities without considering payoff relevance
        sender.payoff = Constants.BONUS_AMOUNT if sender_wins else Currency(0)
        receiver.payoff = Constants.BONUS_AMOUNT if receiver_wins else Currency(0)

    # Print statement with detailed round information for debugging
    print(f"Round {sender.round_number}:")
    print(f"  - Secret number: {group.secret_number}")
    print(f"  - Sender's message: {group.sender_message}")
    print(f"  - Receiver's guess: {group.receiver_guess}")
    print(f"  - Sender probability: {sender_prob}, Receiver probability: {receiver_prob}")
    print(f"  - Sender wins: {sender_wins}, Receiver wins: {receiver_wins}")
    print(f"  - Sender payoff: {sender.payoff} (Relevant: {is_sender_payoff_relevant})")
    print(f"  - Receiver payoff: {receiver.payoff} (Relevant: {is_receiver_payoff_relevant})")
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

    timeout_seconds = Constants.TIME_PER_ROUND

    @staticmethod
    def vars_for_template(player: Player):
        current_round = player.round_number
        is_receiver_payoff_relevant = current_round in Constants.PREDEFINED_RECEIVER_ROUNDS
        return dict(
            is_receiver_payoff_relevant=is_receiver_payoff_relevant
        )


    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.group.sender_message = 0

        # Generate a new secret number for each round (whether timeout happens or not)
        player.group.secret_number = random.randint(1, 6)

    @staticmethod
    def before_next_page(player, timeout_happened):
        group = player.group
        current_round = player.round_number

        # Handle timeout: set sender_message to 0 if timeout happens
        if timeout_happened:
            group.sender_message = 0

        # Generate a new secret number for each round
        group.secret_number = random.randint(1, 6)

        # Determine if the current round is payoff-relevant for sender and receiver
        player.is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        player.is_receiver_payoff_relevant = current_round in Constants.PREDEFINED_RECEIVER_ROUNDS

class WaitForSender(WaitPage):
    pass


class ReceiverGuess(Page):
    form_model = 'group'
    form_fields = ['receiver_guess']

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2

    timeout_seconds = Constants.TIME_PER_ROUND
    @staticmethod
    def vars_for_template(player: Player):
        # Obtener el mensaje del sender
        sender_message = player.group.sender_message

        # Verificar si la ronda es payoff-relevant para el Sender (Participante A)
        current_round = player.round_number
        is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS

        return dict(
            sender_message=sender_message,  # Pasar el mensaje del sender
            is_sender_payoff_relevant=is_sender_payoff_relevant  # Pasar si la ronda es payoff-relevant para el Sender
        )
    @staticmethod
    def js_vars(player: Player):
        return dict(
            max_guess=6,  # Maximum allowed guess
            min_guess=1  # Minimum allowed guess
        )
    @staticmethod
    def before_next_page(player, timeout_happened):
        # Only set receiver_guess to 0 if timeout happens
        if timeout_happened:
            player.group.receiver_guess = 0

        current_round = player.round_number

        # Determine if the current round is payoff-relevant for sender and receiver
        player.is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        player.is_receiver_payoff_relevant = current_round in Constants.PREDEFINED_RECEIVER_ROUNDS


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(self):
        # Get the sender and receiver players
        sender = self.group.get_player_by_id(1)
        receiver = self.group.get_player_by_id(2)

        return {
            'secret_number': self.group.secret_number,
            'sender_message': self.group.sender_message,
            'receiver_guess': self.group.receiver_guess,
            'sender_payoff': sender.payoff,
            'receiver_payoff': receiver.payoff,
        }

    timeout_seconds = Constants.TIME_PER_ROUND

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        current_round = player.round_number
        sender = player.group.get_player_by_id(1)
        receiver = player.group.get_player_by_id(2)

        # Check if this round is payoff-relevant for the sender and receiver
        is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        is_receiver_payoff_relevant = current_round in Constants.PREDEFINED_RECEIVER_ROUNDS

        # If the round is NOT payoff-relevant, we subtract that round's payout from the cumulative total.
        if not is_sender_payoff_relevant:
            sender.payoff = 0 # Subtract payment if not relevant
        if not is_receiver_payoff_relevant:
            receiver.payoff = 0 # Subtract payment if not relevant

        print(f"Round {current_round}: Sender Payoff = {sender.payoff}, Receiver Payoff = {receiver.payoff}")
        print(f"Total Sender Payoff (Cumulative): {sender.participant.payoff}")
        print(f"Total Receiver Payoff (Cumulative): {receiver.participant.payoff}")

page_sequence = [instructions1, instructions2, instructions3, instructions4, role_info, start_page, Round_number, SenderMessage, WaitForSender, ReceiverGuess,
                 ResultsWaitPage, Results]
