from graphics import COLOUR_NAMES
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'  # Hides welcome message of pygame
import pygame
import sys
import random
import time
from move import Move
from board import Board

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
Dumbo_text_button = font.render('Dumbo', True, COLOUR_NAMES["BLACK"])
reset_text_button = font.render('Reset', True, COLOUR_NAMES["BLACK"])
running = False
paused = False
move_set_calculated = None
current_player = None
game_status = None
move_index = None
duration = False
normal_move = False
capture_move = False    

# ______________________________Checkmate checker_________________________________________

def check_game_over(board, player):
    #Check if checkmate or stalemate
    possible_moves = board.generate_possible_moves(player)
    #print(board.pieces) -- for debugging
    #print(king_in_check) -- for debugging
    if not possible_moves and board.king_in_check:
        return True
    else:
        return False 

# ______________________________Search algorithms_________________________________________

def get_best_move(board, max_depth, player):
    #manage the minimax algorithm and return the best sequence of moves
    global move_index
    global move_set_calculated
    
    move_index = max_depth
    
    if move_set_calculated == None:
        move_set = []
        best_sequence = None
        moves = []
        best_score = float("-inf")
        possible_moves = board.generate_possible_moves(player)
        
        for move in possible_moves:
            piece, square_to = move
            print("FIRST MOVE ", move, 0)
            original_piece_square = piece.square
            board.update(piece, square_to)
            score, sequence = minimax(board, 0, False, max_depth, player, current_sequence=[move])  # Pass first move in the sequence
            board.undo_to_previous(piece, original_piece_square, square_to)
            print("ORIGINAL POSITION ", board.pieces)
            if score > best_score:
                best_score = score
                best_sequence = sequence
        print(best_sequence)
        
        count = 1
        count_pos_x = 550
        count_pos_y = 100
        pos_x = 570
        pos_y = 100
        for move in best_sequence:
            piece, square_to = move
            for p in board.pieces:
                if p == piece:
                    p.square = square_to
            if square_to in board.occupied_squares:
                if piece.piece_type == "p" or piece.piece_type == "P":
                    move_obj = Move(piece.piece_type, square_to.x, square_to.y, piece.square.x, iscapture=True)
                else:
                    move_obj = Move(piece.piece_type, square_to.x, square_to.y, iscapture=True)
            else:
                move_obj = Move(piece.piece_type, square_to.x, square_to.y)
            moves.append(move_obj)
            
        for move in moves:
            board.draw_board()
            for piece in board.pieces:
                piece.draw(screen)
            pygame.display.flip()
            screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
            screen.blit(font.render(str(moves[0]), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
            screen.blit(font.render(str(moves[1]), True, COLOUR_NAMES["BLACK"]), (pos_x + 70,pos_y))
            screen.blit(font.render(str(moves[2]) + "#", True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y + 60))
            move_set.append((str(moves[0]), 570, 100))
            move_set.append((str(moves[1]), 640, 100))
            move_set.append((str(moves[2]) + "#", 570, 160))
            move_set_calculated = move_set
            return move_set
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

    if isMaximising:
        best_score = float("-inf")
        best_sequence = None
        if current_player == "w":
            player = "w"
        else:
            player = "b"
        
        for move in board.generate_possible_moves(player):
            piece, square_to = move
            original_piece_square = piece.square
            #Vital area: update move, recursively call minimax with the new board state and player, and undo the move once returned
            board.update(piece, square_to)
            score, sequence = minimax(board, depth + 1, False, max_depth, player, current_sequence + [move])
            board.undo_to_previous(piece, original_piece_square, square_to)
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
        
        for move in board.generate_possible_moves(player):
            piece, square_to = move
            original_piece_square = piece.square
            #Vital area: update move, recursively call minimax with the new board state and player, and undo the move once returned
            board.update(piece, square_to)
            score, sequence = minimax(board, depth + 1, True, max_depth, player, current_sequence + [move])
            board.undo_to_previous(piece, original_piece_square, square_to)
            if score < best_score:
                best_score = score
                best_sequence = sequence
        return best_score, best_sequence
    
def get_best_move_with_AB(board, max_depth, player):
    #Manages the minimax algorithm that has alpha beta pruning 
    global move_index
    global move_set_calculated
    
    move_index = max_depth
    
    if move_set_calculated == None:
        move_set = []
        best_sequence = None
        moves = []
        best_score = float("-inf")
        possible_moves = board.generate_possible_moves(player)
        
        for move in possible_moves:
            piece, square_to = move
            #print("FIRST MOVE ", move, 0)
            original_piece_square = piece.square
            board.update(piece, square_to)
            score, sequence = minimax_with_AB(board, 0, False, max_depth, player, float("-inf"), float("inf"), current_sequence=[move])  # Pass first move in the sequence
            board.undo_to_previous(piece, original_piece_square, square_to)
            #print("ORIGINAL POSITION ", board.pieces)
            if score > best_score:
                best_score = score
                best_sequence = sequence
        print(best_sequence)
        
        count = 1
        count_pos_x = 550
        count_pos_y = 100
        pos_x = 570
        pos_y = 100
        for move in best_sequence:
            piece, square_to = move
            for p in board.pieces:
                if p == piece:
                    p.square = square_to
            if square_to in board.occupied_squares:
                if piece.piece_type == "p" or piece.piece_type == "P":
                    move_obj = Move(piece.piece_type, square_to.x, square_to.y, piece.square.x, iscapture=True)
                else:
                    move_obj = Move(piece.piece_type, square_to.x, square_to.y, iscapture=True)
            else:
                move_obj = Move(piece.piece_type, square_to.x, square_to.y)
            moves.append(move_obj)
            
        for move in moves:
            board.draw_board()
            for piece in board.pieces:
                piece.draw(screen)
            pygame.display.flip()
            screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
            screen.blit(font.render(str(moves[0]), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
            screen.blit(font.render(str(moves[1]), True, COLOUR_NAMES["BLACK"]), (pos_x + 70,pos_y))
            screen.blit(font.render(str(moves[2]) + "#", True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y + 60))
            move_set.append((str(moves[0]), 570, 100))
            move_set.append((str(moves[1]), 640, 100))
            move_set.append((str(moves[2]) + "#", 570, 160))
            move_set_calculated = move_set
            return move_set
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

    if isMaximising:
        best_score = float("-inf")
        best_sequence = None
        if current_player == "w":
            player = "w"
        else:
            player = "b"
        
        for move in board.generate_possible_moves(player):
            piece, square_to = move
            original_piece_square = piece.square
            board.update(piece, square_to)
            score, sequence = minimax(board, depth + 1, False, max_depth, player, alpha, beta, current_sequence + [move])
            board.undo_to_previous(piece, original_piece_square, square_to)
            best_score = max(score, best_score)
            best_sequence = sequence
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_sequence
    
    else:
        best_score = float("inf")
        best_sequence = None
        if current_player == "w":
            player = "b"
        else:
            player = "w"
        
        for move in board.generate_possible_moves(player):
            piece, square_to = move
            original_piece_square = piece.square
            board.update(piece, square_to)
            score, sequence = minimax(board, depth + 1, True, max_depth, player, current_sequence + [move])
            board.undo_to_previous(piece, original_piece_square, square_to)
            best_score = max(score, best_score)
            best_sequence = sequence
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_sequence
    
    
def dfs(board, depth, max_depth, player, move, sequence, moves):
    #The DFS search algorithm that recursively calls itself until it reaches the limit
    global move_index
    global move_set_calculated

    move_index = max_depth
    if move_set_calculated == None:
        if depth == max_depth+1:
            if check_game_over(board, player):
                print(sequence)
                move_set = []
                count = 1
                count_pos_x = 550
                count_pos_y = 100
                pos_x = 570
                pos_y = 100
                for move in moves:
                    board.draw_board()
                    for piece in board.pieces:
                        piece.draw(screen)
                    pygame.display.flip()
                screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
                screen.blit(font.render(str(moves[0]), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
                screen.blit(font.render(str(moves[1]), True, COLOUR_NAMES["BLACK"]), (pos_x + 70,pos_y))
                screen.blit(font.render(str(moves[2]) + "#", True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y + 60))
                move_set.append((str(moves[0]), 570, 100))
                move_set.append((str(moves[1]), 640, 100))
                move_set.append((str(moves[2]) + "#", 570, 160))
                move_set_calculated = move_set
                return move_set
            else:
                return None

        possible_moves = board.generate_possible_moves(player)
        for move in possible_moves:
            piece, square_to = move
            sequence.append(str(move))
            if square_to in board.occupied_squares:
                if piece.piece_type == "p" or piece.piece_type == "P":
                    move_obj = Move(piece.piece_type, square_to.x, square_to.y, piece.square.x, iscapture=True)
                else:
                    move_obj = Move(piece.piece_type, square_to.x, square_to.y, iscapture=True)
            else:
                move_obj = Move(piece.piece_type, square_to.x, square_to.y)
            moves.append(move_obj)
            #pygame.time.delay(1000)
            original_piece_square = piece.square
            board.update(piece, square_to)
            result = dfs(board, depth + 1, max_depth, "w" if player == "b" else "b", move, sequence, moves)

            if result == None:
                board.undo_to_previous(piece, original_piece_square, square_to)
                sequence.pop()
                moves.remove(move_obj)
                
            if depth == 2:
                board.captured_pieces = []

            if result is not None:
                return result
        return None
    else:
        return move_set_calculated

def dumbo(board, current_player, number_of_moves):
    #The dumb AI that returns the move that captures the most valuable piece if possible else if no captures returns a random move
    global move_set_calculated
    global game_status
    global move_index
    
    count = 1
    count_pos_x = 550
    count_pos_y = 100
    return_set = []
    pos_x = 570
    pos_y = 100
    number_of_moves *= 2
    
    if move_set_calculated == None:
        for move_number in range(number_of_moves):
            
            possible_moves = board.generate_possible_moves(current_player)
            if current_player == "w":
                current_player = "b"
            else:
                current_player = "w"

            highest_valued_piece_capturable, status, iscapture = get_highest_valued_piece_capturable(board, possible_moves)
            
            #pygame.time.delay(1000)
            print(highest_valued_piece_capturable)
            
            piece, square = highest_valued_piece_capturable
            if status == "capture":
                original_piece_x = piece.square.x
            if iscapture:
                if piece.piece_type == "P" or piece.piece_type == "p":
                    piece_to = None
                    for p in board.pieces:
                        if p.square == square:
                            piece_to = p
                            
                    if piece_to:
                        board.capture(piece, piece_to)
                        
                    moves = board.generate_possible_moves(current_player)
                    if not moves and board.king_in_check:
                        print(highest_valued_piece_capturable)
                        print(piece, square)
                        move = Move(piece.piece_type, square.x, square.y, original_piece_x, iscapture=True, ischeckmate=True)
                        break
                    elif not moves and not board.king_in_check:
                        print(highest_valued_piece_capturable)
                        print(piece, square)
                        move = Move(piece.piece_type, square.x, square.y, original_piece_x, iscapture=True)
                        break
                    else:
                        print(piece, square)
                        move = Move(piece.piece_type, square.x, square.y, original_piece_x, iscapture=True)
                else:
                    piece_to = None
                    for p in board.pieces:
                        if p.square == square:
                            piece_to = p
                            
                    if piece_to:
                        board.capture(piece, piece_to)
                        
                    moves = board.generate_possible_moves(current_player)
                    if not moves and board.king_in_check:
                        print(highest_valued_piece_capturable)
                        move = Move(piece.piece_type, square.x, square.y, iscapture=True, ischeckmate=True)
                        break
                    elif not moves and not board.king_in_check:
                        print(highest_valued_piece_capturable)
                        move = Move(piece.piece_type, square.x, square.y, iscapture=True)
                        break
                    else:
                        move = Move(piece.piece_type, square.x, square.y, iscapture=True)
            else:
                board.update(piece, square)
                moves = board.generate_possible_moves(current_player)
                move = Move(piece.piece_type, square.x, square.y)
                if not moves and board.king_in_check:
                    print("Checkmate!")
                    move = Move(piece.piece_type, square.x, square.y, ischeckmate=True)
                    screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
                    screen.blit(font.render(str(move), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
                    return_set.append((move, pos_x, pos_y))
                    move_set_calculated = return_set
                    move_index = move_number
                    return return_set
                elif not moves and not board.king_in_check:
                    print("Stalemate!")
                    move = Move(piece.piece_type, square.x, square.y)
                    screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
                    screen.blit(font.render(str(move), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
                    return_set.append((move, pos_x, pos_y))
                    move_set_calculated = return_set
                    move_index = move_number
                    return return_set
                else:
                    move = Move(piece.piece_type, square.x, square.y)
                    
            return_set.append((move, pos_x, pos_y))
                                       
            board.draw_board()
            for piece in board.pieces:
                piece.draw(screen)
            
            screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
            screen.blit(font.render(str(move), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
            
            pygame.display.flip()
            
            if move_number == 0 or move_number == 2 or move_number == 4:
                pos_x += 70
            else:
                count += 1
                count_pos_y += 60
                pos_x = 570
                pos_y += 60
                
        move_set_calculated = return_set
        move_index = move_number
        return return_set
    else:
        return move_set_calculated

def get_highest_valued_piece_capturable(board, possible_moves):
    # Checks the value of each piece capturable and returns the one that captures the highest
    pieces = []
    piece_values = {
        'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
        'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0
    }
    capturable_moves_tuples = []
    
    for move in possible_moves:
        piece, square_to = move
        for piece in board.pieces:
            if square_to == piece.square:
                pieces.append((move,piece))
                
    for piece in pieces:
        move, p = piece
        score = piece_values[p.piece_type]
        capturable_moves_tuples.append((move,score))
        
    max_score = 0
    best_moves = []
    for moves in capturable_moves_tuples:
        move, score = moves
        if (score >= max_score):
            if best_moves:
                if (score > max_score):
                    max_score = score
                    best_moves.pop(0)
                    best_moves.append(move)
                else:
                    max_score = score
                    best_moves.append(move)
            else:
                max_score = score
                best_moves.append(move)
    
    if len(best_moves) > 1:
        return (random.choice(best_moves), "capture", True)
    elif not best_moves: #No captures
        if possible_moves:
            return (random.choice(possible_moves), "not checkmate", False)
        else:
            if board.king_in_check:
                return ("Checkmate!", "checkmate", False)
            else:
                return ("Draw!", "draw", False)
    else:
        return (best_moves[0], "capture", True)
     
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
    if 455 < x < 550 and 610 < y < 660:
        print("Dumbo")
        return "Dumbo"
    if 580 < x < 670 and 610 < y < 660:
        print("Reset")
        return "Reset"
        
# ______________________________FEN parser_________________________________________

def parse_file(file):
    #Parses the textfile and returns the 3 lines separated and formatted
    row_pieces = []
    with open(file, "r") as f:
        lines = f.readlines()

    # Process the board configuration
    board_line = lines[0].strip()
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
    global game_status
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
        
        if algorithm == "Dumbo":
            start_time = time.time()
            move_set = dumbo(board, current_player, number_of_moves)
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
            #Render moves for each algorithm
            for set in move_set:
                move, x, y = set
                if number_of_moves == 1:
                    screen.blit(font.render(str(move), True, COLOUR_NAMES["BLACK"]), (x,y))
                    screen.blit(font.render(str(1), True, COLOUR_NAMES["BLACK"]), (550,100))
                elif number_of_moves == 2:
                    screen.blit(font.render(str(move), True, COLOUR_NAMES["BLACK"]), (x,y))
                    screen.blit(font.render(str(1), True, COLOUR_NAMES["BLACK"]), (550,100))
                    screen.blit(font.render(str(2), True, COLOUR_NAMES["BLACK"]), (550,160))
                    if move_index > 1:
                        screen.blit(font.render(str(2), True, COLOUR_NAMES["BLACK"]), (550,160))
            screen.blit(font.render("Time: ", True, COLOUR_NAMES["BLACK"]), (550, 220))
            screen.blit(font.render(str(duration_time), True, COLOUR_NAMES["BLACK"]), (620, 220))
        
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
        pygame.draw.rect(screen,COLOUR_NAMES["WHITE"], (455, 610, 95, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (455, 610, 95, 50), 1)
        screen.blit(Dumbo_text_button, (470, 620))
        pygame.draw.rect(screen,COLOUR_NAMES["WHITE"], (580, 610, 90, 50))
        pygame.draw.rect(screen, COLOUR_NAMES["BLACK"], (580, 610, 90, 50), 1)
        screen.blit(reset_text_button, (595, 620))
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
