import time as t

import trueskill as ts

from src.game import * 

def run(player1, player2, board_size, depth1, depth2, t_run, N, cp):
    """ Run Match """

    #run 1 test
    board = HexBoard(board_size)
        
    if player1 == 'alpha-beta-iterative-deepening':
        robot1 = HexRobot(player1, board.BLUE, board.RED, maxtime=t_run)
    elif player1 == 'mcts':
        robot1 = HexRobot(player1, board.BLUE, board.RED, maxtime=t_run, maxiter=N, cp=cp)
    else:
        robot1 = HexRobot(player1, board.BLUE, board.RED, depth = depth1)
    
    if player2 == 'alpha-beta-iterative-deepening':
        robot2 = HexRobot(player2, board.RED, board.BLUE, maxtime=t_run)
    elif player2 == 'mcts':
        robot2 = HexRobot(player2, board.RED, board.BLUE, maxtime=t_run, maxiter=N, cp=cp)
    else:
        robot2 = HexRobot(player2, board.RED, board.BLUE, depth = depth2)

    #play the game
    print("Start Match: Player 1 ({}): {}, Player 2 ({}): {}".format(board.char_player1, player1, board.char_player2, player2))
    while not board.is_game_over():
        robot1.make_move(board)

        if board.is_game_over() == True:
            break
        
        robot2.make_move(board)
    return board


def match(players, board_size, depths, r1, r2, amount, t_run, N, cp):
    """ Set up the Match"""
    # save ratings
    save = np.empty(0)

    #play game
    for i in range(amount):

        board = run(players[(i+1)%2], players[i%2], board_size, depths[(i+1)%2], depths[i%2], t_run, N, cp)

        #evaluate who won and update rating
        if board.check_win(board.BLUE) and (i+1)%2 == 0 or board.check_win(board.RED) and (i+1)%2 == 1:
            r1, r2 = ts.rate_1vs1(r1, r2) 
        elif board.check_win(board.BLUE) and (i+1)%2 == 1 or board.check_win(board.RED) and (i+1)%2 == 0:
            r2, r1 = ts.rate_1vs1(r2, r1) 
        else: #draw
            r1, r2 = ts.rate_1vs1(r1, r2, drawn=True) 
        
        save = np.append(save, r1)
        save = np.append(save, r2)

    return r1, r2, save

def evaluate(players, board_size, depths = [4,4], amount = 1, t_run = 7.2, N = 1e9, cp = 1):
    """
    Evaluation between two methods in players, based on TrueSkill evaluation
    """

    #initialize rating
    if len(players) == 2:
        r1 = ts.Rating()
        r2 = ts.Rating()
       
        print()
        print('rating 1: ', r1)
        print('rating 2: ', r2)
        print()

        r1, r2, save = match(players, board_size, depths, r1, r2, amount, t_run, N, cp)

        print()
        print('rating 1: ', r1)
        print('rating 2: ', r2)
        print()

    elif len(players) == 3:
        r1 = ts.Rating()
        r2 = ts.Rating()
        r3 = ts.Rating()

        print("Evaluating players: {} {} width depth: {} {}".format(players[0], players[1], depths[0], depths[1]))
        r1, r2, save_1 = match([players[0],players[1]], board_size, depths, r1, r2, amount, t_run, N, cp)
        print("Evaluating players: {} {} width depth: {} {}".format(players[0], players[2], depths[0], depths[2]))
        r1, r3, save_2 = match([players[0],players[2]], board_size, depths, r1, r3, amount, t_run, N, cp)
        print("Evaluating players: {} {} width depth: {} {}".format(players[1], players[2], depths[1], depths[2]))
        r2, r3, save_3 = match([players[1],players[2]], board_size, depths, r2, r3, amount, t_run, N, cp)

        print()
        print('rating 1: ', r1)
        print('rating 2: ', r2)
        print('rating 3: ', r3)
        print()
    
        save = np.hstack((r1, r2, r3))

    return save

def time_move(player, board_size, depth):
    """
    Measure time of single move
    """
    clock = np.zeros(10)
    for i in range(10):
        board = HexBoard(board_size)
        robot = HexRobot(player, board.BLUE, board.RED, depth = depth)

        t1 = t.time()
        robot.make_move(board)
        t2 = t.time()
        clock[i] = t2 - t1

    t_estimate = np.mean(clock) #seconds
    return t_estimate

def time_match(players, board_size, depths):
    """Measure time of a match"""
    board = HexBoard(board_size)

    robot1 = HexRobot(players[0], board.BLUE, board.RED, depth = depths[0])
    robot2 = HexRobot(players[1], board.RED, board.BLUE, depth = depths[1])

    moves_made = 0

    #play the game
    t1 = t.time()
    while not board.is_game_over():
        moves_made +=1 
        robot1.make_move(board)

        if board.is_game_over() == True:
            break
        
        moves_made +=1 
        robot2.make_move(board)

    t2 = t.time()
    t_match = t2 - t1 #seconds
    return t_match, moves_made

def test_time(players, board_size, depths):
    """Run to evaluate the speed of a match
    
    ouput: printing First move time, averaged move time and total match time
     """
    print("Time for player {} with depth {} to make a single move: {:.4f} s".format(players[0], depths[0], time_move(players[0], board_size, depths[0])))
    print()

    t_match, moves_made = time_match(players, board_size, depths)

    print("Time for player {} vs player {}, with depths {} and {} to do a whole match: {:.4f} s".format(players[0], players[1], depths[0], depths[1], t_match))
    print("Averaged move time: {:.4f} s ".format(t_match/moves_made))
    print()  
