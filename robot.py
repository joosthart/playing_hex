
from algorithms import alphabeta, AlphaBeta

import numpy as np


class HexRobot:

    def __init__(self, algorithm, robot_color, opponent_color, **kwargs):
        self.algorithm = algorithm
        self.robot_color = robot_color
        self.opponent_color = opponent_color
        self.alpha_beta_search_depth = kwargs.get('depth')

        if self.algorithm == 'alpha-beta':
            self.engine = AlphaBeta()
            if not self.alpha_beta_search_depth:
                self.alpha_beta_search_depth = 3
        elif self.algorithm == 'random':
            pass

    def best_move_alphabeta(self, board):
        empty_spaces = len(board.get_move_list())
        move, _ = self.engine.search(
            board, 
            self.robot_color,
            self.opponent_color,
            depth=min(empty_spaces,self.alpha_beta_search_depth)
        )
        print(move)
        return move

    def random_move(self, board):
        movelist = board.get_move_list()
        idx_move = np.random.randint(len(movelist))
        return movelist[idx_move]

    def make_move(self, board):
        if self.algorithm == 'alpha-beta':
            move = self.best_move_alphabeta(board)
        elif self.algorithm == 'random':
            move = self.random_move(board)
        board.set_piece(move, color=self.robot_color)
