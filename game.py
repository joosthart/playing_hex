import sys
import warnings

import numpy as np

from robot import random_move_generator

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
                'Illegal move: piece is trying to be set at an invalid location ({}).'.format(pos)
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
        y, x = pos
        neighbors = []

        # Check if sarting position 
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
        for y in range(self.size):
            board_string += (y-1)*' '
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

class Client(HexBoard):

    def __init__(self, opponent='random,', **kwargs):
        self.opponent = opponent
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

        # TODO import this from robot

        movelist = self.get_move_list()
        idx_move = np.random.randint(len(movelist))
        # Move list is in [r,q] but set piece expects [q,r]
        self.set_piece(tuple(movelist[idx_move]), player=self.RED)
    
    def alpha_beta(self):
        raise NotImplementedError

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
    
    def robot_make_move(self):
        if self.opponent == 'random':
            self.random_move_generator()


def dijkstra(board, player):

    if player == board.BLUE:
        initial = (0, -sys.maxsize)
        endstate = [(i, board.size-1) for i in range(board.size)]
        opponent = board.RED
    elif player == board.RED:
        initial = (-sys.maxsize, 0)
        endstate = [(board.size-1, i) for i in range(board.size)]
        opponent = board.BLUE
    else:
        raise RuntimeError('Hier gaat wat mis...')

    visited = {}
    queue = {initial: 0}

    while queue: 
        state = min(queue, key=queue.get)

        if state in endstate:
            return queue[state]

        neighbors = board.get_neighbors(state)

        for n in neighbors:

            if n in visited:
                continue
            if board.board[n] == opponent:
                continue

            if board.board[n] == player:
                score = queue[state] 
            else:
                score = queue[state] + 1
            
            if n in queue:
                if queue[n] > score:
                    queue[n] = score
                # else: new value higher than queued value
            else: # n not in queue
                queue[n] = score

        visited[state] = queue[state]
        del queue[state]

def play(opponent, board_size):
    game = Client(opponent=opponent, size=board_size)

    print('Let\'s the game begin!')
    print(
        'The human is playing as \"{}\" and the robot as \"{}\".'.format(
            game.char_player1, 
            game.char_player2
        )
    )
    print()
    game.print()
    while not game.is_game_over():
        game.user_make_move()
        game.robot_make_move()
        game.print()

    print()
    print(80*'-')
    print()

    if game.check_win(game.BLUE):
        print('The human has won!')
    elif game.check_win(game.RED):
        print('The robot has won...')
    else:
        print('We have a problem...')

if __name__ == '__main__':
    play('random', 5)