import numpy as np

from src.data import load_file, create_index_map, create_answers_in_guesses_mask, load_deep_decision_tree
from src.wordle import Wordle
from src.solver.greedy_answer_scope_solver import GreedyAnswerScopeSolver
from src.solver.greedy_all_scope_solver import GreedyAllScopeSolver
from src.solver.greedy_deep_solver import GreedyDeepSolver
from src.solver.base_solver import BaseSolver
from src.solver_beanchmark import SolverBenchmark


def main():
    guesses = load_file("data/wordle_guesses.txt")
    answers = load_file("data/wordle_words.txt")
    guess_matrix = np.loadtxt("data/guess_matrix.csv")
    deep_decision_tree = load_deep_decision_tree("data/deep_decision_tree.pkl")
    wordle = Wordle(answers[np.random.randint(0, answers.shape[0])], guesses)
    #wordle = Wordle("wooly", guesses)
    basic_solver = GreedyDeepSolver(wordle, guesses, answers, guess_matrix, create_index_map(guesses), create_index_map(answers), create_answers_in_guesses_mask(answers, guesses), deep_decision_tree)
    wordle.human_play()
    #solver_benchmark = SolverBenchmark(GreedyDeepSolver, guesses, answers, guess_matrix, create_index_map(guesses), create_index_map(answers), create_answers_in_guesses_mask(answers, guesses))
    #solver_benchmark.start()
    print()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
