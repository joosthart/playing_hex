

class HumanClient():
    
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
            'coordinates of next move (x,y): '
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