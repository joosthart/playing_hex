import sys
import os
import warnings

import numpy as np

from src.robot import HexRobot
from src.user import HumanClient
from src.algorithms import dijkstra

class HexBoard:
    """Base class of the board for the game Hex
    """
    BLUE = 1
    RED = 2
    EMPTY = 3

    def __init__(self, size, char_empty='o', char_player1='+', 
                 char_player2='x'):
        """
        Args:
            size (int): Size of the board
            char_empty (str, optional): Character to print on empty board 
                position. Defaults to 'o'.
            char_player1 (str, optional): Character to print for player 1. 
                Defaults to '+'.
            char_player2 (str, optional): Character to print for player 2. 
                Defaults to 'x'.
        """
        self.size = size
        self.char_empty = char_empty
        self.char_player1 = char_player1
        self.char_player2 = char_player2

        self.board = np.full((size, size), HexBoard.EMPTY, dtype=int)
        self.game_over=False
    
    def get_size(self):
        return self.size

    def is_game_over(self):
        """Check if the game is over.
        """
        if (self.check_win(HexBoard.RED) or self.check_win(HexBoard.BLUE) or 
            len(self.get_move_list())==0):
            self.game_over = True
        return self.game_over
    
    def is_empty(self, pos):
        return self.board[pos] == HexBoard.EMPTY

    def is_color(self, pos, color):
        return self.board[pos] == color

    def get_color(self, pos):
        if pos == (-1, -1):
            return HexBoard.EMPTY
        return self.board[pos]

    def set_piece(self, pos, color):
        """Set a piece on the board at position [r,q].

        Args:
            pos (tup[int,int]): Position to place piece. Coordinates should be 
                (row, column).
            color (int): integer that indicates color.

        Returns:
            bool: If move illegal, returns false. If legal move, returns True.
        """

        # Check whether pos is a valid position
        if not self.move_is_valid(pos):
            raise RuntimeWarning('cannot set piece: invalid move.')
        else:
            self.board[pos] = color
            if self.check_win(HexBoard.RED) or self.check_win(HexBoard.BLUE):
                self.game_over = True            
        return True
    
    def unset_piece(self, pos, color):
        """Remove a piece from the board.

        Args:
            pos (tup[int,int]): Position to place piece. Coordinates should be 
                (row, column).
            color (int): integer that indicates color.

        Returns:
            bool: If legal move, returns True. If position on board is empty,
                returns False.
        """
        if self.board[pos] == color:
            self.board[pos] = 0
            return True
        else:
            warnings.warn(
                'Illegal move: tryig to unset piece that does not exist.'
            )
            return False
    
    def move_is_valid(self, pos):
        """Check if move is valid

        Args:
            pos (tup[int,int]): Position to place piece. Coordinates should be 
                (row, column).

        Returns:
            Bool
        """

        if (not isinstance(pos, tuple) or len(pos) != 2 or 
            not isinstance(pos[0], int) or not isinstance(pos[1], int)):
            return False
        y, x = pos
        if (y >= 0 and y < self.size and x >= 0 and x < self.size and 
                self.board[pos] == HexBoard.EMPTY):
            return True
        else:
            return False
        
    def get_neighbors(self, pos):
        """Get a list of neighbors of a given piostion.
        """
        y, x = pos
        neighbors = []

        # Check if sarting position for dijsktra.
        if y == sys.maxsize:
            neighbors = [(self.size-1,i) for i in range(self.size)]
        elif y == -sys.maxsize:
            neighbors = [(0,i) for i in range(self.size)]
        elif x == sys.maxsize:
            neighbors = [(i,self.size-1) for i in range(self.size)]
        elif x == -sys.maxsize:
            neighbors = [(i,0) for i in range(self.size)]
        # Position inside board
        else:
            if y-1 >= 0:
                neighbors.append((y-1, x))
            if y+1 < self.size:
                neighbors.append((y+1, x))
            if y-1 >= 0 and x+1 <= self.size-1:
                neighbors.append((y-1, x+1))
            if y+1 < self.size and x-1 >= 0:
                neighbors.append((y+1, x-1))
            if x+1 < self.size:
                neighbors.append((y, x+1))
            if x-1 >= 0:
                neighbors.append((y, x-1))
        return neighbors

    def check_win(self, color):
        """Check if a player has won using dijsktra shortest path.
        """
        if dijkstra(self, color) == 0:
            return True
        else:
            return False

    def get_move_list(self):
        """Return list of available moves"""
        return [
            tuple(x) for x in np.argwhere(self.board == HexBoard.EMPTY).tolist()
        ]

    def print(self):
        """Print the board to console"""
        board_string = ''
        for y in range(self.size):
            if y == 0:
                board_string += '+  '
                for x in range(self.size):
                    board_string += str(x+1) + ' '
                board_string += '\n'
                board_string += (1+3*self.size)*'-'
                board_string += '\n'
            board_string += str(y+1)+'|'+y*' '
            
            for x in range(self.size):
                board_string += ' '
                if self.board[y,x] == HexBoard.BLUE:
                    board_string += self.char_player1
                elif self.board[y,x] == HexBoard.RED:
                    board_string += self.char_player2
                else: 
                    board_string += self.char_empty
            board_string += '\n'
        board_string = board_string.strip()

        print(board_string)
    
    def hash_state(self):
        """Hash the board state.
        """
        return hash(self.board.tostring())


def play_(opponent, board_size, level=3):
    board = HexBoard(board_size)

    human = HumanClient(board.BLUE)
    robot = HexRobot(opponent, board.RED, board.BLUE, depth=level)


    print('Let the game begin!')
    print(
        'The human is playing as \"{}\" and the robot as \"{}\".'.format(
            board.char_player1, 
            board.char_player2
        )
    )
    print()
    board.print()
    while not board.is_game_over():
        human.make_move(board)
        robot.make_move(board)
        board.print()

    print()
    print(80*'-')
    print()

    if board.check_win(board.BLUE):
        print('The human has won!')
    elif board.check_win(board.RED):
        print('The robot has won...')
    else:
        print('We have a problem...')

def play(algorithm, board_size, kwargs):
    board = HexBoard(board_size)

    human = HumanClient(board.BLUE)
    robot = HexRobot(algorithm, board.RED, board.BLUE, **kwargs)

    os.system('clear')

    print('Let the game begin!')
    print(
        'The human is playing as \"{}\" and the robot as \"{}\".'.format(
            board.char_player1, 
            board.char_player2
        )
    )
    print('The human is playing horizontally and the robot vertically.')
    print()
    board.print()

    while not board.is_game_over():
        human.make_move(board)
        os.system('clear')
        board.print()
        if board.is_game_over():
            break

        print('Robot is thinking...')
        robot.make_move(board)
        os.system('clear')
        board.print()
        robot.print_stats()
        if board.is_game_over():
            break
    
    if board.check_win(board.BLUE):
        print('The human has won!')
    elif board.check_win(board.RED):
        print('The robot has won...')
    else:
        print('It\'s a draw')


if __name__ == '__main__':
    play('alpha-beta', 4)