import sys


from game import HexBoard, dijkstra

def test_boarder():
    board = HexBoard(size=5)

    for i in board.get_neighbors((+sys.maxsize, 0)):
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



if __name__ == '__main__':
    # test_boarder()
    test_dijkstra()