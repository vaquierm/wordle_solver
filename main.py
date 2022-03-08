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
    #evaluate_solver(GreedyAnswerScopeSolver, guesses, answers, guess_matrix, None)
    human_play_random_word(guesses, answers, guess_matrix, deep_decision_tree, True, True)


def counts(deep_decision_tree):
    for first_guess in deep_decision_tree.keys():
        count = {}
        for pattern in deep_decision_tree[first_guess]["children"].keys():
            for second_guess in deep_decision_tree[first_guess]["children"][pattern].keys():
                if second_guess not in count:
                    count[second_guess] = 0
                count[second_guess] += 1
        best_guess = ""
        best_count = 0
        second_guess = ""
        second_count = -1
        total = 0
        for guess in count.keys():
            total += count[guess]
            if count[guess] > best_count:
                second_guess = best_guess
                second_count = best_count
                best_count = count[guess]
                best_guess = guess
            elif count[guess] > second_count:
                second_guess = guess
                second_count = count[guess]
        print(first_guess)
        print(str(best_count / total * 100) + " " + str(best_guess))
        print(str(second_count / total * 100) + " " + str(second_guess))
        print()


def human_play_random_word(guesses, answers, guess_matrix, deep_decision_tree, suggestions, post_guess_analysis):
    wordle = Wordle(answers[np.random.randint(0, answers.shape[0])], guesses)
    wordle = Wordle("hoard", guesses)
    if suggestions or post_guess_analysis:
        GreedyDeepSolver(wordle, guesses, answers, guess_matrix, create_index_map(guesses), create_index_map(answers), create_answers_in_guesses_mask(answers, guesses), deep_decision_tree)
    wordle.human_play()


def evaluate_solver(solver, guesses, answers, guess_matrix, deep_decision_tree):
    solver_benchmark = SolverBenchmark(solver, guesses, answers, guess_matrix, create_index_map(guesses), create_index_map(answers), create_answers_in_guesses_mask(answers, guesses), deep_decision_tree)
    solver_benchmark.start()


if __name__ == '__main__':
    main()
