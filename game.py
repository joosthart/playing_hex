import copy
import sys
import warnings

import numpy as np


from robot import HexRobot

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
        if self.check_win(HexBoard.RED) or self.check_win(HexBoard.BLUE):
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
            [bool]: If move illegal, returns false. If legal move, returns True.
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
            [bool]: If legal move, returns True. If position on board is empty,
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

    def shortest_path(self, color):
        if color == self.BLUE:
            initial = (0, -sys.maxsize)
            endstate = [(i, self.size-1) for i in range(self.size)]
            opponent = self.RED
        elif color == self.RED:
            initial = (-sys.maxsize, 0)
            endstate = [(self.size-1, i) for i in range(self.size)]
            opponent = self.BLUE

        visited = {}
        queue = {initial: 0}

        while queue: 
            state = min(queue, key=queue.get)

            if state in endstate:
                return queue[state]

            neighbors = self.get_neighbors(state)

            for n in neighbors:

                if n in visited:
                    continue
                if self.board[n] == opponent:
                    continue

                if self.board[n] == color:
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

    def check_win(self, color):
        if self.shortest_path(color) == 0:
            return True
        else:
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



class HumanClient():
    # TODO Move to another module
    def __init__(self, color):
        self.color = color

    def get_user_input(self, msg):
        """Get user input through console

        Args:
            msg (str): Message to display

        Returns:
            str: response
        """
        resp = input(msg)
        return resp

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

    def make_move(self, board):
        """Query user to make move and set piece on board.
        """
        user_input = self.get_user_input(
            'coordinates of next move: '
        )
        move = self.transform_user_input(user_input)

        valid = board.move_is_valid(move)
        while not valid:
            user_input = self.get_user_input(
                'Invalid move, coordinate of next move: '
            )
            move = self.transform_user_input(user_input)
            valid = board.move_is_valid(move)
        board.set_piece(move, color=self.color)
    

def play(opponent, board_size):
    board = HexBoard(board_size)

    human = HumanClient(board.BLUE)
    robot = HexRobot(opponent, board.RED, board.BLUE)

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

if __name__ == '__main__':
    play('alpha-beta', 5)