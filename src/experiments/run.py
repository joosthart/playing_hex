
from astropy.modeling.functional_models import Gaussian1D
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sbs

from src.experiments.evaluation import *

sbs.set_context('notebook')
sbs.set_style('ticks')


def elo_explain_experiments():
    # Coin toss
    steps = 100
    np.random.seed(42)
    random_eval = np.random.choice([0, 1], steps)
    random_eval = [
        sum(random_eval[:i+1] == 0)/len(random_eval[:i+1])
        for i in range(len(random_eval))
    ]

    # Run against itself
    saved = evaluate(['alpha-beta', 'alpha-beta'], 4, [3, 3], steps)

    std = np.array([saved[i].sigma for i in range(len(saved))])
    mean = np.array([saved[i].mu for i in range(len(saved))])

    x = np.arange(0, 50, 0.01)

    plt.figure()
    plt.plot(x, Gaussian1D(mean=25, stddev=8.333)(x), label='Initial value')
    plt.plot(x, Gaussian1D(mean=15, stddev=6)(x), label='Player 2, loss')
    plt.plot(x, Gaussian1D(mean=35, stddev=6)(x), label='Player 1, win')

    plt.xlabel('Rating Scale')
    plt.yticks([])

    plt.axvline(15, c='gray', ls='dashed')
    plt.axvline(25, c='gray', ls='dashed')
    plt.axvline(35, c='gray', ls='dashed')

    plt.text(13.1, 0.8, '$\mu = 15$', rotation='vertical', c='k', alpha=0.4)
    plt.text(23.1, 0.8, '$\mu = 25$', rotation='vertical', c='k', alpha=0.4)
    plt.text(33.1, 0.8, '$\mu = 35$', rotation='vertical', c='k', alpha=0.4)

    plt.legend(loc=6)
    plt.tight_layout()
    plt.savefig('./output/ELO_explain1.pdf')
    plt.close()

    x = np.arange(-20, 50, 0.01)

    fig, ax1 = plt.subplots()
    ax1.plot(x, Gaussian1D(mean=10, stddev=10)(x), label='Diff. Gaussian')
    ax1.fill_between(
        np.arange(-20, 0, 0.01),
        Gaussian1D(
            mean=10,
            stddev=10
        )(np.arange(-20, 0, 0.01)),
        color='blue',
        alpha=0.3
    )

    ax1.axvline(10, c='gray', ls='dashed')
    ax1.legend(loc=6)

    cum_gaus = np.cumsum(Gaussian1D(mean=10, stddev=10)(x))

    ax2 = ax1.twinx()
    ax2.plot(x, cum_gaus/cum_gaus[-1],
             color='red', label='Cum. diff. Gaussian')
    ax2.legend(loc=5)
    ax2.set_ylabel("P(x)")
    ax1.set_ylabel('p(x) [unnormalized]')
    ax1.set_xlabel('x')

    fig.tight_layout()
    plt.savefig('./output/ELO_explain2.pdf')
    plt.close()

    indexing = np.arange(0, len(saved), 2)
    x = np.arange(steps)

    fig, ax1 = plt.subplots()
    fig.set_figwidth(10)
    fig.set_figheight(5)

    ax1.plot(random_eval, label='# of Heads in a Coin Flip')
    ax1.set_ylim(ymin=0, ymax=1)

    ax1.axhline(0.5, ls='dashed', c='gray')
    ax1.axvline(12, c='k', alpha=0.4)
    ax1.set_ylabel('p (Heads)')
    ax1.set_xlabel('Amount of Games')
    ax1.text(12.5, 0.02, 'Recommaned Cut-off',
             rotation='vertical', c='k', alpha=0.4)
    ax1.text(14.5, 0.02, 'by TrueSkill', rotation='vertical', c='k', alpha=0.4)

    ax1.legend(loc=1)

    ax2 = ax1.twinx()
    ax2.fill_between(x, y1=mean[indexing]-2 * std[indexing], y2=mean[indexing]+2 *
                     std[indexing], color='orange', alpha=0.3, label='$2\sigma$ rating uncertainty')
    ax2.plot(mean[indexing], label='Alpha-Beta, depth = 3',
             c='orange', alpha=0.7)
    ax2.fill_between(x, y1=mean[indexing+1]-2 * std[indexing+1], y2=mean[indexing+1] +
                     2*std[indexing+1], color='red', alpha=0.3, label='$2\sigma$ rating uncertainty')
    ax2.plot(mean[indexing+1], label='Alpha-Beta, depth = 3',
             c='red', alpha=0.7)

    ax2.legend(loc=4)
    ax2.axvline(24, c='k', alpha=0.4)
    ax1.text(24.5, 0.02, 'Chosen Cut-off',
             rotation='vertical', c='k', alpha=0.4)

    fig.tight_layout()
    plt.savefig('./output/ELO_convergience.pdf')
    plt.close()


def alpha_beta_experiments():

    run_times = np.array([1, 2, 4, 10])
    ratings_saved = np.empty((len(run_times), 2), dtype=np.object)

    for idx, run_time in enumerate(run_times):
        print("Move Time: ", run_time)
        save = evaluate(['alpha-beta', 'alpha-beta-iterative-deepening'],
                        5, [4, 4], amount=24, t_run=run_time)
        ratings_saved[idx] = save[-2:]

    plt.figure()
    plt.errorbar(run_times,
                 [ratings_saved[:, 0][i].mu for i in range(len(run_times))],
                 yerr=[2*ratings_saved[:, 0]
                       [i].sigma for i in range(len(run_times))],
                 marker='o', label='Alpha-Beta, search depth 4', ls='', capsize=5)
    plt.errorbar(run_times+0.2,
                 [ratings_saved[:, 1][i].mu for i in range(len(run_times))],
                 yerr=[2*ratings_saved[:, 1]
                       [i].sigma for i in range(len(run_times))],
                 marker='o', label='Alpha-Beta, iterative deepening + transportation tables', ls='', capsize=5)
    plt.xlabel("Move Time [s]")
    plt.ylabel("Elo Rating")
    plt.legend()
    plt.tight_layout()
    plt.savefig("./output/ELOrating_2_2.pdf")
    plt.close()

    board_sizes = np.arange(3, 8)
    ratings_saved = np.empty((len(board_sizes), 3), dtype=np.object)

    for idx, board_size in enumerate(board_sizes):
        print("Board size: ", board_size)
        save = evaluate(['random', 'alpha-beta', 'alpha-beta'],
                        board_size, [3, 3, 4], amount=12)
        ratings_saved[idx] = save

    plt.figure()
    plt.errorbar(board_sizes,
                 [ratings_saved[:, 0][i].mu for i in range(len(board_sizes))],
                 yerr=[2*ratings_saved[:, 0]
                       [i].sigma for i in range(len(board_sizes))],
                 marker='o', label='Random Heuristic', ls='', capsize=5)
    plt.errorbar(board_sizes+0.1,
                 [ratings_saved[:, 1][i].mu for i in range(len(board_sizes))],
                 yerr=[2*ratings_saved[:, 1]
                       [i].sigma for i in range(len(board_sizes))],
                 marker='o', label='Alpha-Beta, search depth 3', ls='', capsize=5)
    plt.errorbar(board_sizes+0.2,
                 [ratings_saved[:, 2][i].mu for i in range(len(board_sizes))],
                 yerr=[2*ratings_saved[:, 2]
                       [i].sigma for i in range(len(board_sizes))],
                 marker='o', label='Alpha-Beta, search depth 4', ls='', capsize=5)
    plt.xlabel("Board Size [N]")
    plt.ylabel("Elo Rating")
    plt.axis(xmin=2, xmax=8)
    plt.legend()
    plt.tight_layout()
    plt.savefig("./output/ELOrating_2_1.pdf")
    plt.close()


def mtcs_experiments():
    Ns = np.logspace(1, 3, 3)
    ratings_saved = np.empty((len(Ns), 2), dtype=np.object)

    for idx, N in enumerate(Ns):
        print("Rollouts: ", N)
        save = evaluate(['mcts', 'alpha-beta-iterative-deepening'],
                        5, amount=24, t_run=5, N=N, cp=1)
        ratings_saved[idx] = save[-2:]

    plt.figure()
    plt.errorbar(Ns,
                 [ratings_saved[:, 0][i].mu for i in range(len(Ns))],
                 yerr=[2*ratings_saved[:, 0][i].sigma for i in range(len(Ns))],
                 marker='o', label='Monte Carlo Tree Search ($C_p = 1$)', ls='', capsize=5)

    plt.errorbar(Ns+0.2,
                 [ratings_saved[:, 1][i].mu for i in range(len(Ns))],
                 yerr=[2*ratings_saved[:, 1][i].sigma for i in range(len(Ns))],
                 marker='o', label='Alpha-Beta, iterative deepening + transportation tables', ls='', capsize=5)
    plt.xlabel("Number of Node Expansions [N]")
    plt.ylabel("Elo Rating")
    plt.xscale('log')
    plt.legend(loc=3)
    plt.tight_layout()
    plt.savefig("./output/ELOrating_3_1.pdf")
    plt.close()

    cps = np.array([0.1, 0.3, 0.5, 0.7, 1, 3])
    ratings_saved = np.empty((len(cps), 2), dtype=np.object)

    for idx, cp in enumerate(cps):
        print("$C_p$: ", cp)
        save = evaluate(['mcts', 'alpha-beta-iterative-deepening'],
                        5, amount=24, t_run=5, N=5e2, cp=cp)
        ratings_saved[idx] = save[-2:]

    plt.figure()
    plt.errorbar(cps,
                 [ratings_saved[:, 0][i].mu for i in range(len(cps))],
                 yerr=[2*ratings_saved[:, 0]
                       [i].sigma for i in range(len(cps))],
                 marker='o', label='Monte Carlo Tree Search ($N = 500$)', ls='', capsize=5)
    plt.errorbar(cps,
                 [ratings_saved[:, 1][i].mu for i in range(len(cps))],
                 yerr=[2*ratings_saved[:, 1]
                       [i].sigma for i in range(len(cps))],
                 marker='o', label='Alpha-Beta, iterative deepening + transportation tables', ls='', capsize=5)
    plt.xlabel("Exploitation parameter [$C_P$]")
    plt.ylabel("Elo Rating")
    plt.tight_layout()
    plt.legend(loc=8)
    plt.savefig("./output/ELOrating_3_2.pdf")
    plt.close()


def all_experiments():
    """Run all experiments used to generate report
    """
    elo_explain_experiments()
    alpha_beta_experiments()
    mtcs_experiments()
