
from algorithms import alphabeta

import numpy as np

class HexRobot:

    def __init__(self, algorithm, robot_color, opponent_color, **kwargs):
        self.algorithsm = algorithm
        self.robot_color = robot_color
        self.opponent_color = opponent_color

    def best_move_alphabeta(self, board):
        move, _ = alphabeta(board, self.robot_color, self.opponent_color)
        return move

    def random_move(self, board):
        movelist = board.get_move_list()
        idx_move = np.random.randint(len(movelist))
        return tuple(movelist[idx_move])

    def make_move(self, board):
        if self.algorithm == 'alpha-beta':
            move = self.best_move_alphabeta(board)
        elif self.algorithm == 'random':
            move = self.random_move(board)
        board.set_piece(move, color=self.robot_color)