import math

import numpy as np

from src.solver.base_solver import additional_information
from src.solver.greedy_all_scope_solver import GreedyAllScopeSolver
from src.wordle import Wordle


class GreedyDeepSolver(GreedyAllScopeSolver):
    def __init__(self, wordle: Wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask):
        super().__init__(wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask)
        self.temp_best_non_answer_guess_index = -1

    def average_score(self, guess, guess_mask, answer_mask, layer, current_min_average_score):
        # Check if there are only a few answers left and return
        answers_left = answer_mask.sum()
        if answers_left == 1:
            return 1.0
        if answers_left == 2:
            return 1.5

        # Find all possible guess patterns that could result from this guess
        possible_patterns = self.guess_matrix[self.guess_index_map[guess]][answer_mask]

        # Find the frequency of each possible guess pattern
        pattern_counts = np.unique(possible_patterns, return_counts=True)

        # Temp variables
        next_answer_mask = np.copy(answer_mask)
        next_guess_mask = np.copy(guess_mask)

        average_score = 0
        if layer == 0:
            print("Guess: " + guess)
            print("Pattern count: " + str(len(pattern_counts[0])))
        for i in range(len(pattern_counts[0])):
            pattern = pattern_counts[0][i]
            count = pattern_counts[1][i]

            # If the pattern in fully correct, we only have to make one guess
            if pattern == 33333:
                average_score += 1
                continue

            # Get an updated answers mask
            np.copyto(next_answer_mask, answer_mask)
            next_answer_mask[self.guess_matrix[self.guess_index_map[guess]] != pattern] = False

            # Get the top guesses
            np.copyto(next_guess_mask, guess_mask)
            next_guesses = self.get_top_guess_suggestions(next_guess_mask, next_answer_mask)
            best_score_for_pattern = math.inf
            for guess_index in range(next_guesses.shape[0]):
                score_for_pattern_for_guess = 1 + self.average_score(next_guesses[guess_index], next_guess_mask, next_answer_mask, layer + 1, best_score_for_pattern - 1)
                if best_score_for_pattern > score_for_pattern_for_guess:
                    best_score_for_pattern = score_for_pattern_for_guess
                if best_score_for_pattern == 2:
                    # this should mean that we no longer want to explore guesses that are not in the answer set
                    break

            # Add the the average score of this guess
            average_score += count * best_score_for_pattern / possible_patterns.shape[0]

            if layer == 0 and average_score > current_min_average_score:
                print("No point to continue, saved " + str(len(pattern_counts[0]) - i) + " iterations out of " + str(len(pattern_counts[0])))
                return average_score

        return average_score

    def get_top_guess_suggestions(self, guesses_mask, answers_mask):
        if np.sum(answers_mask) == 1:
            return self.possible_answers[answers_mask]

        info_needed_to_narrow_to_one = -math.log2(1 / np.sum(answers_mask))
        self.temp_best_non_answer_guess_index = -1
        def information(guess):
            if self.temp_best_non_answer_guess_index == -1:
                guess_info = additional_information(answers_mask, guess, self.guess_index_map, self.guess_matrix)
                # Cou;d also be a gueess in the answer set that can no longer be the answer
                if info_needed_to_narrow_to_one - guess_info < 0.000001 and (guess not in self.answer_index_map or guess not in self.possible_answers[answers_mask]):
                    self.temp_best_non_answer_guess_index = self.guess_index_map[guess]
                return guess_info
            else:
                if guess in self.answer_index_map:
                    return additional_information(answers_mask, guess, self.guess_index_map, self.guess_matrix)
                else:
                    return 0

        potential_guesses_information = np.zeros(self.answers_in_guesses_mask.shape[0])
        potential_guesses_information[guesses_mask] = np.vectorize(information)(self.possible_guesses[guesses_mask])

        # Update the mask to know which guesses are no longer considered to give any useful information
        if self.temp_best_non_answer_guess_index != -1:
            # Remove the guesses that are not the answer that gives as much info as another
            potential_guesses_information[np.logical_not(self.answers_in_guesses_mask)] = 0

            # Remove the guesses that are in the answer set but can no longer be the answer
            answers_information = potential_guesses_information[self.answers_in_guesses_mask]
            answers_information[np.logical_not(answers_mask)] = 0
            potential_guesses_information[self.answers_in_guesses_mask] = answers_information

            potential_guesses_information[self.temp_best_non_answer_guess_index] = info_needed_to_narrow_to_one

        guesses_mask[potential_guesses_information == 0] = False

        max_info_indexes = np.argpartition(potential_guesses_information, -10)[-10:]
        top_guesses = self.possible_guesses[max_info_indexes]
        return top_guesses[potential_guesses_information[max_info_indexes] != 0]

    def top_N_suggestions(self, n: int):
        self.update_possible_answers()
        if self.wordle.guess_n == 0:
            return np.array(["soare"])
        elif self.wordle.guess_n == 1:
            return np.array(["clint"])

        top_guesses_suggestions = self.get_top_guess_suggestions(self.guesses_mask, self.answers_mask)

        average_scores = np.array([np.inf for _ in range(top_guesses_suggestions.shape[0])])
        for i in range(top_guesses_suggestions.shape[0]):
            # Make it so that when you get the answer your information is higher than if you narrow it down to 1
            # Don't compute the information if there is only one answer
            # If the information you get is enough to narrow down to 0 stop
            # If the first score is 2 there is no point checking another word not in the answer set. make a smarter chosing of words
            # Need a better priority than just checking the n most ifo words especially if there is no filtering for words in the answer set doing better
            average_scores[i] = self.average_score(top_guesses_suggestions[i], self.guesses_mask, self.answers_mask, 0, average_scores.min())
            print(top_guesses_suggestions[i] + ": " + str(average_scores[i]))

        return_count = average_scores.shape[0] if average_scores.shape[0] < n else n
        return top_guesses_suggestions[np.argsort(average_scores)][:return_count]
