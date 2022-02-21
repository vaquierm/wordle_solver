import numpy as np

from src.solver.base_solver import BaseSolver, additional_information
from src.wordle import Wordle


class GreedyAnswerScopeSolver(BaseSolver):
    def __init__(self, wordle: Wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask):
        super().__init__(wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask)

    def top_10_suggestions(self):
        self.update_possible_answers()

        if self.wordle.guess_n == 0:
            return np.array(["raise"])

        def information(guess):
            return additional_information(self.answers_mask, guess, self.guess_index_map, self.guess_matrix)

        potential_answers = self.possible_answers[self.answers_mask]
        potential_answers_information = np.vectorize(information)(potential_answers)

        potential_answers = potential_answers[potential_answers_information.argsort()[::-1]]
        return potential_answers if potential_answers.shape[0] < 10 else potential_answers[:10]
