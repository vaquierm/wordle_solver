import math

import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from src.wordle import compute_guess


def load_file(file_path: str):
    if not os.path.isfile(file_path):
        raise Exception("Cannot find the file")
    return np.loadtxt(file_path, dtype=str)


def create_index_map(data):
    index_map = {}
    for i in range(data.shape[0]):
        index_map[data[i]] = i
    return index_map


def load_deep_decision_tree(file_path: str):
    if not os.path.isfile(file_path):
        return {}
    pickle_file = open(file_path, 'rb')
    return pickle.load(pickle_file)


def save_deep_decision_tree(file_path: str, decision_tree):
    pickle_file = open(file_path, 'wb')
    pickle.dump(decision_tree, pickle_file)


def create_answers_in_guesses_mask(answers, guesses):
    def mark(guess):
        return guess in answers

    return np.vectorize(mark)(guesses)


def solver_performance_summary(scores, solver_name):
    fig, ax = plt.subplots()
    N, bins, patches = ax.hist(scores, bins=[1, 2, 3, 4, 5, 6, 7, 8], align="left", density=True, edgecolor='white')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.title('Performance of ' + solver_name + " (" + str(round(scores.mean(), 2)) + " guess average)")
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    for p in ax.patches:
        percentage = '{:.2f}%'.format(p.get_height() * 100)
        x = p.get_x() + p.get_width() / 2 - 0.35
        y = p.get_y() + p.get_height() + 0.005
        ax.annotate(percentage, (x, y))
    for i in range(0, 3):
        patches[i].set_facecolor('#4f6f16')
    for i in range(3, 4):
        patches[i].set_facecolor('#cec535')
    for i in range(4, 6):
        patches[i].set_facecolor('#ab6420')
    for i in range(6, len(patches)):
        patches[i].set_facecolor('#892a1a')
    plt.show()


def compute_guess_matrix(guesses, answers):
    guess_matrix = np.zeros((guesses.shape[0], answers.shape[0]), dtype=int)
    progress = 0
    for i in range(guesses.shape[0]):
        def compute_single_matrix(answer):
            return compute_guess(guesses[i], answer)
        guess_matrix[i] = np.vectorize(compute_single_matrix)(answers)

        if math.floor(i / guesses.shape[0] * 100) > progress:
            progress = math.floor(i / guesses.shape[0] * 100)
            print(str(progress) + "% complete")
    return guess_matrix


if __name__ == '__main__':
    guesses = load_file("../data/wordle_guesses.txt")
    answers = load_file("../data/wordle_words.txt")
    guess_matrix = compute_guess_matrix(guesses, answers)
    np.savetxt("../data/guess_matrix.csv", guess_matrix, fmt="%d")
