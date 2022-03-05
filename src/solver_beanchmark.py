import math

from src.wordle import Wordle
from src.data import solver_performance_summary
import numpy as np


class SolverBenchmark:
    def __init__(self, solver_type, possible_guesses, possible_answers, guess_matrix, guess_index_map, answer_index_map, answers_in_guesses_mask, deep_decision_tree):
        self.solver_type = solver_type
        self.possible_guesses = possible_guesses
        self.possible_answers = possible_answers
        self.guess_matrix = guess_matrix
        self.guess_index_map = guess_index_map
        self.answer_index_map = answer_index_map
        self.answers_in_guesses_mask = answers_in_guesses_mask
        self.deep_decision_tree = deep_decision_tree

    def start(self):
        score = np.zeros(self.possible_answers.shape[0])
        progress = 0
        solver_name = None
        for i in range(self.possible_answers.shape[0]):
            answer = self.possible_answers[i]
            wordle = Wordle(answer, self.possible_guesses)
            if self.deep_decision_tree is None:
                solver = self.solver_type(wordle, self.possible_guesses, self.possible_answers, self.guess_matrix, self.guess_index_map, self.answer_index_map, self.answers_in_guesses_mask)
            else:
                solver = self.solver_type(wordle, self.possible_guesses, self.possible_answers, self.guess_matrix, self.guess_index_map, self.answer_index_map, self.answers_in_guesses_mask, self.deep_decision_tree)

            solver_name = solver.name
            while wordle.game_state == 0:
                wordle.guess(solver.top_N_suggestions(1)[0])

            score[i] = 7 if wordle.game_state == -1 else wordle.guess_n
            if math.floor(i / self.possible_answers.shape[0] * 100) > progress:
                print(str(math.floor(i / self.possible_answers.shape[0] * 100)) + "% complete")
                progress += 10

        solver_performance_summary(score, solver_name)
        print("Average score: " + str(np.mean(score)))
