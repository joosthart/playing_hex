import copy
import sys
import time

from utils import timeout


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
            else:  # n not in queue
                queue[n] = score

        visited[state] = queue[state]
        del queue[state]


def shortest_path_heuristic(board, player, opponent):
    shortest_path_player = dijkstra(board, player)
    shortest_path_opponent = dijkstra(board, opponent)

    if shortest_path_player == 0:  # player wins
        return board.size+1
    elif shortest_path_opponent == 0:  # oppenent wins
        return -(board.size+1)

    return -(shortest_path_player - shortest_path_opponent)

def random_heuristic():
    pass


class AlphaBeta:

    def __init__(self):
        self.n_searched = 0
        self.cutoffs = 0
    
    def reset(self):
        self.__init__()

    def search(self, board, player, opponent, maximize=True, depth=3, 
               alpha=-sys.maxsize, beta=sys.maxsize):

        if len(board.get_move_list()) < depth:
            depth = len(board.get_move_list())

        self.n_searched +=1
        best_move = None

        # perform some checks
        if depth <= 0:
            score = shortest_path_heuristic(board, player, opponent)
            return (None, score)

        if maximize:
            g = -sys.maxsize
            for move in board.get_move_list():
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, player)

                _, score = self.search(board_hyp, player, opponent, maximize=False,
                                       depth=depth-1, alpha=alpha, beta=beta)

                if score > g:
                    g = score
                    best_move = move

                if g >= beta:
                    self.cutoffs += 1
                    break

                if g > alpha:
                    alpha = g

        else:  # Minimize
            g = sys.maxsize
            for move in board.get_move_list():
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, opponent)

                _, score = self.search(board_hyp, player, opponent, maximize=True,
                                       depth=depth-1, alpha=alpha, beta=beta)

                if score < g:
                    g = score
                    best_move = move

                if g <= alpha:
                    self.cutoffs += 1
                    break

                if g < beta:
                    beta = g

        return best_move, g


class TranspositionTablesAlphaBeta:

    def __init__(self):
        self.tt = {}
        self.cutoffs = 0
        self.n_searched = 0

    def reset(self):
        self.__init__()

    def lookup(self, board, depth, alpha, beta):
        state_key = board.hash_state()

        if state_key not in self.tt.keys():
            return False, None, []

        move, state_depth, g, state = self.tt[state_key]

        hit = False
        if state_depth <= 0:
            hit = True
        elif state_depth >= depth:
            if state == 'LEAF':
                hit = True
            elif state == 'LOWERBOUND' and g >= beta:
                hit = True
            elif state == 'UPERBOUND' and g <= alpha:
                hit = True

        if hit:
            return hit, g, move
        else:            
            return False, None, move

    def store(self, board, depth, move, g, alpha, beta):

        state_key = board.hash_state()

        if depth <= 0 or alpha < g < beta:
            state = 'LEAF'
        elif g >= beta:
            state = 'LOWERBOUND'
            g = beta
        elif g <= alpha:
            state = 'UPPERBOUND'
            g = alpha
        else:
            raise RuntimeError

        self.tt[state_key] = (move, depth, g, state)

    def _move_ordering(self, all_moves, best_moves):
        for m in best_moves:
            if m in all_moves:
                all_moves.remove(m)
                all_moves.insert(0,m)
        return all_moves

    def search(self, board, player, opponent, maximize=True, depth=3,
               alpha=-sys.maxsize, beta=sys.maxsize):

        self.n_searched += 1

        hit, g, tt_best_move = self.lookup(board, depth, alpha, beta)

        if hit:
            self.cutoffs += 1
            return tt_best_move, g

        best_move = []
        if depth <= 0:
            g = shortest_path_heuristic(board, player, opponent)
            board_hyp = copy.deepcopy(board)


        elif maximize:
            g = -sys.maxsize
            ordered_move_list = self._move_ordering(board.get_move_list(), tt_best_move)
            for move in ordered_move_list:
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, player)

                nextmove, score = self.search(board_hyp, player, opponent,
                                              maximize=False, depth=depth-1,
                                              alpha=alpha, beta=beta)

                if score > g:
                    g = score
                    best_move = [move] + nextmove
                elif best_move == []:
                    best_move = [move] + nextmove

                if g >= beta:
                    self.cutoffs += 1
                    break

                if g > alpha:
                    alpha = g

        else:  # Minimize
            g = sys.maxsize
            ordered_move_list = self._move_ordering(board.get_move_list(), tt_best_move)
            for move in ordered_move_list:
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, opponent)

                nextmove, score = self.search(board_hyp, player, opponent,
                                              maximize=True, depth=depth-1,
                                              alpha=alpha, beta=beta)

                if score < g:
                    g = score
                    best_move = [move] + nextmove
                elif best_move == []:
                    best_move = [move] + nextmove

                if g <= alpha:
                    self.cutoffs += 1
                    break

                if g < beta:
                    beta = g

        self.store(board_hyp, depth, best_move, g, alpha, beta)

        return best_move, g



    def iterative_deepening(self, board, player, opponent, maxtime, maxdepth=9):

        t0 = time.time()
        d=1
        while d < maxdepth and time.time() - t0 < maxtime:
            print(d)
            move, g = self.search(board, player, opponent, depth=d)
            print(move, g, self.n_searched)
            # print(self.tt)
            d+=1
            
        return move, g


################################################################################
# DEPRECATED                                                                   #
################################################################################


def alphabeta(board, player, opponent, maximize=True, depth=3,
              alpha=-sys.maxsize, beta=sys.maxsize):

    best_move = None

    # perform some checks
    if depth <= 0:
        score = shortest_path_heuristic(board, player, opponent)
        return (None, score)

    if maximize:
        g = -sys.maxsize
        for move in board.get_move_list():
            board_hyp = copy.deepcopy(board)
            board_hyp.set_piece(move, player)

            _, score = alphabeta(board_hyp, player, opponent, maximize=False,
                                 depth=depth-1, alpha=alpha, beta=beta)

            if score > g:
                g = score
                best_move = move

            if g >= beta:
                break

            if g > alpha:
                alpha = g

    else:  # Minimize
        g = sys.maxsize
        for move in board.get_move_list():
            board_hyp = copy.deepcopy(board)
            board_hyp.set_piece(move, opponent)

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

def tt_lookup(tt, board, depth, alpha, beta):
    state_key = board.hash_state()

    if state_key not in tt.keys():
        return False, None, []

    move, state_depth, g, state = tt[state_key]

    hit = False
    if state_depth <= 0:
        hit = True
    elif state_depth >= depth:
        if state == 'LEAF':
            hit = True
        elif state == 'LOWERBOUND' and g >= beta:
            hit = True
        elif state == 'UPERBOUND' and g <= alpha:
            hit = True

    if hit:
        return hit, g, move
    else:
        return False, None, []


def tt_store(tt, board, depth, move, g, alpha, beta):

    state_key = board.hash_state()

    if depth <= 0 or alpha < g < beta:
        state = 'LEAF'
    elif g >= beta:
        state = 'LOWERBOUND'
        g = beta
    elif g <= alpha:
        state = 'UPPERBOUND'
        g = alpha
    else:
        raise RuntimeError

    tt[state_key] = (move, depth, g, state)
    return tt


def tt_alphabeta(board, player, opponent, maximize=True, depth=3, tt={},
                 alpha=-sys.maxsize, beta=sys.maxsize):

    hit, g, tt_best_move = tt_lookup(tt, board, depth, alpha, beta)

    if hit:
        
        return tt_best_move, g, tt

    best_move = []
    if depth <= 0:
        g = shortest_path_heuristic(board, player, opponent)
        board_hyp = copy.deepcopy(board)
        return [], g, tt

    elif maximize:
        g = -sys.maxsize
        for move in tt_best_move + board.get_move_list():
            board_hyp = copy.deepcopy(board)
            board_hyp.set_piece(move, player)

            nextmove, score, tt = tt_alphabeta(board_hyp, player, opponent,
                                               maximize=False, depth=depth-1,
                                               tt=tt, alpha=alpha, beta=beta)

            if score > g:
                g = score
                best_move = [move] + nextmove
            elif best_move == []:
                best_move = [move] + nextmove

            if g >= beta:
                break

            if g > alpha:
                alpha = g

    else:  # Minimize
        g = sys.maxsize
        for move in tt_best_move + board.get_move_list():
            board_hyp = copy.deepcopy(board)
            board_hyp.set_piece(move, opponent)

            nextmove, score, tt = tt_alphabeta(board_hyp, player, opponent,
                                               maximize=True, depth=depth-1,
                                               tt=tt, alpha=alpha, beta=beta)

            if score < g:
                g = score
                best_move = [move] + nextmove
            elif best_move == []:
                best_move = [move] + nextmove

            if g <= alpha:
                break

            if g < beta:
                beta = g

    tt = tt_store(tt, board_hyp, depth, best_move, g, alpha, beta)

    return best_move, g, tt
