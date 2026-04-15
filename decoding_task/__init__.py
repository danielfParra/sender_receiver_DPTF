from otree.api import *
import pandas as pd

class Constants(BaseConstants):
    name_in_url = 'decoding_task'
    players_per_group = None  # No grouping required
    PIECE_RATE_DECODE = Currency(500)  # New constant for the piece rate per correct answer
    num_rounds = 1  # Only run the decoding task once
    TIME_PER_TASK = 20
    NUM_TASKS = 6

    # Load csv with decoding tasks (answer and encoding)
    import pandas as pd
    file = '_static/data/encoding_task.csv'
    df_decoding_tasks = pd.read_csv(file)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    decoding_answer = models.IntegerField(blank=True)  # Stores the answer for each task
    task_number = models.IntegerField(initial=1)  # Tracks the current task (1 to 20)
    correct_answers = models.IntegerField(initial=0)  # Tracks how many correct answers the player has given


# Pages
class DecodingInstructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1  # Show only in the first round

    @staticmethod
    def vars_for_template(player: Player):
        return {
            "time_per_task": Constants.TIME_PER_TASK,
            "total_tasks": Constants.NUM_TASKS,
        }


class DecodingStart(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class DecodingTask(Page):
    form_model = 'player'
    form_fields = ['decoding_answer', 'correct_answers']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        import json
        tasks = Constants.df_decoding_tasks.to_dict(orient='records')
        current_task_index = player.task_number - 1
        current_task = tasks[current_task_index]

        return {
            'task_number': player.task_number,
            'total_tasks': Constants.NUM_TASKS,
            'encoding': current_task['encoding'],
            'tasks_json': json.dumps(tasks),
            'time_per_task': Constants.TIME_PER_TASK,
            'correct_answers': player.correct_answers,
        }


class DecodingTaskResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'total_score': player.correct_answers,
            'total_tasks': Constants.NUM_TASKS,
        }

    timeout_seconds = 30
    timer_text = '⏳ Tiempo restante para continuar:'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Store correct answers in participant.vars for use in other apps
        player.participant.vars['correct_answers'] = player.correct_answers

class MyWaitPage(WaitPage):
    pass


page_sequence = [DecodingInstructions, DecodingStart, DecodingTask, DecodingTaskResults, MyWaitPage]


# Bot
class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield DecodingInstructions()
            yield DecodingStart()

            # Load task data
            df_decoding_tasks = pd.read_csv('_static/data/encoding_task.csv')
            tasks = df_decoding_tasks.to_dict(orient='records')

            # Iterate through tasks, simulating correct answers
            for task in tasks[:Constants.NUM_TASKS]:  # Ensure only NUM_TASKS are attempted
                correct_answer = task['answer']  # Assuming 'answer' column exists in CSV
                yield Submission(DecodingTask, {'decoding_answer': correct_answer})

            # Final results page
            yield DecodingTaskResults()
