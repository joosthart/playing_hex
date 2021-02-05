import numpy as np

class Board:

    def __init__(self, size, char_empty='o', char_player1='+', char_player2='x'):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.char_empty = char_empty
        self.char_player1 = char_player1
        self.char_player2 = char_player2

    def set_piece(self, pos, player):

        # Check whether pos is a valid position
        if not self.set_is_valid(pos):
            raise ValueError('Illegal move: piece is trying to be set at an invalid location.')
        r, q = pos
        self.grid[q,r] = player
    
    def unset_piece(self, pos, player):

        r, q = pos
        if self.grid[q,r] == player:
            self.grid[q,r] = 0
        else:
            raise ValueError('Illegal move: tryig to unset piece that does not exist.')
    
    def set_is_valid(self, pos):
        r, q = pos
        if (r >= 0 and r < self.size and q >= 0 and q < self.size and 
                self.grid[q,r] == 0):
            return True
        else:
            return False

    def get_move_list(self):
        # [r,q]
        return np.argwhere(self.grid == 0)

    def print(self):
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
    

if __name__== '__main__':
    board = Board(5)

    board.set_piece((3,4), -1)
    board.set_piece((1,2), 1)
    # board.unset_piece((1,2), -1)
    print(board.get_move_list())

    board.print()
