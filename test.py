import sys


from game import HexBoard
from algorithms import dijkstra, alphabeta

def test_boarder():
    board = HexBoard(size=3)

    for i in board.get_neighbors((0, -sys.maxsize)):
        board.set_piece(i, board.RED)

    board.print()

def test_dijkstra():

    board = HexBoard(size=6)

    board.set_piece((2, 0), board.BLUE)
    board.set_piece((2, 1), board.BLUE)
    board.set_piece((2, 2), board.BLUE)
    board.set_piece((3, 2), board.BLUE)

    board.set_piece((3, 0), board.RED)
    board.set_piece((4, 0), board.RED)
    board.set_piece((3, 1), board.RED)
    board.set_piece((1, 2), board.RED)


    dist_blue = dijkstra(board, board.BLUE)
    dist_red  = dijkstra(board, board.RED)
    print(80*'-')
    print(dist_blue)
    print(dist_red)


    board.print()

def test_neighbors():

    board = HexBoard(size=5)

    for i in board.get_neighbors((0, 2)):
        board.set_piece(i, board.RED)

    board.print()


def test_win():

    board = HexBoard(size=5)

    for i in range(5):
        board.set_piece((0,i), board.RED)
    
    board.print()

    print(board.is_game_over())

    #############################################

    board = HexBoard(size=5)

    for i in range(5):
        board.set_piece((0,i), board.BLUE)
    
    board.print()

    print(board.is_game_over())

    #############################################

    board = HexBoard(size=5)

    for i in range(5):
        board.set_piece((i,0), board.BLUE)
    
    board.print()

    print(board.is_game_over())

    #############################################

    board = HexBoard(size=5)

    for i in range(5):
        board.set_piece((i,0), board.RED)
    
    board.print()

    print(board.is_game_over())

    #############################################

    board = HexBoard(size=3)

    board.set_piece((2,0), board.BLUE)
    board.set_piece((1,1), board.BLUE)
    board.set_piece((1,2), board.BLUE)
    
    board.print()

    print(dijkstra(board, board.BLUE))

    print(board.is_game_over())


def test_alphabeta():
    board = HexBoard(size=4)

    board.set_piece((1,1), board.BLUE)
    board.set_piece((1,0), board.RED)

    board.print()


    while True:
        print(20*'-' + '  TURN BLUE  ' + 20*'-')

        best_move, g = alphabeta(board, board.BLUE, board.RED, depth=9)
        board.set_piece(best_move, board.BLUE)
        board.print()
        print('score: ', g)

        if board.check_win(board.BLUE):
            print('win')
            break

        print(20*'-' + '  TURN RED   ' + 20*'-')

        best_move, g = alphabeta(board, board.RED, board.BLUE, depth=9)
        board.set_piece(best_move, board.RED)
        board.print()
        print('score: ', g)

        if board.check_win(board.RED):
            print('win')
            break


if __name__ == '__main__':
    # test_boarder()
    # test_dijkstra()
    test_neighbors()
    # test_win()
    # test_alphabeta()