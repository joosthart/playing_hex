import argparse

from src.game import play
from src.experiments import run

parser = argparse.ArgumentParser(description='placeholder')

parser.add_argument(
    '-r', '--run-experiments', 
    action='store_true', 
    help='run all experiments.'
)
parser.add_argument(
    '-p', '--play' ,
    action='store_true', 
    help='Play against a robot.'
)
parser.add_argument(
    '-ab', '--alpha-beta' ,
    action='store_true', 
    help='Play against Robot using Alpha-Beta algorithm'
)
parser.add_argument(
    '-abtt', '--alpha-beta-transposition-table' ,
    action='store_true', 
    help=(
        'Play against Robot using Alpha-Beta algorithm enhanched with'
        'transposition tables and iterative deepening.'
    )
)
parser.add_argument(
    '-mcts', '--monte-carlo-tree-search' ,
    action='store_true', 
    help='Play against Robot using MCTS algorithm.'
)
parser.add_argument(
    '-s', '--board-size' ,
    default=5,
    type=int,
    help='Board size (max 9).'
)
parser.add_argument(
    '-d', '--depth' ,
    default=4,
    type=int,
    help='Robot algorithm search depth.'
)
parser.add_argument(
    '-t', '--time' ,
    default=5,
    type=int,
    help='Robot maximum search time.'
)
parser.add_argument(
    '-cp' ,
    default=0.3,
    type=int,
    help='Cp parmaeter for MCTS.'
)
parser.add_argument(
    '-i', '--max-iterations' ,
    default=500,
    type=int,
    help='Maximum iterations of MCTS.'
)



args = parser.parse_args()

if __name__ == '__main__':

    if args.run_experiments:
        run.all_experiments()

    elif args.play:
        if args.alpha_beta:
            algorithm = 'alpha-beta'
        elif args.alpha_beta_transposition_table:
            algorithm = 'alpha-beta-iterative-deepening'
        elif args.monte_carlo_tree_search:
            algorithm = 'mcts'
        else:
            algorithm = 'random'

        kwargs = {
            'depth': args.depth,
            'maxdepth': args.depth,
            'maxtime': args.time,
            'cp': args.cp,
            'maxiter': args.max_iterations
        }

        play(algorithm, min(args.board_size, 9), kwargs)