# KRK Endgame Program

## Description

This is a program I wrote for an artificial intelligence class (CPSC 481) I took while doing my masters in psychology at California State University, Fullerton. It simulates a KRK chess endgame, where player X has a king and rook, while player Y has only a king. The goal of the player X is to force player Y into checkmate, while the goal of player Y is to avoid this situation until the maximum number of moves have played out.

### Minimax and Heuristics
Each player uses a minimax algorithm (with alpha-beta pruning to reduce infeasible brances of the game tree in order to reduce the size of the search space). Player X and player Y each have their own heuristic functions to determine what moves are best for them based on their goals. For the heuristic functions, I initially based player X’s heuristic off of the mop-up evaluation of CHESS 4.5, as indicated in [this](https://chessprogramming.wikispaces.com/Mop-up+evaluation) chess programming wiki.

#### Heuristic Strategies

For player X’s heuristic, the value receives a bonus for checkmate states, which is weighted based on how far it is from the current node. Similarly, the heuristic implements a penalty for stalemate states, also weighted by distance from the current game state. This way, player X is guided towards checkmate positions and away from states that lead to a draw. For player Y’s heuristic, the central idea is to deduct points the further the bare king is from the center. This is due to the fact that checkmate is much easier to acquire when the king is cornered, staying near the middle of the board is the bare king’s best chance of pulling through a draw. However, a stalemate will most likely occur when the bare king is cornered as well, which is one of the most advantageous outcome for the bare king since it terminates the game early as a draw.

Since it may be very easy for a game that is seemingly moving toward a stalemate outcome to result in checkmate, player Y’s heuristic does not advocate stalemates. The other optimal outcome besides dragging out a draw is for player Y’s king to take player X’s rook. Although this situation is unlikely to occur since it would require player X to make a very poor move, leaving it exposed to a diagonal attack from the bare king, it is a possibility. In order to provoke this possibility against another opponent player X, player Y's heuristic applies a bonus for game states that allow player X’s rook to get taken out. This would lead the game to draw due to insufficient materials, which is the best possible outcome for player Y.

#### Minimax Implentation

The implementation found in the game is an adaptation from a Python implementation found on [UC Berkeley’s website](http://aima.cs.berkeley.edu/python/games.html) (unfortunately, it appears that this link is now dead). One important adjustment I made was to ensure random selection in the event of multiple children with a maximum heuristic value. To do this, I created a list of tuples that included the child states and their corresponding heuristic values, sorted in non-increasing order by heuristic value. Then, I used a for loop to iterate over the sorted list, appending each state to a list called winners until the heuristic value changed. Subsequently, the function choice() from Python’s random module was used to randomly select a child state from the list, if necessary. Additionally, I made another adjustment to help lure player X away from situations where a repeating cycle of states occurs. I did this by having the alpha-beta algorithm treat states that have an immediate repeating series of ancestors between four and eight ancestors long like a leaf. This way, those states get directly evaluated by the heuristic function, which penalizes states for having cycle histories. However, the algorithm will only do this when it is player X searching through states since the algorithm is implemented as a method for the Player class.

## Usage
`git clone https://github.com/shandelman116/AI-Chess-KRK-Endgame.git`

`python main.py`

Note: When printing the chessboard, the program makes use of ANSI escape codes to color the terminal like a real chessboard. Unfortunately, this is not supported in Windows CMD, and therefore is automatically disabled if the detected OS is Windows.

## Instructions

* Choose whether you want to run a supplied test case (by default, it reads from testCases.txt). The syntax for test cases is straightforward in the testCase.txt file on how to specify starting positions (see below for more details). If you say no, you will be able to pick player 1 or player 2 and play against the program.
* Enter the maximum number of moves the game should terminate after.
* If you chose a test case, the program will run its course based on the supplied test cases.
* If you choose no test, then you must tell the program whether to play as player X or player Y.
* Choose the initial starting points of each piece (player X's king and rook, player Y's king).
* When entering moves in the game, use the format K(3,5), which here means "move my king to file 3, rank 5".


### Using Test Cases: testCase.txt

In testing mode, the program will play its own player X and player Y by itself, printing the moves as they occur into the terminal window as well as to a file named gameResult.txt. The parsing function for the test cases was written so that the testCase.txt file can have comments written into it (using the # symbol) and have empty lines, which will not interfere with the normal functioning of the program. However, the syntax of the test cases must adhere to the syntax as used in the assignment test case examples. For instance, x.K(1,4) will be understood as player X’s king at file 1, rank 4. Although the X and K are not case sensitive, the parsing function is expecting a dot between the letters to let it know that the first letter indicates the player and owner of the piece, while the second letter represents the actual piece itself.
