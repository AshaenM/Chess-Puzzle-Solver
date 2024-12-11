# Chess Puzzle Solving AI
## Overview
The Chess Puzzle Solving AI Project is an advanced new take of the chess game where position files of chess puzzles can be passed with the command line and the user is allowed to choose different AI that solve the puzzle.

# Features
- AI algorithms: Minimax, Minimax with Alpha-Beta Pruning, Depth-First Search (DFS), Breadth-First Search (BFS) solve the puzzles.
- User's choice: The user gets to select which algorithm solves the puzzle and then observes the solution along with the time taken.
- UI interface: The UI shows the original position of the puzzle and then the final position once the puzzle is solved along with the moves in chess notation.

# Current State
- All the AI work for 1,2 and 3 move checkmate puzzles.
- For 4 move mates, I've tested one puzzle so far. Only DFS has returned a correct solution. BFS doesn't work properly. Minimax and Minimax with Alpha Beta Pruning take really long to find a solution. I've waited around 7 minutes for Minimax with Alpha Beta Pruning to find a solution for position10 but it didn't.
- En Passant, casting, and promotions haven't been implemented yet. Hence, puzzles involving those moves as winning moves will definitely not be picked up by any of the AI.

# Technologies Used
- Programming Language: Python
- Game Framework: Pygame
- Development Environment: Visual Studio Code

# How to Play
- Download python, pygame, chess libraries
- Run main.py with the position file. Eg: python main.py position1.txt
- Left click on any of the AI Algorithm buttons to solve the puzzle.
- Left click the reset button to reset the puzzle to the original position and use a different AI to solve the puzzle

# Future Enhancements
- Extended to solve puzzles with more moves.
- More AI algorithms implemented.

# Acknowledgements
- Piece images creator: https://github.com/plemaster01
