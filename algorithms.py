import copy
import sys
import time

import numpy as np

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
        raise RuntimeError

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


def random_heuristic(board, **kwargs):
    movelist = board.get_move_list()
    idx_move = np.random.randint(len(movelist))
    return movelist[idx_move]

class AlphaBeta:

    def __init__(self, heuristic = shortest_path_heuristic):
        self.nodes_searched = 0
        self.cutoffs = 0
        self.heuristic = heuristic

    def reset(self):
        self.__init__()

    def search(self, board, player, opponent, maximize=True, depth=3,
               alpha=-sys.maxsize, beta=sys.maxsize):

        # TODO: move this check outside method
        if len(board.get_move_list()) < depth:
            depth = len(board.get_move_list())

        self.nodes_searched += 1
        best_move = None

        if depth <= 0:
            score = self.heuristic(board, player=player, opponent=opponent)
            return (None, score)

        if maximize:
            g = -sys.maxsize
            for move in board.get_move_list():
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, player)

                _, score = self.search(
                    board_hyp, 
                    player, 
                    opponent, 
                    maximize=False,
                    depth=depth-1, 
                    alpha=alpha, 
                    beta=beta
                )

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

                _, score = self.search(
                    board_hyp, 
                    player, 
                    opponent, 
                    maximize=True,
                    depth=depth-1, 
                    alpha=alpha, 
                    beta=beta
                )

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

    def __init__(self, heuristic = shortest_path_heuristic):
        self.tt = {}
        self.cutoffs = 0
        self.nodes_searched = 0
        self.tt_lookups = 0
        self.search_depth = 0
        self.heuristic = heuristic

    def reset(self):
        self.__init__(self.heuristic)

    def lookup(self, board, depth, alpha, beta):
        state_key = board.hash_state()

        if state_key not in self.tt.keys():
            return False, None, []

        move, state_depth, g, state = self.tt[state_key]

        hit = False
        # TODO look at this; I do not understand why/if this works
        if state_depth < depth:
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
                all_moves.insert(0, all_moves.pop(all_moves.index(m)))

        return all_moves

    def search(self, board, player, opponent, maximize=True, depth=3,
               alpha=-sys.maxsize, beta=sys.maxsize):

        hit, g, tt_best_move = self.lookup(board, depth, alpha, beta)

        if hit:
            self.tt_lookups += 1
            return tt_best_move, g
        
        self.nodes_searched += 1

        best_move = []
        if depth <= 0:
            g = self.heuristic(board, player=player, opponent=opponent)
            board_hyp = copy.deepcopy(board)
            return [], g

        elif maximize:
            g = -sys.maxsize
            ordered_move_list = self._move_ordering(
                board.get_move_list(), tt_best_move
            )

            for move in ordered_move_list:
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, player)

                nextmove, score = self.search(
                    board_hyp, 
                    player, 
                    opponent,
                    maximize=False, 
                    depth=depth-1,
                    alpha=alpha, 
                    beta=beta
                )

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
            ordered_move_list = self._move_ordering(
                board.get_move_list(), tt_best_move
            )
            for move in ordered_move_list:
                board_hyp = copy.deepcopy(board)
                board_hyp.set_piece(move, opponent)

                nextmove, score = self.search(
                    board_hyp, 
                    player, 
                    opponent,
                    maximize=True, 
                    depth=depth-1,
                    alpha=alpha, 
                    beta=beta
                )

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

        # TODO This will always exceed the timeout
        while self.search_depth < maxdepth and time.time() - t0 < maxtime:
            self.search_depth += 1
            move, g = self.search(
                board, 
                player, 
                opponent, 
                depth=self.search_depth
            )
        return move, g

    def print_summary(self):
        summary_txt = (
            '\n'
            'SUMMARY OF MOVE TAKING PROCESS:\n'
            '-----------------------------------------------------'+'\n'
            'Search depth:                | {depth}\n'
            'Nodes searched:              | {nodes_searched}\n'
            'Alpha-Beta pruning cutoffs:  | {cutoffs}\n'
            'Transposition table lookups: | {tt_lookups}\n'
            '-----------------------------------------------------'+'\n'
        )
        
        print(
            summary_txt.format(
                depth=self.search_depth,
                nodes_searched=self.nodes_searched,
                cutoffs=self.cutoffs,
                tt_lookups=self.tt_lookups
            )
        )

class Node:
    
    def __init__(self, player_to_move, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.player_to_move = player_to_move

        self.visited = 0
        self.score = 0

        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
    
    def is_fully_expanded(self):
        if self.children and all(c.visited>0 for c in self.children):
            return True
        else:
            return False


class MonteCarloTreeSearch:

    def __init__(self, maxiter=1000, maxtime=5, cp=1):
        self.maxiter = maxiter
        self.maxtime = maxtime
        self.cp = 1

    def best_child(self, node):
        
        weights = [
            c.score/c.visited + self.cp * np.sqrt(np.log(node.visited/c.visited))
            for c in node.children
        ]
        # Select best child randomly out equally good children
        return node.children[np.argmax(weights == np.amax(weights))]

    def get_most_visited_child(self, node):
        visits = [c.visited for c in node.children]
        # Select best child randomly out equally good children
        return node.children[np.argmax(visits == np.amax(visits))]

    def make_node_move(self, node, board):
        if node.player_to_move == self.player_to_move:
            board.set_piece(node.move, self.opponent)
        else:
            board.set_piece(node.move, self.player_to_move)

    def select(self):
        node = self.root
        board_hyp = copy.deepcopy(self.root_board)

        while node.is_fully_expanded():
            node = self.best_child(node)
            self.make_node_move(node, board_hyp)

            if node.visited == 0:
                return node, board_hyp
        
        if not node.children:
            self.expand(node, board_hyp)
        
        if node.children:
            node = np.random.choice(node.children)
            self.make_node_move(node, board_hyp)

        return node, board_hyp

    def expand(self, node, board):
        if node.player_to_move == self.player_to_move:
            next_player = self.opponent
        else:
            next_player = self.player_to_move

        for move in board.get_move_list():
            child_node = Node(next_player, move, node)
            node.add_child(child_node)

    def select_random_move(self, board):
        movelist = board.get_move_list()
        idx_move = np.random.randint(len(movelist))
        return movelist[idx_move]

    def rollout_policy(self, board):
        return self.select_random_move(board)

    def rollout(self, leaf, board):
        board_hyp = copy.deepcopy(board)

        current_player = leaf.player_to_move
        while not board_hyp.is_game_over():
            move = self.rollout_policy(board_hyp)
            board_hyp.set_piece(move, current_player)
            
            if current_player == self.player_to_move:
                current_player = self.opponent
            else:
                current_player = self.player_to_move

        if board_hyp.check_win(self.player_to_move):
            return 1
        elif board_hyp.check_win(self.opponent):
            return 0
        else: # draw
            return 0.5

    def update_node(self, node, result):
        node.visited += 1
        node.score += result
        return node

    def backpropagate(self, node, result):
        if node.parent == None: # parent node
            node = self.update_node(node, result)
            return
        node = self.update_node(node, result)
        self.backpropagate(node.parent, result)

    def search(self, board, player_to_move, opponent):
        self.player_to_move = player_to_move
        self.opponent = opponent

        self.root = Node(self.player_to_move)
        self.root_board = copy.deepcopy(board)

        t0 = time.time()
        i = 0
        while time.time()-t0 < self.maxtime and i < self.maxiter:
            leaf, board = self.select()
            simulation_result = self.rollout(leaf, board)
            self.backpropagate(leaf, simulation_result)
            i+=1

        best_child = self.get_most_visited_child(self.root)
        best_move = best_child.move

        return best_move

    def get_tree_size(self):
        size = 0

        queue = [self.root]
        while queue:
            node = queue.pop()
            
            for child in node.children:
                queue.append(child)
            
            size += 1

        return size