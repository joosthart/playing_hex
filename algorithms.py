import copy
import sys

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

def shortest_path_heuristic(board, player, opponent):
    shortest_path_player = dijkstra(board, player)
    shortest_path_opponent = dijkstra(board, opponent)

    if shortest_path_player == 0: # player wins
        return board.size+1
    elif shortest_path_opponent == 0: # oppenent wins
        return -(board.size+1)
    
    return -(shortest_path_player - shortest_path_opponent)

def alphabeta(board, player, opponent, maximize=True, depth=3, 
              alpha=-sys.maxsize, beta=sys.maxsize):

    best_move=None

    # perform some checks
    if depth <=0:
        score = shortest_path_heuristic(board, player, opponent)
        return (None , score)

    if maximize:
        g = -sys.maxsize
        for move in board.get_move_list():
            board_hyp = copy.deepcopy(board)
            board_hyp.set_piece(tuple(move), player)

            _, score = alphabeta(board_hyp, player, opponent, maximize=False, 
                                 depth=depth-1, alpha=alpha, beta=beta)

            if score > g:
                g = score
                best_move = move

            if g >= beta:
                break

            if g > alpha:
                alpha = g

    else: # Minimize
        g = sys.maxsize
        for move in board.get_move_list():
            board_hyp = copy.deepcopy(board) 
            board_hyp.set_piece(tuple(move), opponent)

            _, score = alphabeta(board_hyp, player, opponent, maximize=True, 
                                 depth=depth-1, alpha=alpha, beta=beta)
            
            if score < g:
                g = score
                best_move = move

            if g <= alpha:
                break

            if g < beta:
                beta = g

    return tuple(best_move), g