from graphics import COLOUR_NAMES
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'  # Hides welcome message of pygame
import pygame
import sys
from collections import deque
import time
from move import Move
from board import Board
import chess

pygame.init() #initialise the pygame environment

#Constants for drawing the screen and gaps
WIDTH = 700
HEIGHT = 700
GAP = 25

#pygame initalization and global variables
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Puzzle Solver")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Comic Sans MS', 20)
minimax_text_button = font.render('Minimax', True, COLOUR_NAMES["BLACK"])
minimax_with_AB_text_button = font.render('Minimax (AB)', True, COLOUR_NAMES["BLACK"])
DFS_text_button = font.render('DFS', True, COLOUR_NAMES["BLACK"])
BFS_text_button = font.render('BFS', True, COLOUR_NAMES["BLACK"])
reset_text_button = font.render('Reset', True, COLOUR_NAMES["BLACK"])
move_set_calculated = None
current_player = None
move_index = None
duration = False   
original_fen = None

# ______________________________Checkmate checker_________________________________________

def check_game_over(board, player):
    #Check if checkmate or stalemate
    possible_moves = board.generate_possible_moves(player)
    
    original_position_fen = board.generate_fen()
        
    board_1 = chess.Board(original_position_fen + " " + player)
    legal_moves_uci = [move.uci() for move in board_1.legal_moves]
    possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
    
    
    #print(board.pieces) -- for debugging
    #print(king_in_check) -- for debugging
    if not possible_moves and board.king_in_check:
        return True
    else:
        return False 
    
def display_moves(board, moves):
    count_pos_x = 550
    count_pos_y = 100
    pos_x = 570
    pos_y = 100
    count = 1
    move_set = []
    move_offset_y = 60  # Vertical offset between moves
    move_offset_x = 70  # Horizontal offset between columns

    board.draw_board()  # Draw board before displaying moves
    for piece in board.pieces:
        piece.draw(screen)
    pygame.display.flip()

    # Display move count
    screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x, count_pos_y))

    # Loop through all moves and display them
    for i, move in enumerate(moves):
        move_text = f"{move}#" if i == len(moves) - 1 else str(move)  # Add '#' for the final move if it's a mate
        move_x = pos_x + (i % 2) * move_offset_x  # Alternate X position for two columns
        move_y = pos_y + (i // 2) * move_offset_y  # Adjust Y position based on index

        screen.blit(font.render(move_text, True, COLOUR_NAMES["BLACK"]), (move_x, move_y))
        move_set.append((move_text, move_x, move_y))

    pygame.display.update()  # Update the display after rendering all moves
    return move_set

# ______________________________Search algorithms_________________________________________

def get_best_move(board, max_depth, player):
    #manage the minimax algorithm and return the best sequence of moves
    global move_index
    global move_set_calculated
    
    max_depth = max_depth + max_depth - 1
    move_index = max_depth
    
    if move_set_calculated == None:
        best_sequence = None
        moves = []
        best_score = float("-inf")
        
        possible_moves = board.generate_possible_moves(player)
        
        original_position_fen = board.generate_fen()
        
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        row_pieces = []
        board_line = original_position_fen.strip()
        ranks = board_line.split("/")
        for rank in ranks:
            split_strings = [char for char in rank]
            row_pieces.append(split_strings)
        
        for move in possible_moves:
            piece, square_to = move
            board.update(piece, square_to)
            score, sequence = minimax(board, 1, False, max_depth, player, current_sequence=[move])  # Pass first move in the sequence
            board.add_pieces(row_pieces)
            if score > best_score:
                best_score = score
                best_sequence = sequence
        print(best_sequence)
        
        for move in best_sequence:
            piece, square_to = move
            if square_to in board.occupied_squares:
                if piece.piece_type == "p" or piece.piece_type == "P":
                    move_obj = Move(piece, square_to.x, square_to.y, piece.square.x, iscapture=True)
                else:
                    move_obj = Move(piece, square_to.x, square_to.y, iscapture=True)
            else:
                move_obj = Move(piece, square_to.x, square_to.y)
            board.update(piece, square_to)
            moves.append(move_obj)
            
        move_set_calculated = display_moves(board, moves)
        return move_set_calculated
    else:
        return move_set_calculated

def minimax(board, depth, isMaximising, max_depth, player, current_sequence=[]):
    # The minimax algoirithm
    if depth >= max_depth:
        if current_player == "w":
            player = "b"
        else:
            player = "w"

        if check_game_over(board, player):
            return 100, current_sequence
        else:
            return -100, current_sequence
        
    original_position_fen = board.generate_fen()
    row_pieces = []
    board_line = original_position_fen.strip()
    ranks = board_line.split("/")
    for rank in ranks:
        split_strings = [char for char in rank]
        row_pieces.append(split_strings)
            
    if isMaximising:
        best_score = float("-inf")
        best_sequence = None
        if current_player == "w":
            player = "w"
        else:
            player = "b"
        
        possible_moves = board.generate_possible_moves(player)
                
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        for move in possible_moves:
            piece, square_to = move
            #Vital area: update move, recursively call minimax with the new board state and player, and undo the move once returned
            board.update(piece, square_to)
            score, sequence = minimax(board, depth + 1, False, max_depth, player, current_sequence + [move])
            board.add_pieces(row_pieces)
            if score > best_score:
                best_score = score
                best_sequence = sequence
        return best_score, best_sequence
    
    else:
        best_score = float("inf")
        best_sequence = None
        if current_player == "w":
            player = "b"
        else:
            player = "w"
            
        possible_moves = board.generate_possible_moves(player)
                
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        for move in possible_moves:
            piece, square_to = move
            #Vital area: update move, recursively call minimax with the new board state and player, and undo the move once returned
            board.update(piece, square_to)
            score, sequence = minimax(board, depth + 1, True, max_depth, player, current_sequence + [move])
            board.add_pieces(row_pieces)
            if score < best_score:
                best_score = score
                best_sequence = sequence
        return best_score, best_sequence
    
def get_best_move_with_AB(board, max_depth, player):
    #Manages the minimax algorithm that has alpha beta pruning 
    global move_index
    global move_set_calculated
    max_depth = max_depth + max_depth - 1
    move_index = max_depth
    
    if move_set_calculated == None:
        best_sequence = None
        moves = []
        best_score = float("-inf")
        
        possible_moves = board.generate_possible_moves(player)
    
        original_position_fen = board.generate_fen()
                          
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
    
        row_pieces = []
        board_line = original_position_fen.strip()
        ranks = board_line.split("/")
        for rank in ranks:
            split_strings = [char for char in rank]
            row_pieces.append(split_strings)
            
        for move in possible_moves:
            piece, square_to = move
            board.update(piece, square_to)
            score, sequence = minimax_with_AB(board, 1, False, max_depth, player, float("-inf"), float("inf"), current_sequence=[move])  # Pass first move in the sequence
            board.add_pieces(row_pieces)
            if score > best_score:
                best_score = score
                best_sequence = sequence
        print(best_sequence)
        
        for move in best_sequence:
            piece, square_to = move
            if square_to in board.occupied_squares:
                if piece.piece_type == "p" or piece.piece_type == "P":
                    move_obj = Move(piece, square_to.x, square_to.y, piece.square.x, iscapture=True)
                else:
                    move_obj = Move(piece, square_to.x, square_to.y, iscapture=True)
            else:
                move_obj = Move(piece, square_to.x, square_to.y)
            board.update(piece, square_to)
            moves.append(move_obj)
            
        move_set_calculated = display_moves(board, moves)
        return move_set_calculated
    else:
        return move_set_calculated

def minimax_with_AB(board, depth, isMaximising, max_depth, player, alpha, beta, current_sequence=[]):
    #Minimax with alpha beta pruning
    if depth >= max_depth:
        if current_player == "w":
            player = "b"
        else:
            player = "w"

        if check_game_over(board, player):
            return 100, current_sequence
        else:
            return -100, current_sequence
        
    original_position_fen = board.generate_fen()
    row_pieces = []
    board_line = original_position_fen.strip()
    ranks = board_line.split("/")
    for rank in ranks:
        split_strings = [char for char in rank]
        row_pieces.append(split_strings)

    if isMaximising:
        best_score = float("-inf")
        best_sequence = None
        if current_player == "w":
            player = "w"
        else:
            player = "b"
        
        possible_moves = board.generate_possible_moves(player)
        
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        for move in possible_moves:
            piece, square_to = move
            board.update(piece, square_to)
            score, sequence = minimax_with_AB(board, depth + 1, False, max_depth, player, alpha, beta, current_sequence + [move])
            board.add_pieces(row_pieces)

            if score > best_score:
                best_score = score
                best_sequence = sequence
            alpha = max(alpha, best_score)
            if beta <= alpha:  # Pruning
                break
        return best_score, best_sequence
    
    else:
        best_score = float("inf")
        best_sequence = None
        if current_player == "w":
            player = "b"
        else:
            player = "w"
            
        possible_moves = board.generate_possible_moves(player)
        
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        for move in possible_moves:
            piece, square_to = move
            board.update(piece, square_to)
            score, sequence = minimax_with_AB(board, depth + 1, True, max_depth, player, alpha, beta, current_sequence + [move])
            board.add_pieces(row_pieces)
            
            if score < best_score:
                best_score = score
                best_sequence = sequence
            beta = min(beta, best_score)
            if beta <= alpha:  # Pruning
                break
        return best_score, best_sequence
    
    
def dfs(board, depth, max_depth, player, move, sequence, moves):
    #The DFS search algorithm that recursively calls itself until it reaches the limit
    global move_index
    global move_set_calculated
    
    move_index = max_depth
    
    original_position_fen = board.generate_fen()
    row_pieces = []
    board_line = original_position_fen.strip()
    ranks = board_line.split("/")
    for rank in ranks:
        split_strings = [char for char in rank]
        row_pieces.append(split_strings)
        
    if move_set_calculated == None:
        if depth >= max_depth + max_depth - 1:
            if check_game_over(board, player):
                print(sequence)
                move_set_calculated = display_moves(board, moves)
                return move_set_calculated
            else:
                return None

        possible_moves = board.generate_possible_moves(player)
        
        board_1 = chess.Board(original_position_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        for move in possible_moves:
            piece, square_to = move
            print(move)
            sequence.append(str(move))
            if square_to in board.occupied_squares:
                if piece.piece_type == "p" or piece.piece_type == "P":
                    move_obj = Move(piece, square_to.x, square_to.y, piece.square.x, iscapture=True)
                else:
                    move_obj = Move(piece, square_to.x, square_to.y, iscapture=True)
            else:
                move_obj = Move(piece, square_to.x, square_to.y)
            moves.append(move_obj)
            
            board.update(piece, square_to)
            result = dfs(board, depth + 1, max_depth, "w" if player == "b" else "b", move, sequence, moves)

            if result == None:
                board.add_pieces(row_pieces)
                sequence.pop()
                moves.remove(move_obj)
                
            if depth == max_depth:
                board.captured_pieces = []

            if result is not None:
                return result
        return None
    else:
        return move_set_calculated
    
def bfs(board, max_depth, player):
    global move_set_calculated
    global move_index
    
    move_index = max_depth
    moves = []
    
    if move_set_calculated == None:
        # Initialize BFS with the starting player and first possible move
        possible_moves = board.generate_possible_moves(player)
        current_fen = board.generate_fen()
        board_1 = chess.Board(current_fen + " " + player)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]
        initial_possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
        
        initial_row_pieces = []
        board_line = current_fen.strip()
        ranks = board_line.split("/")
        for rank in ranks:
            split_strings = [char for char in rank]
            initial_row_pieces.append(split_strings)
        
        # Initialize BFS queue with the possible moves
        for move in initial_possible_moves:
            piece, square_to = move
            board.update(piece, square_to)
            temp_player = "b" if player == "w" else "w"
            
            # Queue stores tuples of (board_state, move_sequence)
            queue = deque([(board.generate_fen(), [move], 0, temp_player)])
            visited = set()  # To avoid revisiting the same board states
            best_sequence = None
            
            while queue:
                current_fen, current_sequence, depth, current_player = queue.popleft()
                
                row_pieces = []
                board_line = current_fen.strip()
                ranks = board_line.split("/")
                for rank in ranks:
                    split_strings = [char for char in rank]
                    row_pieces.append(split_strings)
                    
                board.add_pieces(row_pieces)
                
                # Check if we've reached the desired depth and if the game is over
                if depth >= max_depth:
                    if check_game_over(board, current_player):
                        best_sequence = current_sequence
                        print(best_sequence)
                        board.add_pieces(initial_row_pieces)
                        for move in best_sequence:
                            piece, square_to = move
                            if square_to in board.occupied_squares:
                                if piece.piece_type == "p" or piece.piece_type == "P":
                                    move_obj = Move(piece, square_to.x, square_to.y, piece.square.x, iscapture=True)
                                else:
                                    move_obj = Move(piece, square_to.x, square_to.y, iscapture=True)
                            else:
                                move_obj = Move(piece, square_to.x, square_to.y)
                            board.update(piece, square_to)
                            moves.append(move_obj)
                        move_set_calculated = display_moves(board, moves)
                        return move_set_calculated
                    continue  # If max depth reached, continue to explore other branches

                # If the current position is not visited, generate next moves
                if current_fen not in visited:
                    visited.add(current_fen)
                    possible_moves = board.generate_possible_moves(current_player)
                    
                    board_1 = chess.Board(current_fen + " " + current_player)
                    legal_moves_uci = [move.uci() for move in board_1.legal_moves]
                    possible_moves = board.check_for_differences(legal_moves_uci, possible_moves)
                    
                    # Explore all the possible moves for the current player
                    for move in possible_moves:
                        piece, square_to = move
                        board.update(piece, square_to)  # Apply the move
                        next_fen = board.generate_fen()  # Get FEN after the move
                        next_player = "w" if current_player == "b" else "b"
                        queue.append((next_fen, current_sequence + [move], depth + 1, next_player))
                        board.add_pieces(row_pieces)  # Undo the move by restoring FEN

            # After all possible moves have been explored, restore the initial board state
            board.add_pieces(initial_row_pieces)

        return None  # No solution found
    else:
        return move_set_calculated
         
# ______________________________Algorithm clicks checker_________________________________________

def check_algorithm_request(event):
    #To check the areas of left mouse clicks and trigger algorithms
    x, y = event.pos
    if 25 < x < 135 and 610 < y < 660:
        print("Minimax")
        return "Minimax"
    if 165 < x < 325 and 610 < y < 660:
        print("Minimax with Alpha Beta Pruning")
        return "Minimax with AB"
    if 355 < x < 425 and 610 < y < 660:
        print("DFS")
        return "DFS"
    if 455 < x < 530 and 610 < y < 660:
        print("BFS")
        return "BFS"
    if 560 < x < 650 and 610 < y < 660:
        print("Reset")
        return "Reset"
        
# ______________________________FEN parser_________________________________________

def parse_file(file):
    global original_fen
    
    #Parses the textfile and returns the 3 lines separated and formatted
    row_pieces = []
    with open(file, "r") as f:
        lines = f.readlines()

    # Process the board configuration
    board_line = lines[0].strip()
    original_fen = board_line
    ranks = board_line.split("/")

    for rank in ranks:
        split_strings = [char for char in rank]
        row_pieces.append(split_strings)

    # Process the player and number of moves
    player = lines[1].strip()
    number_of_moves = lines[2].strip()
    
    return row_pieces, player, number_of_moves

# ______________________________Image Loader_________________________________________

def load_images():
    #gets the path of the image files and assigns them to the resepctive pieces
    images = {}
    piece_map = {
        'P': 'white pawn.png',
        'R': 'white rook.png',
        'N': 'white knight.png',
        'B': 'white bishop.png',
        'Q': 'white queen.png',
        'K': 'white king.png',
        'p': 'black pawn.png',
        'r': 'black rook.png',
        'n': 'black knight.png',
        'b': 'black bishop.png',
        'q': 'black queen.png',
        'k': 'black king.png',
    }
    for piece, filename in piece_map.items():
        path = os.path.join('assets', 'images', filename)
        image = pygame.image.load(path)
        if piece == 'P' or piece == 'p':
            image = pygame.transform.smoothscale(image, (40, 40))
        elif piece == 'R' or piece == 'r' or piece == 'N' or piece == 'n':
            image = pygame.transform.smoothscale(image, (45, 45))
        else:
            image = pygame.transform.smoothscale(image, (55, 55))
        images[piece] = image
    return images

# ______________________________Main Loop_________________________________________

def main():
    #Main loop
    global move_set_calculated
    global current_player
    global move_index
    global duration
    
    move_set = None
    
    position_file = sys.argv[1]
    
    parsed_file = parse_file(position_file)
    row_pieces = parsed_file[0]
    current_player = parsed_file[1]
    number_of_moves = int(parsed_file[2])
    
    images = load_images()
    board = Board(8, 8, images, screen, row_pieces)
    algorithm = None
    
    board.draw_board()
    board.add_pieces(row_pieces)
    board.draw_pieces()
            
    running = True
    #Main pygame loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    board.display_indexes = not board.display_indexes 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    algorithm = check_algorithm_request(event)
        screen.fill(COLOUR_NAMES["LIGHT_GREY"])
        
        if algorithm == "Minimax":
            start_time = time.time()
            move_set = get_best_move(board, number_of_moves, current_player)
            end_time = time.time()
            if not duration:
                duration_time = round(end_time - start_time, 4)
                duration = True
        
        if algorithm == "BFS":
            start_time = time.time()
            move_set = bfs(board, number_of_moves, current_player)
            end_time = time.time()
            if not duration:
                duration_time = round(end_time - start_time, 4)
                duration = True
            
        if algorithm == "DFS":
            move = None
            sequence = []
            moves = []
            start_time = time.time()
            move_set = dfs(board, 0, number_of_moves, current_player, move, sequence, moves)
            end_time = time.time()
            if not duration:
                duration_time = round(end_time - start_time, 4)
                duration = True
            
        if algorithm == "Minimax with AB":
            start_time = time.time()
            move_set = get_best_move_with_AB(board, number_of_moves, current_player)
            end_time = time.time()
            if not duration:
                duration_time = round(end_time - start_time, 4)
                duration = True
            
        if move_set:
            y_offset = 100  # Initial Y position for moves
            y_step = 40     # Space between rows
            
            x_number_offset = 550  # X position for move numbers
            x_white_move_offset = 570  # X position for White's move
            x_black_move_offset = 635  # X position for Black's move

            move_pairs = []  # To store pairs of moves (White, Black)

            # Group moves into pairs
            for i in range(0, len(move_set), 2):
                white_move = move_set[i]
                black_move = move_set[i + 1] if i + 1 < len(move_set) else None
                move_pairs.append((white_move, black_move))

            # Render each pair of moves
            for row_index, (white_move, black_move) in enumerate(move_pairs):
                # Display the move number and White's move
                move_number = row_index + 1
                screen.blit(font.render(str(move_number), True, COLOUR_NAMES["BLACK"]), (x_number_offset, y_offset + row_index * y_step))
                screen.blit(font.render(str(white_move[0]), True, COLOUR_NAMES["BLACK"]), (x_white_move_offset, y_offset + row_index * y_step))

                # Display Black's move if available
                if black_move:
                    screen.blit(font.render(str(black_move[0]), True, COLOUR_NAMES["BLACK"]), (x_black_move_offset, y_offset + row_index * y_step))

            # Display the time below all moves
            screen.blit(font.render("Time: ", True, COLOUR_NAMES["BLACK"]), (x_number_offset, y_offset + len(move_pairs) * y_step + 20))
            screen.blit(font.render(str(duration_time), True, COLOUR_NAMES["BLACK"]), (620, y_offset + len(move_pairs) * y_step + 20))


        if algorithm == "Reset":
            board.draw_board()
            board.add_pieces(row_pieces)
            board.draw_pieces()
            move_set_calculated = None
            move_set = None
            board.captured_pieces = []
            duration = False
            
        pygame.draw.rect(screen, COLOUR_NAMES["WHITE"], (25, 610, 110, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (25, 610, 110, 50), 1)
        screen.blit(minimax_text_button, (40, 620))
        pygame.draw.rect(screen,COLOUR_NAMES["WHITE"], (165, 610, 160, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (165, 610, 160, 50), 1)
        screen.blit(minimax_with_AB_text_button, (180, 620))
        pygame.draw.rect(screen,COLOUR_NAMES["WHITE"], (355, 610, 70, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (355, 610, 70, 50), 1)
        screen.blit(DFS_text_button, (370, 620))
        pygame.draw.rect(screen,COLOUR_NAMES["WHITE"], (455, 610, 75, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (455, 610, 75, 50), 1)
        screen.blit(BFS_text_button, (470, 620))
        pygame.draw.rect(screen,COLOUR_NAMES["WHITE"], (560, 610, 90, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (560, 610, 90, 50), 1)
        screen.blit(reset_text_button, (575, 620))
        board.draw_board()
        for piece in board.pieces:
            piece.draw(screen)
        if board.display_indexes:
            board.draw_indexes()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
