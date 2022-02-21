import numpy as np

from src.data import load_file, create_index_map, create_answers_in_guesses_mask
from src.wordle import Wordle
from src.solver.greedy_answer_scope_solver import GreedyAnswerScopeSolver
from src.solver.greedy_all_scope_solver import GreedyAllScopeSolver
from src.solver.base_solver import BaseSolver
from src.solver_beanchmark import SolverBenchmark


def main():
    guesses = load_file("data/wordle_guesses.txt")
    answers = load_file("data/wordle_words.txt")
    guess_matrix = np.loadtxt("data/guess_matrix.csv")
    wordle = Wordle(answers[np.random.randint(0, answers.shape[0])], guesses)
    basic_solver = GreedyAllScopeSolver(wordle, guesses, answers, guess_matrix, create_index_map(guesses), create_index_map(answers), create_answers_in_guesses_mask(answers, guesses))
    wordle.human_play()
    #solver_benchmark = SolverBenchmark(GreedyAllScopeSolver, guesses, answers, guess_matrix, create_index_map(guesses), create_index_map(answers), create_answers_in_guesses_mask(answers, guesses))
    #solver_benchmark.start()
    print()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
