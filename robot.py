
import numpy as np

from algorithms import AlphaBeta, MonteCarloTreeSearch

class HexRobot:

    def __init__(self, algorithm, robot_color, opponent_color, **kwargs):
        self.algorithm = algorithm
        self.robot_color = robot_color
        self.opponent_color = opponent_color
        

        if self.algorithm == 'alpha-beta':
            self.alpha_beta_search_depth = kwargs.get('depth')
            self.heuristic = kwargs.get('heuristic')
            
            if not self.alpha_beta_search_depth:
                self.alpha_beta_search_depth = 3
            
            if self.heuristic:
                self.engine = AlphaBeta(heuristic=self.heuristic)
            else:
                self.engine = AlphaBeta()

        elif self.algorithm == 'mcts':
            self.maxiter = kwargs.get('maxiter')
            self.maxtime = kwargs.get('maxtime')
            self.cp = kwargs.get('cp')

            if not self.maxiter:
                self.maxiter = 1000
            if not self.maxtime:
                self.maxtime = 5
            if not self.cp:
                self.cp = 1

            self.engine = MonteCarloTreeSearch(
                self.maxiter, 
                self.maxtime,
                self.cp
            )


        elif self.algorithm == 'random':
            pass

        else:
            raise ValueError('Unknown algorithm "{}"'.format(algorithm))

    def best_move_mcts(self, board):
        move = self.engine.search(
            board,
            self.robot_color,
            self.opponent_color
        )
        return move

    def best_move_alphabeta(self, board):
        empty_spaces = len(board.get_move_list())
        move, _ = self.engine.search(
            board, 
            self.robot_color,
            self.opponent_color,
            depth=min(empty_spaces, self.alpha_beta_search_depth)
        )
        return move

    def random_move(self, board):
        movelist = board.get_move_list()
        idx_move = np.random.randint(len(movelist))
        return movelist[idx_move]

    def make_move(self, board):
        if self.algorithm == 'alpha-beta':
            move = self.best_move_alphabeta(board)
        elif self.algorithm == 'mcts':
            move = self.best_move_mcts(board)
        elif self.algorithm == 'random':
            move = self.random_move(board)
        board.set_piece(move, color=self.robot_color)
