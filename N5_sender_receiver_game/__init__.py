from otree.api import *
import math
import random
import json
import time


class Constants(BaseConstants):
    name_in_url = 'sender_receiver_game'
    players_per_group = None  # All players in one subsession; data is stored per Player, not per Group
    num_rounds = 24
    BONUS_AMOUNT = Currency(4000)
    PIECE_RATE_DECODE = Currency(500)  # New constant for the piece rate per correct answer
    HONESTY_GUESS_BONUS = Currency(1000)  # Bonus for honesty guess
    CREDULITY_GUESS_BONUS = Currency(1000)  # Bonus for credulity guess
    EXPLANATION_BONUS = Currency(4000) # Bonus for the explanation task
    #RECEIVER_ROLE = 'Player B'
    POOL_SIZE = 5
    TIME_PER_ROUND = 40
    TIME_PER_ROUND_PREV = 20
    FEEDBACK_TIME = 10
    ATTEMPT_DELAY = 5

  
    TIME_PER_TASK = 20  # Time limit for each decoding task (in seconds)
    NUM_TASKS = 6  # Number of tasks in the decoding phase


    # Predefined lists of payoff-relevant rounds for senders and receivers
    # These vectors should be 12 rounds out of the total 24, for each role

    # Sender's payoff-relevant rounds
    PREDEFINED_SENDER_ROUNDS = [2, 5, 7, 9, 11, 13, 15, 16, 18, 19, 20, 23]

    # Receiver's payoff-relevant rounds
    PREDEFINED_RECEIVER_ROUNDS = [1, 3, 4, 6, 8, 10, 12, 14, 17, 21, 22, 24]

    # Load csv with encoded messages
    import pandas as pd
    file = '_static/data/encoded_messages.csv'
    df_encodings = pd.read_csv(file)

    # Load csv with decoding tasks (answer and encoding)
    import pandas as pd
    file = '_static/data/encoding_task.csv'
    df_decoding_tasks = pd.read_csv(file)

    # Control questions.
    Q_who_knows = '¿Quién conoce el número secreto?'
    O_who_knows = ['Jugador A', 'Jugador B', 'Ambos', 'Ninguno']
    A_who_knows = 'Ninguno'
    H_who_knows = 'Considere cómo se determina el número secreto. Si nadie ha recibido información sobre él, ¿cómo podría alguien conocerlo?'

    Q_task = '¿Cuál es tu tarea en este juego?'
    O_task = ['Adivinar el número secreto', 'Escribir un texto', 'Enviar un mensaje']
    A_task_PA = 'Enviar un mensaje'
    A_task_PB = 'Adivinar el número secreto'
    A_task_PB_Belief = 'Reportar mi creencia sobre la probabilidad de que el Jugador A delegó al computador'
    O_task_Belief = ['Reportar mi creencia sobre la probabilidad de que el Jugador A delegó al computador', 'Escribir un texto', 'Enviar un mensaje']
    H_task = 'Piensa en qué acción se te requiere realizar durante el juego. Tu rol determina tu tarea principal.'
    H_task_Belief = 'Recuerda: en lugar de adivinar directamente, tú reportas una creencia sobre el Jugador A y el computador calcula la suposición óptima por ti.'

    Q_payoff_PB = '¿Cómo maximizan su pago los jugadores en tu rol (Jugador B)?'
    O_payoff_PB = ['Adivinando el número secreto lo más precisamente posible',
                   'Adivinando un número lo más cercano posible al mensaje', 'Siempre adivinando bajo',
                   'Siempre adivinando alto']
    A_payoff_PB = 'Adivinando el número secreto lo más precisamente posible'
    H_payoff_PB = 'Tu objetivo es acercarte lo más posible al número secreto real. Cuanto más precisa sea tu adivinanza, mejor será tu pago.'

    Q_payoff_PA = '¿Cómo maximizan su pago los jugadores en tu rol (Jugador A)?'
    O_payoff_PA = ['Haciendo que el Jugador B adivine el número secreto',
                   'Haciendo que el Jugador B adivine lo más alto posible',
                   'Haciendo que el Jugador B adivine cerca del número enviado']
    A_payoff_PA = 'Haciendo que el Jugador B adivine lo más alto posible'
    H_payoff_PA = 'Tu pago depende de influir en la adivinanza del Jugador B. Piensa exactamente por qué depende de la adivinanza.'

    Q_payoff_other_PA = '¿Cómo maximizan su pago los jugadores en el otro rol (Jugador B)?'
    O_payoff_other_PA = ['Adivinando el número secreto lo más precisamente posible',
                         'Adivinando un número lo más cercano posible al mensaje', 'Siempre adivinando bajo',
                         'Siempre adivinando alto']
    A_payoff_other_PA = 'Adivinando el número secreto lo más precisamente posible'
    H_payoff_other_PA = 'Considera el objetivo del otro jugador. Su mejor estrategia está alineada con identificar el número secreto real, no solo responder al mensaje en sí.'

    Q_payoff_other_PB = '¿Cómo maximizan su pago los jugadores en el otro rol (Jugador A)?'
    O_payoff_other_PB = ['Haciendo que adivines el número secreto', 'Haciendo que adivines lo más alto posible',
                         'Haciendo que adivines cerca del número enviado']
    A_payoff_other_PB = 'Haciendo que adivines lo más alto posible'
    H_payoff_other_PB = 'El pago del otro jugador depende de influir en tu adivinanza. Piensa exactamente por qué depende de la adivinanza.'

    Q_independence = 'Considera el siguiente escenario:'
    Q_independence_text = 'Estás en la ronda 3 del juego. En las rondas 1 y 2, el número secreto fue 5. ¿Cuál de las siguientes afirmaciones sobre el número secreto en la ronda 3 es verdadera?'
    O_independence = ['Es probable que sea mayor que 5, ya que el número secreto fue 5 en las rondas anteriores',
                      'Es probable que sea menor que 5, ya que el número secreto fue 5 en las rondas anteriores',
                      'Es probable que sea 5, ya que el número secreto fue 5 en las rondas anteriores',
                      'Cualquier número es igualmente probable, independientemente de las rondas anteriores']
    A_independence = 'Cualquier número es igualmente probable, independientemente de las rondas anteriores'
    H_independence = 'Piensa en cómo se eligen los números: ¿el proceso recuerda valores pasados?'

    Q_secret_number_generation = '¿Cómo se genera el número secreto?'
    O_secret_number_generation = ['Lo elige el Jugador A', 'Lo elige el Jugador B',
                                  'Lo genera aleatoriamente el computador']
    A_secret_number_generation = 'Lo genera aleatoriamente el computador'
    H_secret_number_generation = 'El número secreto se determina de una manera que ni el Jugador A ni el Jugador B tienen control directo sobre él. Piensa de dónde podría venir el número si ningún jugador es responsable de elegirlo.'

    Q_no_knowledge_guess = 'Adivinanza sin información:'
    Q_no_knowledge_guess_text = 'Supón que no tienes información sobre el número secreto. ¿Cuál es la mejor estrategia para estar más cerca al real?'
    O_no_knowledge_guess = ['Adivinar un número aleatorio', 'Adivinar 7 (el número más alto)',
                            'Adivinar 1 (el número más bajo)', 'Adivinar 4 (el promedio de todos los números posibles)']
    A_no_knowledge_guess = 'Adivinar 4 (el promedio de todos los números posibles)'
    H_no_knowledge_guess = 'Si no tienes información, tu mejor adivinanza debería minimizar el error potencial en todas las posibilidades. Considera qué elección equilibra el riesgo de adivinar demasiado alto o demasiado bajo.'

    Q_message_origin = '¿De dónde provienen los mensajes que verás?'
    O_message_origin = ['Fueron generados automáticamente por el computador durante esta sesión',
                        'Fueron enviados por otros participantes actualmente en la sala',
                        'Fueron escritos por participantes del Jugador A que participaron en un experimento anterior',
                        'Fueron creados por el experimentador como ejemplos']
    A_message_origin = 'Fueron escritos por participantes del Jugador A que participaron en un experimento anterior'
    H_message_origin = 'Los mensajes que verás no fueron generados durante tu sesión. Piensa en quién los envió y cuándo fueron enviados.'

    Q_fixbelief_understanding = '¿Cuál afirmación es correcta sobre el Jugador A y el mensaje que observas?'
    O_fixbelief_understanding = [
        'Tu Jugador A es seleccionado de 4 Jugadores A que enviaron este mensaje, y si un Jugador A delegó al computador, ese Jugador A envió el verdadero número secreto',
        'Tu Jugador A cambia cada ronda, y delegar significa enviar un número aleatorio',
        'Tu Jugador A es seleccionado de todos los participantes del experimento anterior, y delegar significa enviar el número más alto',
        'Tu Jugador A es seleccionado de 4 Jugadores A que enviaron este mensaje, y delegar significa elegir cualquier número estratégicamente'
    ]
    A_fixbelief_understanding = 'Tu Jugador A es seleccionado de 4 Jugadores A que enviaron este mensaje, y si un Jugador A delegó al computador, ese Jugador A envió el verdadero número secreto'
    H_fixbelief_understanding = 'Recuerda: tu Jugador A proviene de un grupo de 4 Jugadores A que enviaron ese mensaje, y delegar significa que el computador envió el verdadero número secreto.'

    Q_nouncertainty_understanding = '¿Cuál afirmación es correcta sobre cómo se evalúa tu adivinanza en este tratamiento?'
    O_nouncertainty_understanding = [
        'Mi única adivinanza se compara con los 4 números secretos de los 4 Jugadores A del grupo, y mi desempeño en la ronda se calcula como el promedio de esas 4 comparaciones',
        'Después de adivinar, el computador selecciona aleatoriamente a uno de los 4 Jugadores A, y solo ese Jugador A determina mi pago',
        'Envío 4 adivinanzas separadas, una por cada Jugador A del grupo',
        'Mi adivinanza solo se compara con los Jugadores A que delegaron al computador'
    ]
    A_nouncertainty_understanding = 'Mi única adivinanza se compara con los 4 números secretos de los 4 Jugadores A del grupo, y mi desempeño en la ronda se calcula como el promedio de esas 4 comparaciones'
    H_nouncertainty_understanding = 'Recuerda: envías una sola adivinanza, se compara con los 4 números secretos del grupo, y tu desempeño en la ronda es el promedio de esas 4 comparaciones.'

    wrong_answer_message = 'No respondiste correctamente a esta pregunta. La siguiente pista puede ayudarte cuando intentes responder de nuevo:'
    correct_answer_message = 'Respondiste correctamente a esta pregunta. No necesitas cambiarla.'

    # Templates
    ReceiverReminder = 'N5_sender_receiver_game/templates/ReceiverReminder.html'
    SenderReminder = 'N5_sender_receiver_game/templates/SenderReminder.html'

class Subsession(BaseSubsession):
    pass


def get_sender_messages_csv_path(session):
    if session.config.get('treatment') == 'Belief':
        return __name__ + '/messages_for_receivers_belief.csv'
    if session.config.get('treatment') == 'NoUncertainty':
        return __name__ + '/messages_for_receivers_with_X_secrets.csv'
    if session.config.get('treatment') == 'FixBelief':
        return __name__ + '/messages_for_receivers_with_X.csv'
    return __name__ + '/messages_for_receivers.csv'


def get_bundle_secret_numbers_from_row(row, round_num):
    secret_numbers = []
    for sender_index in range(1, 5):
        key = f'secret_number_{sender_index}_R{round_num}'
        raw_value = row.get(key)
        if raw_value in [None, '']:
            continue
        secret_numbers.append(int(float(raw_value)))
    return secret_numbers


def get_bundle_secret_numbers(player: 'Player'):
    if not player.bundle_secret_numbers_json:
        return []
    try:
        return json.loads(player.bundle_secret_numbers_json)
    except json.JSONDecodeError:
        return []


def get_effective_receiver_guess(player: 'Player'):
    if player.receiver_guess == 0 and player.sender_message > 0:
        return float(player.sender_message)
    return float(player.receiver_guess)


def get_receiver_accuracy(secret_number, guess):
    return max(0.0, 1 - (1 / 36) * (secret_number - guess) ** 2)


def creating_session(subsession: Subsession):
    import csv

    round_num = subsession.round_number
    players = subsession.get_players()
    treatment = subsession.session.config.get('treatment', 'ExpertRep')

    # Set role via player.participant — same mechanism that successfully writes all other fields
    for player in players:
        player.treatment = treatment
        player.participant.role = 'Player B'
        player.participant.vars['role'] = 'Player B'
        player.participant.treatment = treatment
        player.participant.vars['treatment'] = treatment
        player.participant.vars['payoff_relevant_rounds'] = Constants.PREDEFINED_RECEIVER_ROUNDS.copy()

    csv_path = get_sender_messages_csv_path(subsession.session)

    with open(csv_path, encoding='utf-8-sig') as f:
        all_rows = list(csv.DictReader(f))
    code_row_map = {r['code']: r for r in all_rows}
    has_used_column = bool(all_rows) and 'used' in all_rows[0]

    if round_num == 1:
        # Round 1: assign a sender code to each participant from the CSV
        if has_used_column:
            available = [r['code'] for r in all_rows if str(r.get('used', '0')) == '0']
            if len(available) < len(players):
                # Not enough unused codes — refill from the full pool to avoid duplicates
                available = [r['code'] for r in all_rows]
        else:
            available = [r['code'] for r in all_rows]
        random.shuffle(available)

        used_codes = []
        for i, player in enumerate(players):
            code = available[i % len(available)]
            player.participant.assigned_sender_code = code
            used_codes.append(code)
            print(f'[creating_session R1] player id_in_subsession={player.id_in_subsession} -> code={code}')

        if has_used_column:
            # Mark codes as used only in CSVs that track reuse.
            for r in all_rows:
                if r['code'] in used_codes:
                    r['used'] = '1'
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
                writer.writeheader()
                writer.writerows(all_rows)

    # Write THIS round's player data (each round writes its own data)
    # In round 1 the participant field was just set above; in rounds 2+ it was set in round 1.
    for player in players:
        code = player.participant.assigned_sender_code
        print(f'[creating_session R{round_num}] player id={player.id_in_subsession} code={code}')
        if not code:
            continue
        row = code_row_map.get(code)
        if row is None:
            continue


        player.sender_code    = code
        player.secret_number  = int(float(row[f'secret_number_R{round_num}']))
        player.sender_message = int(float(row[f'sender_message_R{round_num}']))
        player.sender_choice  = int(float(row[f'sender_choice_R{round_num}']))
        player.x_count = int(float(row.get(f'X_R{round_num}', 0) or 0))
        if treatment == 'NoUncertainty':
            bundle_secret_numbers = get_bundle_secret_numbers_from_row(row, round_num)
            if not bundle_secret_numbers:
                bundle_secret_numbers = [player.secret_number]
            player.bundle_secret_numbers_json = json.dumps(bundle_secret_numbers)
        else:
            player.bundle_secret_numbers_json = json.dumps([])
        player.bundle_receiver_scores_json = json.dumps([])
        player.bundle_receiver_average_score = 0

        if player.sender_message == 0:
            player.sender_message_encoded = 'El Jugador A no envió un número'
        else:
            player.sender_message_encoded = str(player.sender_message)



class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField(initial='')

    decoding_answer = models.IntegerField(blank=True)  # Stores the answer for each task
    task_number = models.IntegerField(initial=1)  # Tracks the current task (1 to 10)
    correct_answers = models.IntegerField(initial=0)  # Tracks how many correct answers the player has given

    # Fields moved from Group — each player has their own independent data row
    secret_number = models.IntegerField(initial=4)
    sender_choice = models.IntegerField(initial=0)
    sender_message = models.IntegerField(initial=0)
    x_count = models.IntegerField(initial=0)
    bundle_secret_numbers_json = models.LongStringField(initial='[]')
    bundle_receiver_scores_json = models.LongStringField(initial='[]')
    bundle_receiver_average_score = models.FloatField(initial=0)
    sender_message_encoded = models.StringField(initial='')
    sender_code = models.StringField(initial='')
    receiver_guess = models.FloatField(min=0, max=7, initial=0)
    tutorial_message = models.IntegerField(initial=0)
    tutorial_x_count = models.IntegerField(initial=2)
    tutorial_message_encoded = models.StringField(initial='')
    math_solution = models.IntegerField(label=None, initial=0)
    sender_win_prob = models.FloatField(initial=0)
    receiver_win_prob = models.FloatField(initial=0)
    sender_wins = models.BooleanField(initial=False)
    receiver_wins = models.BooleanField(initial=False)
    honesty_rate = models.FloatField(initial=0)
    credulity_rate = models.FloatField(initial=0)
    guess_confirmed = models.BooleanField(initial=False)


    # Control question fields
    wrong_answer = models.IntegerField(initial = 1)
    wrong_answer_count = models.IntegerField(initial = 0)
    Q_task = models.StringField(label = Constants.Q_task, initial = 'na')
    Q_task_count = models.IntegerField(initial = 0)

    Q_payoff = models.StringField(initial = 'na')
    Q_payoff_count = models.IntegerField(initial = 0)
    Q_message_origin = models.StringField(label = Constants.Q_message_origin, initial = 'na')
    Q_message_origin_count = models.IntegerField(initial = 0)
    Q_fixbelief_understanding = models.StringField(label=Constants.Q_fixbelief_understanding, initial='na')
    Q_fixbelief_understanding_count = models.IntegerField(initial=0)
    Q_nouncertainty_understanding = models.StringField(label=Constants.Q_nouncertainty_understanding, initial='na')
    Q_nouncertainty_understanding_count = models.IntegerField(initial=0)
    Q_payoff_other = models.StringField(initial = 'na')
    Q_payoff_other_count = models.IntegerField(initial = 0)
    Q_independence = models.StringField(label = Constants.Q_independence, initial = 'na')
    Q_independence_count = models.IntegerField(initial = 0)
    Q_secret_number_generation = models.StringField(label = Constants.Q_secret_number_generation, initial = 'na')
    Q_secret_number_generation_count = models.IntegerField(initial = 0)
    Q_no_knowledge_guess = models.StringField(label = Constants.Q_no_knowledge_guess, initial = 'na')
    Q_no_knowledge_guess_count = models.IntegerField(initial = 0)


    is_sender_payoff_relevant = models.BooleanField(initial=False)
    is_receiver_payoff_relevant = models.BooleanField(initial=False)

    belief_honest_pct = models.IntegerField(min=0, max=100, initial=0)

    honesty_guess = models.IntegerField()
    honesty_certainty = models.IntegerField()
    credulity_guess = models.IntegerField()
    credulity_certainty = models.IntegerField()

    strategy_explanation = models.LongStringField(
        label="",
        blank=False
    )

# These functions assign choice options to questions and display them in a random order.
def Q_task_choices(player):
    if player.participant.treatment == 'Belief':
        L = Constants.O_task_Belief.copy()
    else:
        L = Constants.O_task.copy()
    random.shuffle(L)
    return L

def Q_payoff_choices(player):
    # Everyone is Player B in this 1-player simulation
    L = Constants.O_payoff_PB.copy()
    random.shuffle(L)
    return L

def Q_payoff_other_choices(player):
    # Everyone is Player B in this 1-player simulation
    L = Constants.O_payoff_other_PB.copy()
    random.shuffle(L)
    return L

def Q_independence_choices(player):
    L = Constants.O_independence.copy()
    random.shuffle(L)
    return L

def Q_secret_number_generation_choices(player):
    L = Constants.O_secret_number_generation.copy()
    random.shuffle(L)
    return L

def Q_no_knowledge_guess_choices(player):
    L = Constants.O_no_knowledge_guess.copy()
    random.shuffle(L)
    return L

def Q_message_origin_choices(player):
    L = Constants.O_message_origin.copy()
    random.shuffle(L)
    return L

def Q_fixbelief_understanding_choices(player):
    L = Constants.O_fixbelief_understanding.copy()
    random.shuffle(L)
    return L

def Q_nouncertainty_understanding_choices(player):
    L = Constants.O_nouncertainty_understanding.copy()
    random.shuffle(L)
    return L

def check_cq_answers(answer, solution, count):
    if answer != solution:
        return 1, count + 1
    else:
        return 0, count


def set_payoffs(player: Player):
    # Apply the decoding bonus only in the first round
    if player.round_number == 1:
        player.payoff = player.correct_answers * Constants.PIECE_RATE_DECODE

    effective_guess = get_effective_receiver_guess(player)

    if player.sender_message == 0:
        sender_prob = 0
    else:
        sender_prob = (effective_guess - 1) / 6 if effective_guess > 0 else 0

    if player.sender_message == 0 or effective_guess == 0:
        bundle_scores = []
        receiver_prob = 0
    elif player.participant.treatment == 'NoUncertainty':
        bundle_secret_numbers = get_bundle_secret_numbers(player) or [player.secret_number]
        bundle_scores = [get_receiver_accuracy(secret_number, effective_guess) for secret_number in bundle_secret_numbers]
        receiver_prob = sum(bundle_scores) / len(bundle_scores)
    else:
        bundle_scores = [get_receiver_accuracy(player.secret_number, effective_guess)]
        receiver_prob = bundle_scores[0]

    sender_wins = random.random() < sender_prob
    receiver_wins = random.random() < receiver_prob

    player.sender_win_prob = sender_prob
    player.receiver_win_prob = receiver_prob
    player.bundle_receiver_scores_json = json.dumps(bundle_scores)
    player.bundle_receiver_average_score = receiver_prob
    player.sender_wins = sender_wins
    player.receiver_wins = receiver_wins

    if player.receiver_guess == 0:
        player.payoff += Currency(0)
    else:
        player.payoff += Constants.BONUS_AMOUNT if receiver_wins else Currency(0)

    print(f"Round {player.round_number}:")
    print(f"  - Secret number: {player.secret_number}")
    if player.participant.treatment == 'NoUncertainty':
        print(f"  - Bundle secret numbers: {get_bundle_secret_numbers(player)}")
    print(f"  - Sender's message: {player.sender_message}")
    print(f"  - Receiver's guess: {player.receiver_guess}")
    print(f"  - Sender probability: {sender_prob}, Receiver probability: {receiver_prob}")
    print(f"  - Sender wins: {sender_wins}, Receiver wins: {receiver_wins}")
    print(f"  - Player payoff: {player.payoff}")


# pages.py

class PreviousExperimentInfo(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class instructions1(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass

class instructions2(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}

class TimeLimit(Page):
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
    
class Decode(Page):
    @staticmethod
    def is_displayed(player: Player):
        return False


class Round_number(Page):
    timeout_seconds = 3
    timer_text = 'La siguiente ronda comienza en:'


class role_info(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}

class ControlQuestions(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.wrong_answer > 0
    
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['Q_task', 'Q_payoff', 'Q_payoff_other', 'Q_independence', 'Q_no_knowledge_guess', 'Q_secret_number_generation', 'Q_message_origin']
        if player.participant.treatment == 'FixBelief':
            fields.append('Q_fixbelief_understanding')
        if player.participant.treatment == 'NoUncertainty':
            fields.append('Q_nouncertainty_understanding')
        return fields

    @staticmethod
    def before_next_page(player,timeout_happened):
        player.wrong_answer = 0
        # Everyone is Player B — use treatment-specific correct answer for Q_task
        task_answer = Constants.A_task_PB_Belief if player.participant.treatment == 'Belief' else Constants.A_task_PB
        a, player.Q_task_count = check_cq_answers(player.Q_task, task_answer, player.Q_task_count)
        b, player.Q_payoff_count = check_cq_answers(player.Q_payoff, Constants.A_payoff_PB, player.Q_payoff_count)
        c, player.Q_payoff_other_count = check_cq_answers(player.Q_payoff_other, Constants.A_payoff_other_PB, player.Q_payoff_other_count)
        d, player.Q_independence_count = check_cq_answers(player.Q_independence, Constants.A_independence, player.Q_independence_count)
        e, player.Q_no_knowledge_guess_count = check_cq_answers(player.Q_no_knowledge_guess, Constants.A_no_knowledge_guess, player.Q_no_knowledge_guess_count)
        f, player.Q_secret_number_generation_count = check_cq_answers(player.Q_secret_number_generation, Constants.A_secret_number_generation, player.Q_secret_number_generation_count)
        g, player.Q_message_origin_count = check_cq_answers(player.Q_message_origin, Constants.A_message_origin, player.Q_message_origin_count)
        if player.participant.treatment == 'FixBelief':
            h, player.Q_fixbelief_understanding_count = check_cq_answers(
                player.Q_fixbelief_understanding,
                Constants.A_fixbelief_understanding,
                player.Q_fixbelief_understanding_count,
            )
        else:
            h = 0

        if player.participant.treatment == 'NoUncertainty':
            i, player.Q_nouncertainty_understanding_count = check_cq_answers(
                player.Q_nouncertainty_understanding,
                Constants.A_nouncertainty_understanding,
                player.Q_nouncertainty_understanding_count,
            )
        else:
            i = 0


        player.wrong_answer = max(a,b,c,d,e,f,g,h,i)
        player.wrong_answer_count += player.wrong_answer


class start_page(Page):
    # Only show in the first round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    
    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}
    
class SenderTutorial(Page):
    # Legacy Player A page — never displayed in 1-player simulation
    @staticmethod
    def is_displayed(player: Player):
        return False


class SenderMessage(Page):
    # Legacy Player A page — never displayed in 1-player simulation
    @staticmethod
    def is_displayed(player: Player):
        return False

class TutorialIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def vars_for_template(player: Player):
        return {"round_number": player.round_number}
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        tutorial_message = 6
        player.tutorial_message = tutorial_message
        player.tutorial_message_encoded = str(tutorial_message)
        player.tutorial_x_count = 2

class ReceiverTutorial(Page):
    form_model = 'player'
    @staticmethod
    def get_form_fields(player: Player):
        return ['receiver_guess']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.treatment not in ['Belief', 'FixBelief', 'NoUncertainty']

    @staticmethod
    def vars_for_template(player: Player):
        current_round = player.round_number
        is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        return dict(
            is_sender_payoff_relevant=is_sender_payoff_relevant
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            encoded_message=player.tutorial_message_encoded,
            sender_message=player.tutorial_message,
            x_count=player.tutorial_x_count,
            treatment=player.participant.treatment,
            max_guess=7,
            min_guess=1
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Reset tutorial guess — doesn't affect game payoffs
        player.receiver_guess = 0


class FixBeliefTutorial(Page):
    """Interactive tutorial for FixBelief treatment with X-based explanation."""
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return ['receiver_guess']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.treatment == 'FixBelief'

    @staticmethod
    def vars_for_template(player: Player):
        current_round = player.round_number
        is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        return dict(
            is_sender_payoff_relevant=is_sender_payoff_relevant,
            x_count = player.tutorial_x_count,
            strategic_sender_count = max(0, 4 - player.tutorial_x_count)
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            encoded_message=player.tutorial_message_encoded,
            sender_message=player.tutorial_message,
            x_count=player.tutorial_x_count,
            treatment=player.participant.treatment,
            max_guess=7,
            min_guess=1
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Reset tutorial guess — doesn't affect game payoffs
        player.receiver_guess = 0


class NoUncertaintyTutorial(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return ['receiver_guess']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.treatment == 'NoUncertainty'

    @staticmethod
    def vars_for_template(player: Player):
        current_round = player.round_number
        is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        return dict(
            is_sender_payoff_relevant=is_sender_payoff_relevant,
            x_count = player.tutorial_x_count,
            strategic_sender_count = max(0, 4 - player.tutorial_x_count)
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            encoded_message=player.tutorial_message_encoded,
            sender_message=player.tutorial_message,
            x_count=player.tutorial_x_count,
            treatment=player.participant.treatment,
            max_guess=7,
            min_guess=1
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.receiver_guess = 0


class BeliefTransition(Page):
    """Shown only to Belief participants after the historical instructions,
    making clear they will report beliefs rather than direct guesses."""
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.treatment == 'Belief'


class BeliefTutorial(Page):
    """Interactive tutorial for the Belief treatment guessing interface."""
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return ['belief_honest_pct']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.treatment == 'Belief'

    @staticmethod
    def js_vars(player: Player):
        return dict(
            encoded_message=player.tutorial_message_encoded,
            sender_message=player.tutorial_message,
            treatment=player.participant.treatment,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Reset tutorial values — don't affect payoffs
        player.belief_honest_pct = 0
        player.receiver_guess = 0


class ReceiverGuess(Page):
    form_model = 'player'
    @staticmethod
    def get_form_fields(player: Player):
        fields = ['receiver_guess', 'guess_confirmed']
        if player.participant.treatment == 'Belief':
            fields.append('belief_honest_pct')
        return fields

    @staticmethod
    def is_displayed(player):
        return True

    timer_text = '⏳ Tiempo restante:'

    @staticmethod
    def get_timeout_seconds(player: Player):
        deadline_key = f'receiver_guess_deadline_round_{player.round_number}'
        deadline = player.participant.vars.get(deadline_key)

        if deadline is None:
            deadline = time.time() + Constants.TIME_PER_ROUND
            player.participant.vars[deadline_key] = deadline

        return max(0, deadline - time.time())

    @staticmethod
    def vars_for_template(player: Player):
        current_round = player.round_number
        is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        return dict(
            sender_message=player.sender_message,
            is_sender_payoff_relevant=is_sender_payoff_relevant,
            x_count=player.x_count,
            strategic_sender_count=max(0, 4 - player.x_count),
            bundle_sender_count=4,
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            sender_message=player.sender_message,
            encoded_message=player.sender_message_encoded,
            treatment=player.participant.treatment,
            x_count=player.x_count,
            max_guess=7,
            min_guess=1
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        deadline_key = f'receiver_guess_deadline_round_{player.round_number}'
        player.participant.vars.pop(deadline_key, None)

        if timeout_happened and not player.guess_confirmed:
            player.receiver_guess = 0

        # For Belief treatment, compute the optimal guess from stated belief
        if player.participant.treatment == 'Belief':
            p = player.belief_honest_pct / 100.0
            msg = player.sender_message if player.sender_message > 0 else 4
            optimal = p * msg + (1 - p) * 4.0
            player.receiver_guess = round(max(1.0, min(7.0, optimal)), 1)

        current_round = player.round_number
        player.is_sender_payoff_relevant = current_round in Constants.PREDEFINED_SENDER_ROUNDS
        player.is_receiver_payoff_relevant = current_round in Constants.PREDEFINED_RECEIVER_ROUNDS

        set_payoffs(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        bundle_secret_numbers = get_bundle_secret_numbers(player)
        try:
            bundle_receiver_scores = json.loads(player.bundle_receiver_scores_json)
        except json.JSONDecodeError:
            bundle_receiver_scores = []
        return {
            'secret_number': player.secret_number,
            'sender_message': player.sender_message,
            'receiver_guess': player.receiver_guess,
            'evaluated_guess': get_effective_receiver_guess(player),
            'player_payoff': player.payoff,
            'correct_answers': player.correct_answers,
            'extra_earnings': player.correct_answers * Constants.PIECE_RATE_DECODE,
            'piece_rate_decode': Constants.PIECE_RATE_DECODE,
            'belief_honest_pct': player.belief_honest_pct,
            'x_count': player.x_count,
            'strategic_sender_count': max(0, 4 - player.x_count),
            'bundle_sender_count': len(bundle_secret_numbers),
            'bundle_secret_numbers_display': ', '.join(str(number) for number in bundle_secret_numbers),
            'bundle_average_secret_number': sum(bundle_secret_numbers) / len(bundle_secret_numbers) if bundle_secret_numbers else 'N/A',
            'bundle_receiver_scores_display': ', '.join(f'{score * 100:.1f}%' for score in bundle_receiver_scores),
            'treatment': player.participant.treatment,
        }

    timeout_seconds = Constants.FEEDBACK_TIME
    timer_text = '⏳ Tiempo restante:'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        current_round = player.round_number
        is_receiver_payoff_relevant = current_round in Constants.PREDEFINED_RECEIVER_ROUNDS

        if not is_receiver_payoff_relevant:
            player.payoff -= Constants.BONUS_AMOUNT if player.receiver_wins else Currency(0)

        player.payoff = max(player.payoff, player.correct_answers * Constants.PIECE_RATE_DECODE)

        print(f"Round {current_round}: Player Payoff = {player.payoff}")
        print(f"Total Payoff (Cumulative): {player.participant.payoff}")

class HonestyGuess(Page):
    form_model = 'player'
    form_fields = ['honesty_guess']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

class HonestyCertainty(Page):
    form_model = 'player'
    form_fields = ['honesty_certainty']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        guess = player.honesty_guess
        lower_bound = max(0, guess - 1)
        upper_bound = min(100, guess + 1)
        return dict(
            lower_bound=lower_bound,
            upper_bound=upper_bound
        )

class FollowingGuess(Page):
    form_model = 'player'
    form_fields = ['credulity_guess']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Calculate honesty and credulity rates from this player's own rounds
        msg = 0
        hnum = 0
        cnum = 0
        hmsg = 0
        for r in range(1, Constants.num_rounds + 1):
            p_round = player.in_round(r)
            msg += 1
            if p_round.sender_choice == 8:
                hnum += 1
            sender_message = p_round.sender_message
            if sender_message == 7:
                hmsg += 1
                if p_round.receiver_guess >= 6.8:
                    cnum += 1

        player.honesty_rate = hnum / msg if msg > 0 else 0
        player.credulity_rate = cnum / hmsg if hmsg > 0 else 0

        honesty_guess_prob = 1 - (player.honesty_rate - player.honesty_guess/100) ** 2
        wins = random.random() < honesty_guess_prob
        player.payoff += Constants.HONESTY_GUESS_BONUS if wins else Currency(0)

        credulity_guess_prob = 1 - (player.credulity_rate - player.credulity_guess/100) ** 2
        wins = random.random() < credulity_guess_prob
        player.payoff += Constants.CREDULITY_GUESS_BONUS if wins else Currency(0)

class FollowingCertainty(Page):
    form_model = 'player'
    form_fields = ['credulity_certainty']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        guess = player.credulity_guess
        lower_bound = max(0, guess - 1)
        upper_bound = min(100, guess + 1)
        return dict(
            lower_bound=lower_bound,
            upper_bound=upper_bound
        )

class ExplanationTask(Page):
    form_model = 'player'
    form_fields = ['strategy_explanation']

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

page_sequence = [
    PreviousExperimentInfo, instructions1, instructions2, TimeLimit, Decode, instructions4,
    role_info,
    ControlQuestions, ControlQuestions, ControlQuestions, ControlQuestions, ControlQuestions,
    TutorialIntro, ReceiverTutorial, FixBeliefTutorial, NoUncertaintyTutorial, BeliefTutorial, start_page,
    Round_number, ReceiverGuess, Results,
    HonestyGuess, HonestyCertainty, FollowingGuess, FollowingCertainty, ExplanationTask
]

