import ast
import warnings

import numpy as np
from numpy.lib.arraysetops import isin

class Board:

    def __init__(self, size, char_empty='o', char_player1='+', char_player2='x'):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.char_empty = char_empty
        self.char_player1 = char_player1
        self.char_player2 = char_player2

    def set_piece(self, pos, player):
        """Set a piece on the board at position [r,q].

        Args:
            pos (tup[int,int]): Position to place piece. Coordinates should be 
                (row, column).
            player (int): integer that indicates player.

        Returns:
            [bool]: If move illegal, returns false. If legal move, returns True.
        """

        # Check whether pos is a valid position
        if not self.move_is_valid(pos):
            warnings.warn(
                'Illegal move: piece is trying to be set at an invalid location.'
            )
            return False
        r, q = pos
        self.grid[q,r] = player
        return True
    
    def unset_piece(self, pos, player):
        """Remove a piece from the board.

        Args:
            pos (tup[int,int]): Position to place piece. Coordinates should be 
                (row, column).
            player (int): integer that indicates player.

        Returns:
            [bool]: If legal move, returns True. If position on board is empty,
                returns False.
        """
        r, q = pos
        if self.grid[q,r] == player:
            self.grid[q,r] = 0
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
            [Bool]
        """
        if (not isinstance(pos, tuple) and len(pos) < 2 and 
            not isinstance(pos[0], int) and not isinstance(pos[1], int)):
            return False
        r, q = pos
        if (r >= 0 and r < self.size and q >= 0 and q < self.size and 
                self.grid[q,r] == 0):
            return True
        else:
            return False

    def get_move_list(self):
        """Return list of available moves"""
        return np.argwhere(self.grid == 0).tolist()

    def print(self):
        """Print the board to console"""
        board_string = ''
        for r in range(self.size):
            board_string += (r-1)*' '
            for q in range(self.size):
                board_string += ' '
                if self.grid[q,r] == -1:
                    board_string += self.char_player1
                elif self.grid[q,r] == 1:
                    board_string += self.char_player2
                else: 
                    board_string += self.char_empty
            board_string += '\n'
        board_string = board_string.strip()

        print(board_string)

class Client(Board):

    def __init__(self, **kwargs):
        super(Client, self).__init__(**kwargs)

    def get_user_input(self, msg):
        """Get user input through console

        Args:
            msg (str): Message to display

        Returns:
            str: response
        """
        resp = input(msg)
        return resp
    
    def random_move_generator(self):
        """Random move generotor bot.
        """
        movelist = self.get_move_list()
        idx_move = np.random.randint(len(movelist))
        # Move list is in [r,q] but set piece expects [q,r]
        self.set_piece(movelist[idx_move][::-1], player=1)

    def transform_user_input(self, user_input):
        """Transform user input to usefull format.

        Args:
            user_input (str): User input string

        Returns:
            Returns None of input in invalid format.
        """
        if ',' in user_input:
            split_user_input = user_input.split(',')
            r, q = int(split_user_input[0])-1, int(split_user_input[1])-1
            return (r,q)
        else:
            return 

    def user_make_move(self):
        """Query user to make move and set piece on board.
        """
        user_input = self.get_user_input(
            'coordinates of next move: '
        )
        move = self.transform_user_input(user_input)

        valid = self.move_is_valid(move)
        while not valid:
            user_input = self.get_user_input(
                'Invalid move, coordinate of next move: '
            )
            move = self.transform_user_input(user_input)
            valid = self.move_is_valid(move)
        self.set_piece(move, player=-1)



if __name__== '__main__':
    game = Client(size=5)
    game.print()
    for _ in range(15):
        game.user_make_move()
        game.random_move_generator()
        game.print()
