# Playing Hex

Welcome! This repository contains several Reinforcement Learning algorithms for the game [Hex](https://en.wikipedia.org/wiki/Hex_(board_game)). Using the CLI you can play against these algorithms. Furthermore, experiments we have run on these algorithms can be reproduced using the CLI.

Have fun!

## Installation

Install the necessary packages using:
    
    pip install -r requirements.txt

## Usage
An example of how to use the CLI:

```
python main.py -p -d 6 -mcts -t 6
```

This wil start a game between the user and a Monte Carlo Tree Search, which has a computation time of 6 seconds, on a 6x6 board. This will give the following output in your terminal:

```
+  1 2 3 4 5 6 
-------------------
1| o o o o o o
2|  o o o o o o
3|   o o o o o o
4|    o o o o o o
5|     o o o o o o
6|      o o o o o o
coordinates of next move (x,y):
```

Many different options exist which can be printed using:

```
python main.py --help
```

All experiments can be run as follows:

```
python main.py -r
```
This will save results of the experiments in the `output` folder. **Note, running all our experiments can take up to 2 hours.**

## Acknowledgements
We had help from some very good blogs and code examples. Below a list of the most helpful ones.

- https://github.com/duilio/c4
- https://github.com/kenjyoung/mopyhex
- https://int8.io/monte-carlo-tree-search-beginners-guide/

