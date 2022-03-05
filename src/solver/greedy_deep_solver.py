import math

import numpy as np
import json
import pickle

from src.solver.base_solver import additional_information
from src.solver.greedy_all_scope_solver import GreedyAllScopeSolver
from src.wordle import Wordle


class GreedyDeepSolver(GreedyAllScopeSolver):
    def __init__(self, wordle: Wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask, deep_decision_tree):
        super().__init__(wordle, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask)
        self.temp_best_non_answer_guess_index = -1
        self.deep_decision_tree = deep_decision_tree if deep_decision_tree is not None else {}

    def average_and_worst_score(self, guess, guess_mask, answer_mask, layer, current_min_average_score, deep_decision_nodes):
        # Check if there are only a few answers left and return
        answers_left = answer_mask.sum()
        if answers_left == 1 and guess in self.possible_answers[answer_mask]:
            return 1.0, 1.0
        if answers_left == 2 and guess in self.possible_answers[answer_mask]:
            return 1.5, 2.0

        if guess in deep_decision_nodes:
            return deep_decision_nodes[guess]["average_score"], deep_decision_nodes[guess]["worst_case_avg_score"]

        # Find all possible guess patterns that could result from this guess
        possible_patterns = self.guess_matrix[self.guess_index_map[guess]][answer_mask]

        # Find the frequency of each possible guess pattern
        pattern_counts = np.unique(possible_patterns, return_counts=True)

        # Temp variables
        next_answer_mask = np.copy(answer_mask)
        next_guess_mask = np.copy(guess_mask)

        average_score = 0
        worst_score = 0
        worst_pattern_count = 0
        children = {}
        for i in range(len(pattern_counts[0])):
            pattern = pattern_counts[0][i]
            count = pattern_counts[1][i]

            children_for_pattern = {}
            children[pattern] = children_for_pattern

            # If the pattern in fully correct, we only have to make one guess
            if pattern == 33333:
                average_score += 1 * count / possible_patterns.shape[0]
                if worst_score < 1:
                    worst_score = 1
                    worst_pattern_count = count
                continue

            # Get an updated answers mask
            np.copyto(next_answer_mask, answer_mask)
            next_answer_mask[self.guess_matrix[self.guess_index_map[guess]] != pattern] = False

            # Get the top guesses
            np.copyto(next_guess_mask, guess_mask)
            next_guesses = self.get_top_guess_suggestions(next_guess_mask, next_answer_mask)

            best_score_for_pattern = math.inf
            for guess_index in range(next_guesses.shape[0]):
                score_for_pattern_for_guess, _ = self.average_and_worst_score(next_guesses[guess_index], next_guess_mask, next_answer_mask, layer + 1, best_score_for_pattern - 1, children_for_pattern)
                score_for_pattern_for_guess += 1

                if best_score_for_pattern > score_for_pattern_for_guess:
                    best_score_for_pattern = score_for_pattern_for_guess

            # Add the the average score of this guess
            average_score += count * best_score_for_pattern / possible_patterns.shape[0]

            # Check if this pattern could lead to bad results
            if worst_score < best_score_for_pattern:
                worst_score = best_score_for_pattern
                worst_pattern_count = count

        if answers_left > 10:
            deep_decision_nodes[guess] = deep_decision_node(average_score, worst_score, worst_pattern_count / possible_patterns.shape[0], pattern_counts[0].shape[0], children)

        return average_score, worst_score

    def get_top_guess_suggestions(self, guesses_mask, answers_mask):
        answers_left = np.sum(answers_mask)
        if answers_left == 1 or answers_left == 2:
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

        max_info_indexes = np.argpartition(potential_guesses_information, -20)[-20:]
        top_guesses = self.possible_guesses[max_info_indexes]
        return top_guesses[potential_guesses_information[max_info_indexes] != 0]

    def get_current_decision_tree(self):
        decision_tree = self.deep_decision_tree
        for i in range(self.wordle.guess_n):
            if self.wordle.guesses[i] not in decision_tree:
                decision_tree[self.wordle.guesses[i]] = {"children": {}}
                decision_tree[self.wordle.guesses[i]]["children"][self.wordle.guess_patterns[i]] = {}
            decision_tree = decision_tree[self.wordle.guesses[i]]["children"][self.wordle.guess_patterns[i]]
        return decision_tree

    def top_N_suggestions(self, n: int):
        self.update_possible_answers()

        decision_tree = self.get_current_decision_tree()

        if len(decision_tree.keys()) == 0:
            top_guesses_suggestions = self.get_top_guess_suggestions(self.guesses_mask, self.answers_mask)
        else:
            # Get keys from tree dict
            top_guesses_suggestions = decision_tree.keys()

        average_scores = np.array([np.inf for _ in range(top_guesses_suggestions.shape[0])])
        worst_scores = np.array([np.inf for _ in range(top_guesses_suggestions.shape[0])])
        for i in range(top_guesses_suggestions.shape[0]):
            average_scores[i], worst_scores[i] = self.average_and_worst_score(top_guesses_suggestions[i], self.guesses_mask, self.answers_mask, self.wordle.guess_n, average_scores.min(), decision_tree)

        return_count = average_scores.shape[0] if average_scores.shape[0] < n else n

        return top_guesses_suggestions[np.argsort(average_scores)][:return_count]


def deep_decision_node(average_score, worst_case_avg_score, worst_case_prob, patterns_from_guess, children):
    node = {"average_score": average_score, "worst_case_avg_score": worst_case_avg_score,
            "patterns_from_guess": patterns_from_guess, "worst_case_prob": worst_case_prob, "children": children}
    return node
