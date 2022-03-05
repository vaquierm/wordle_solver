import math
import numpy as np


def compute_guess(guess, answer):
    target_word_copy = np.array(list(answer), dtype='S1')
    guess_copy = np.array(list(guess), dtype='S1')

    # Check which letters are in the correct position
    correct_pos = guess_copy == target_word_copy

    # Remove the correct letters from the target word
    target_word_copy[correct_pos] = 0

    repeated_target_word = np.tile(target_word_copy, (5, 1))
    tiled_guess = np.repeat(guess_copy, 5).reshape((5, 5))

    letter_hit = tiled_guess == repeated_target_word

    guess_hit_count = letter_hit.sum(axis=1)
    # The pattern is a 5 digit integer with digits 0, 1, 2
    # 1 for gray, 2 for yellow, 3 for green
    pattern = 0
    for i in range(5):
        if correct_pos[i]:
            pattern += math.pow(10, i) * 3
            continue
        if guess_hit_count[i] == 0:
            pattern += math.pow(10, i)
            continue
        found = False
        for j in range(5):
            if letter_hit[i][j]:
                pattern += math.pow(10, i) * 2
                letter_hit[:, j] = False
                found = True
                break
        if not found:
            pattern += math.pow(10, i)

    return int(pattern)


class Wordle:
    def __init__(self, target_word, possible_guesses):
        self.guess_n = 0
        self.game_state = 0
        self.guesses = []
        self.guess_patterns = []
        self.target_word = target_word
        self.pre_move_print = None
        if len(target_word) != 5:
            raise Exception("Target word must be of length 5")
        self.possible_guesses = possible_guesses

    def get_result_pattern_from_human(self):
        valid_pattern = False
        while not valid_pattern:
            user_guess = input("Enter the pattern you obtained using the characters G Y _\n")
            if len(user_guess) != 5:
                continue

    def human_play(self):
        while self.game_state == 0:
            valid_guess = False
            while not valid_guess:
                if self.pre_move_print is not None:
                    self.pre_move_print()
                user_guess = input("Enter a 5 letter word as your guess\n")
                if len(user_guess) != 5:
                    continue

                valid_guess = user_guess in self.possible_guesses

            self.guess(user_guess)
            self.print_board()

        if self.game_state == 1:
            print("You won!")
        else:
            print("Sad sad...")

    def print_board(self):
        for i in range(6):
            line = ""
            for j in range(5):
                if i >= self.guess_n:
                    tile_color_number = 1
                else:
                    tile_color_number = math.floor(self.guess_patterns[i] / math.pow(10, j)) % 10
                if tile_color_number == 3:
                    color = bcolors.GREEN
                elif tile_color_number == 2:
                    color = bcolors.YELLOW
                else:
                    color = bcolors.RESET

                line += color
                if i < len(self.guesses):
                    line += self.guesses[i][j]
                else:
                    line += "_"
                line += bcolors.RESET + " "
            print(line)

    def guess(self, word):
        if self.game_state != 0:
            raise Exception("Game is over")

        self.guesses.append(word)

        guess_matrix = compute_guess(word, self.target_word)
        self.guess_patterns.append(guess_matrix)

        # Check if game was won
        if guess_matrix == 33333:
            self.game_state = 1

        # Increment turn number
        self.guess_n += 1

        if self.guess_n == 6 and self.game_state != 1:
            self.game_state = -1

    def undo(self):
        self.game_state = 0
        self.guesses.pop()
        self.guess_n -= 1
        self.guess_patterns.pop()


class bcolors:
    GREEN = '\033[92m' #GREEN
    YELLOW = '\033[93m' #YELLOW
    RED = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR