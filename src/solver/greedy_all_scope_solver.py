import numpy as np

from src.solver.base_solver import BaseSolver, additional_information
from src.wordle import Wordle


class GreedyAllScopeSolver(BaseSolver):
    def __init__(self, wordle: Wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask):
        super().__init__(wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask)

    def top_10_suggestions(self):
        self.update_possible_answers()

        if self.wordle.guess_n == 0:
            return np.array(["soare"])

        def information(guess):
            return additional_information(self.answers_mask, guess, self.guess_index_map, self.guess_matrix)

        potential_guesses_information = np.vectorize(information)(self.possible_guesses)
        unique_information = np.unique(potential_guesses_information)

        answer_set_information = potential_guesses_information[self.answers_in_guesses_mask]

        # If a guess is in the answer set and gives as much information as something that isn't in the answer set, don't consider the word not in the answer set
        def remove_redundant_information(information):
            if information in answer_set_information:
                potential_guesses_information[np.logical_and(np.logical_not(self.answers_in_guesses_mask), potential_guesses_information == information)] = 0
            if information in answer_set_information[self.answers_mask]:
                answer_set_information[np.logical_and(np.logical_not(self.answers_mask), answer_set_information == information)] = 0
                potential_guesses_information[self.answers_in_guesses_mask] = answer_set_information

        np.vectorize(remove_redundant_information)(unique_information)

        if np.max(unique_information) == 0:
            return self.possible_answers[self.answers_mask]

        potential_answers = self.possible_guesses[potential_guesses_information.argsort()[::-1]]
        sorted_information = potential_guesses_information[potential_guesses_information.argsort()[::-1]]
        if np.max(sorted_information) > 0:
            potential_answers = potential_answers[sorted_information != 0]
        return potential_answers if potential_answers.shape[0] < 10 else potential_answers[:10]
