import ast
import sys
import warnings

import numpy as np
from numpy.lib.arraysetops import isin

class HexBoard:
    BLUE = 1
    RED = 2
    EMPTY = 3

    def __init__(self, size, char_empty='o', char_player1='+', char_player2='x'):
        self.size = size
        self.board = np.full((size, size), HexBoard.EMPTY, dtype=int)
        self.game_over=False
        self.char_empty = char_empty
        self.char_player1 = char_player1
        self.char_player2 = char_player2
    
    def get_size(self):
        return self.size

    def is_game_over(self):
        return self.game_over
    
    def is_empty(self, pos):
        return self.board[pos] == HexBoard.EMPTY

    def is_color(self, pos, color):
        return self.board[pos] == color

    def get_color(self, pos):
        
        if pos == (-1, -1):
            return HexBoard.EMPTY
        return self.board[pos]

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
        if not self.game_over and self.move_is_valid(pos):
            self.board[pos] = player
            if self.check_win(HexBoard.RED) or self.check_win(HexBoard.BLUE):
                self.game_over = True
        else:
            warnings.warn(
                'Illegal move: piece is trying to be set at an invalid location.'
            )
            return False
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
        if self.board[pos] == player:
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
            [Bool]
        """
        if (not isinstance(pos, tuple) and len(pos) < 2 and 
            not isinstance(pos[0], int) and not isinstance(pos[1], int)):
            return False
        y, x = pos
        if (y >= 0 and y < self.size and x >= 0 and x < self.size and 
                self.board[pos] == HexBoard.EMPTY):
            return True
        else:
            return False
        
    def get_neighbors(self, pos):
        y, x = pos
        neighbors = []
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

    def border(self, color, move):
        y,x = move
        return (color == HexBoard.BLUE and y == self.size-1) or \
               (color == HexBoard.RED and x == self.size-1)

    def traverse(self, color, move, visited):
        if not self.is_color(move, color) or (move in visited and visited[move]):
            return False
        if self.border(color, move):
            return True
        visited[move] = True
        for n in self.get_neighbors(move):
            if self.traverse(color, n, visited):
                return True
        return False

    def check_win(self, color):
        for i in range(self.size):
            if color == HexBoard.BLUE:
                move = (0, i)
            else:
                move = (i, 0)
            if self.traverse(color, move, {}):
                return True
        return False

    def get_move_list(self):
        """Return list of available moves"""
        return np.argwhere(self.board == HexBoard.EMPTY).tolist()

    def print(self):
        """Print the board to console"""
        board_string = ''
        for r in range(self.size):
            board_string += (r-1)*' '
            for q in range(self.size):
                board_string += ' '
                if self.board[q,r] == HexBoard.BLUE:
                    board_string += self.char_player1
                elif self.board[q,r] == HexBoard.RED:
                    board_string += self.char_player2
                else: 
                    board_string += self.char_empty
            board_string += '\n'
        board_string = board_string.strip()

        print(board_string)
    

class Client(HexBoard):

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
        self.set_piece(tuple(movelist[idx_move]), player=self.RED)

    def transform_user_input(self, user_input):
        """Transform user input to usefull format.

        Args:
            user_input (str): User input string

        Returns:
            Returns None of input in invalid format.
        """
        if ',' in user_input:
            split_user_input = user_input.split(',')
            x, y = int(split_user_input[0])-1, int(split_user_input[1])-1
            return (y,x)
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
        self.set_piece(move, player=self.BLUE)

class Vertex:

    def __init__(self, pos):
        self.pos = pos
        self.distance = sys.maxint
        self.visited = False
        self.neighbors = {}
    
    def add_neighbor(self, pos, weight):
        self.neighbors[pos] = weight

class Graph:
    pass

def dijkstra_length_shortest_path(board, player):
    unvisited = np.fill((board.get_size(),board.get_size()), sys.maxint)





if __name__== '__main__':
    game = Client(size=5)

    game.set_piece((0,2), game.RED)
    game.set_piece((0,3), game.RED)
    game.set_piece((1,4), game.RED)

    game.set_piece((1,2), game.BLUE)
    game.set_piece((2,2), game.BLUE)
    game.set_piece((3,1), game.BLUE)

    game.print()


    game.print()
    for _ in range(15):
        game.user_make_move()
        if game.is_game_over():
            print('player has won')
            break
        game.random_move_generator()
        if game.is_game_over():
            print('robot has won')
            break
        game.print()
    print()
    game.print()
