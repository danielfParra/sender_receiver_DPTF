from otree.api import Bot, Submission
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield PreviousExperimentInfo
            yield instructions1
            yield instructions2
            yield TimeLimit
            yield instructions3
            yield instructions4
            yield role_info

            cq_data = {
                'Q_task': Constants.A_task_PB_Belief if self.player.participant.treatment == 'Belief' else Constants.A_task_PB,
                'Q_payoff': Constants.A_payoff_PB,
                'Q_payoff_other': Constants.A_payoff_other_PB,
                'Q_independence': Constants.A_independence,
                'Q_secret_number_generation': Constants.A_secret_number_generation,
                'Q_no_knowledge_guess': Constants.A_no_knowledge_guess,
                'Q_message_origin': Constants.A_message_origin,
            }
            if self.player.participant.treatment == 'FixBelief':
                cq_data['Q_fixbelief_understanding'] = Constants.A_fixbelief_understanding
            if self.player.participant.treatment == 'NoUncertainty':
                cq_data['Q_nouncertainty_understanding'] = Constants.A_nouncertainty_understanding
            yield ControlQuestions, cq_data

            yield TutorialIntro
            if self.player.participant.treatment == 'Belief':
                yield BeliefTutorial, {'belief_honest_pct': 50}
            elif self.player.participant.treatment == 'FixBelief':
                yield FixBeliefTutorial, {'receiver_guess': 4}
            elif self.player.participant.treatment == 'NoUncertainty':
                yield NoUncertaintyTutorial, {'receiver_guess': 4}
            else:
                yield ReceiverTutorial, {'receiver_guess': 4}

            yield start_page

        yield Submission(Round_number, check_html=False)

        guess_data = {
            'receiver_guess': 4,
            'guess_confirmed': True,
        }
        if self.player.participant.treatment == 'Belief':
            guess_data['belief_honest_pct'] = 50

        yield Submission(ReceiverGuess, guess_data, check_html=False)
        yield Submission(Results, check_html=False)

        if self.player.round_number == Constants.num_rounds:
            yield HonestyGuess, {'honesty_guess': 50}
            yield HonestyCertainty, {'honesty_certainty': 50}
            yield FollowingGuess, {'credulity_guess': 50}
            yield FollowingCertainty, {'credulity_certainty': 50}
            yield ExplanationTask, {'strategy_explanation': 'Segui una estrategia simple basada en el mensaje y las reglas del tratamiento.'}

