import math

import numpy as np

from src.wordle import Wordle


def additional_information(answers_mask, guess, guess_index_map, guess_matrix):
    # First find all the possible guess patterns that could result from this guess
    guess_patterns = guess_matrix[guess_index_map[guess]][answers_mask]
    pattern_counts = np.unique(guess_patterns, return_counts=True)

    def information(pattern, count):
        space_size_before_guess = np.count_nonzero(answers_mask)
        space_size_after_guess = np.count_nonzero(np.logical_and(answers_mask, pattern == guess_matrix[guess_index_map[guess]]))
        return -math.log2(space_size_after_guess / space_size_before_guess) * count / guess_patterns.shape[0]

    # For each guess pattern compute the amount of information in bits it gives
    vectorized_information_func = np.frompyfunc(information, 2, 1)
    return vectorized_information_func(pattern_counts[0], pattern_counts[1]).sum()


class BaseSolver:
    def __init__(self, wordle: Wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask):
        self.possible_guesses = possible_guesses
        self.possible_answers = possible_answers
        self.answers_mask = np.array([True for _ in range(possible_answers.shape[0])], dtype=bool)
        self.guess_matrix = guess_matrix
        self.guess_index_map = guess_index_map
        self.answer_index_map = answer_index_map
        self.answers_in_guesses_mask = answers_in_guesses_mask
        self.wordle = wordle

        def print_top_10():
            print("Some suggestions are:")
            suggestions = self.top_10_suggestions()
            additional_information(self.answers_mask, suggestions[0], self.guess_index_map, self.guess_matrix)
            for i in range(len(suggestions)):
                print(suggestions[i] + " on average yields " + str(round(additional_information(self.answers_mask, suggestions[i], self.guess_index_map, self.guess_matrix), 2)) + " bits of information")
        self.wordle.pre_move_print = print_top_10
        self.guess_n = 0

    def update_possible_answers(self):
        while self.guess_n < self.wordle.guess_n:
            self.answers_mask[np.logical_not(self.wordle.guess_patterns[self.guess_n] == self.guess_matrix[self.guess_index_map[self.wordle.guesses[self.guess_n]]])] = False
            self.guess_n += 1

    def top_10_suggestions(self):
        self.update_possible_answers()
        possible_answer_count = self.answers_mask.sum()
        return np.random.choice(self.possible_answers[self.answers_mask], 10 if possible_answer_count > 10 else possible_answer_count, replace=False)
