from graphics import COLOUR_NAMES
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'  # Hides welcome message of pygame
import pygame
import sys
import random
import time

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
display_indexes = False
running = False
paused = False
move_set_calculated = None
current_player = None
king_in_check = False
game_status = None
move_index = None
duration = False
normal_move = False
capture_move = False

# ______________________________Classes_________________________________________

class Move:
    """Move class containing the piece type, x and y coordinates and if the move is a capture/checkmate.
    Returns a string in chess annotation form.
    Eg: Ng5, bxc6
    """
    def __init__(self, piece, x, y, from_x = None, iscapture = False, ischeckmate = False):
        self.piece = piece
        self.x = x
        self.y = y
        self.capture = iscapture
        self.checkmate = ischeckmate
        self.from_x = from_x
        
    def __repr__(self):
        if self.x == 0:
            to_x = "a"
        elif self.x == 1:
            to_x = "b"
        elif self.x == 2:
            to_x = "c"
        elif self.x == 3:
            to_x = "d"  
        elif self.x == 4:
            to_x = "e"
        elif self.x == 5:
            to_x = "f" 
        elif self.x == 6:
            to_x = "g"
        elif self.x == 7:
            to_x = "h"   
            
        if self.from_x == 0:
            from_x = "a"
        elif self.from_x == 1:
            from_x = "b"
        elif self.from_x == 2:
            from_x = "c"
        elif self.from_x == 3:
            from_x = "d"  
        elif self.from_x == 4:
            from_x = "e"
        elif self.from_x == 5:
            from_x = "f" 
        elif self.from_x == 6:
            from_x = "g"
        elif self.from_x == 7:
            from_x = "h"      
            
        if not self.capture and not self.checkmate and (self.piece == "p" or self.piece == "P"):
            return f"{to_x}{self.y+1}"
        if not self.capture and not self.checkmate and (self.piece != "p" or self.piece != "P"):
            return f"{self.piece}{to_x}{self.y+1}"
        if self.capture and not self.checkmate and (self.piece == "p" or self.piece == "P"):
            return f"{from_x}x{to_x}{self.y+1}"
        if self.capture and not self.checkmate and (self.piece != "p" or self.piece != "P"):
            return f"{self.piece}x{to_x}{self.y+1}"
        if not self.capture and self.checkmate and (self.piece != "p" or self.piece != "P"):
            return f"{self.piece}{to_x}{self.y+1}#"
        
class Square:
    """Square class containing the x, y coordinates and the index of the square.
    Returns a string with a clear idea of the Square coordinates and index.
    Eg: <Square (1, 5, 42)>
    """
    def __init__(self, x, y, idx):
        self.x = x
        self.y = y
        self.idx = idx
        self.size = 70

    def __repr__(self):
        return f"<Square ({self.x}, {self.y}, {self.idx})>"
          
    def __eq__(self, other):
        if isinstance(other, Square):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        return hash((self.x, self.y, self.idx))
    
    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

class Piece:
    """Piece class containing the piece_type, color, square object and the relevant path to the image representing it.
    Returns a string showing the piece type and the square it is in.
    Eg: Piece (K, <Square (2, 7, 59)>)
    """
    def __init__(self, piece_type, color, square, images):
        self.piece_type = piece_type
        self.color = color
        self.square = square
        self.image = images[piece_type]
        self.size = 65  # Square size
    
    def draw(self, screen):
        x = self.square.x
        y = 7 - self.square.y
        # Calculate the center of the square for placing the piece
        square_center = (GAP + self.size * x + self.size // 2, GAP + self.size * y + self.size // 2)
        # Adjust the image position to center it on the square
        image_rect = self.image.get_rect(center=square_center)
        screen.blit(self.image, image_rect)
        
    def __repr__(self):
        return f"Piece ({self.piece_type}, {self.square})"
    
    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.square == other.square
        return False
    
    
class Board:
    """The main object in this project. Board class containing the rows, columns, images, fen position and most of the main functions.
    """
    def __init__(self, rows, columns, images, fen):
        self.rows = rows
        self.columns = columns
        self.squares = []
        self.occupied_squares = []
        self.square_size = 65
        self.colors = [COLOUR_NAMES["LIGHT_WHITE"], COLOUR_NAMES["LIGHT_GREEN"]]
        self.pieces = []
        self.images = images
        self.initial_fen = fen
        self.captured_piece = None
        self.captured_pieces = []
        self.add_squares()

    def add_squares(self):
        #Adds all the squares with the necessary values to the Board's list of squares.
        idx = 1
        for y in range(self.columns):
            for x in range(self.rows):
                square = Square(x, y, idx)
                self.squares.append(square)
                idx += 1
            
    def draw_board(self):
        #Draws the board
        border_width = 2
        width = self.square_size * self.rows
        height = self.square_size * self.columns
        for row in range(self.rows):
            for col in range(self.columns):
                color = self.colors[(row + col) % 2]
                pygame.draw.rect(screen, color, [GAP + col * self.square_size, GAP + row * self.square_size, self.square_size, self.square_size])
                       
        for row in range(self.rows + 1):
            pygame.draw.line(screen, COLOUR_NAMES["BLACK"], (GAP, GAP + row * self.square_size), (GAP + width, GAP + row * self.square_size), border_width)
        
        for col in range(self.columns + 1):
            pygame.draw.line(screen, COLOUR_NAMES["BLACK"], (GAP + col * self.square_size, GAP), (GAP + col * self.square_size, GAP + height), border_width)
        
        for i in range(8):
            rank_text = font.render(str(8 - i), True, COLOUR_NAMES["BLACK"])
            file_text = font.render(chr(ord('a') + i), True, COLOUR_NAMES["BLACK"])
            screen.blit(rank_text, (5, GAP + i * self.square_size + self.square_size // 2 - rank_text.get_height() // 2))
            screen.blit(file_text, (GAP + i * self.square_size + self.square_size // 2 - file_text.get_width() // 2, GAP + height + GAP // 4))


    def add_pieces(self, row_pieces):
        #Add all pieces to the Board's list of pieces
        self.pieces = []
        self.occupied_squares = []  # Clear the list of occupied squares
        for y, rank in enumerate(row_pieces):
            x = 0
            for char in rank:
                if char.isdigit():
                    x += int(char)
                else:
                    for square in self.squares:
                        if square.x == x and square.y == 7 - y:
                            sqr = square
                            break
                    piece = Piece(char, "white" if char.isupper() else "black", sqr, self.images)
                    self.pieces.append(piece)
                    self.occupied_squares.append(sqr)
                    x += 1
        
    def draw_pieces(self):      
        #Draw the pieces          
        for piece in self.pieces:
            piece.draw(screen)
            
    def draw_indexes(self):
        #Draw the indexes of each box if toggled. (Press 'i')
        if display_indexes:
            for square in self.squares:
                idx_text = font.render(str(square.idx), True, COLOUR_NAMES["BLACK"])
                text_rect = idx_text.get_rect(center=(GAP + square.x * self.square_size + self.square_size // 2, GAP + (7 - square.y) * self.square_size + self.square_size // 2))
                screen.blit(idx_text, text_rect)
                
    def capture(self, piece_from, piece_to):
        #Process a capture
        #print("CAPTURE") -- debugging purposes
        piece_to_square = piece_to.square
        piece_from_square = piece_from.square
        self.captured_pieces.append(piece_to) 
        self.occupied_squares.remove(piece_from_square)
        self.pieces.remove(piece_to)
        self.pieces.remove(piece_from)
        piece_from.square = piece_to_square
        
        self.pieces.append(piece_from)
        self.captured_piece = piece_to
        
    def update(self, piece_from, square_to):
        #update all data when a move is made
        if square_to in self.occupied_squares:
            #handle captures
            for piece_to in self.pieces:
                if piece_to.square == square_to:
                    #print("UPDATECAPUTRE")
                    self.capture(piece_from, piece_to)
                    break
        else:
            #print("NORMAL MOVE UPDATE")
            #normal move
            self.occupied_squares.remove(piece_from.square)
            self.pieces.remove(piece_from)
            piece_from.square = square_to
            self.pieces.append(piece_from)
            self.occupied_squares.append(piece_from.square)
    
    def undo_to_previous(self, piece, original_piece_square, square_to):
        #undo a move
        if self.captured_piece:
            if self.captured_piece.square == square_to:
                self.occupied_squares.remove(piece.square)
                self.occupied_squares.append(self.captured_piece.square)
                self.pieces.append(self.captured_piece)
                self.pieces.remove(piece)
                piece.square = original_piece_square
                self.pieces.append(piece)
                self.occupied_squares.append(piece.square)
                self.captured_piece = None
            else:
                self.occupied_squares.remove(piece.square)
                self.pieces.remove(piece)
                piece.square = original_piece_square
                self.pieces.append(piece)
                self.occupied_squares.append(piece.square)
        else:
            if piece in self.captured_pieces and piece not in self.pieces:
                #print("CAPTURED PIECES:  ", self.captured_pieces)
                #print("ADDING PIECE CAPTURED BACK ", piece)
                self.pieces.append(piece)
                self.occupied_squares.append(piece.square)
                for p in self.captured_pieces:
                    if p == piece:
                        self.captured_pieces.remove(p)
                #print("CAPTURED PIECES:  ", self.captured_pieces)
                #pygame.time.delay(10000)
            else:
                self.occupied_squares.remove(piece.square)
                self.pieces.remove(piece)
                piece.square = original_piece_square
                self.pieces.append(piece)
                self.occupied_squares.append(piece.square)
                                                            
    def generate_fen(self):
        #Generates a fen string of the current position. Not used but was very helpful when debugging. 
        fen = ''
        empty_count = 0

        for y in range(7, -1, -1):  #Iterate from the highest rank to the lowest
            for x in range(8):
                piece_found = False
                for piece in self.pieces:
                    if piece.square.x == x and piece.square.y == y:
                        if empty_count > 0:
                            fen += str(empty_count)
                            empty_count = 0
                        fen += piece.piece_type
                        piece_found = True
                        break
                if not piece_found:
                    empty_count += 1

            if empty_count > 0:
                fen += str(empty_count)
                empty_count = 0

            if y != 0:
                fen += '/'

        return fen

     
# ______________________________Valid move checker_________________________________________

def generate_possible_moves(board, current_player):
    """The most vital function in this project.
    Generates a list of all possible moves at a given position.
    """
    global king_in_check
    
    #Empty lists that will contain very import data
    possible_moves = []     
    opponent_king_squares = []
    opponent_attacking_squares = []
    all_attacking_squares = []
    possible_moves_in_chess_notation = []
    pieces_saying_check = []
    captured_piece = None

    #Function to check if a square is attacked by the opponent
    def is_square_attacked(square, opponent_moves):
        return any(attack_square == square for attack_square in opponent_moves)
    
    #Add the squares adjacent to the opponent's king
    for piece in board.pieces:
        if piece.piece_type.lower() == "k" and ((current_player == 'w' and piece.color == 'black') or (current_player == 'b' and piece.color == 'white')):
            opponent_king_moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in opponent_king_moves:
                x = piece.square.x + dx
                y = piece.square.y + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    opponent_king_squares.append(Square(x, y, y * 8 + x + 1))
                    
    
    
    def get_attacking_squares():
        #Determine all possible attacking moves of the opponent
        for piece in board.pieces:
            if (current_player == 'w' and piece.color == 'black') or (current_player == 'b' and piece.color == 'white'):
                if piece.piece_type.lower() in ["r", "n", "b", "q", "p"]:
                    directions = {
                        'r': [(0, 1), (1, 0), (0, -1), (-1, 0)],
                        'n': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
                        'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'q': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'p': [(1, -1), (-1, -1)] if piece.color == 'black' else [(1, 1), (-1, 1)]
                    }[piece.piece_type.lower()]

                    for dx, dy in directions:
                        x, y = piece.square.x, piece.square.y
                        while True:
                            x += dx
                            y += dy
                            if 0 <= x < 8 and 0 <= y < 8:
                                next_square = Square(x, y, y * 8 + x + 1)
                                for p in board.pieces:
                                    if p.square == next_square:
                                        attacking_piece = piece
                                        all_attacking_squares.append((attacking_piece, next_square))

                                opponent_attacking_squares.append(next_square)
                                if piece.piece_type.lower() in ['n', 'p']:
                                    break  #Knights and pawns move only once in each direction
                                if next_square in board.occupied_squares:
                                    break  #Stop if an occupied square is encountered
                            else:
                                break
                            
    get_attacking_squares()

    # Find the current player's king
    current_king = None
    for piece in board.pieces:
        if piece.piece_type.lower() == "k" and ((current_player == 'w' and piece.color == 'white') or (current_player == 'b' and piece.color == 'black')):
            current_king = piece
            break
                
    def if_check(square, opponent_moves):
        #Check if the king is in check and returns the bool
        for attack_square in opponent_moves:
            attacking_piece, s = attack_square
            if s == square:
                pieces_saying_check.append(attacking_piece)
                king_in_check = True
                return True
        king_in_check = False
        return False
    
    king_in_check = if_check(current_king.square, all_attacking_squares)
        
    def can_capture_checking_piece(piece):
        # Check if the checking piece can be captured
        for checking_piece in pieces_saying_check:
            if checking_piece.piece_type == piece.piece_type and checking_piece.square == piece.square:
                return True

        return False

    def can_move_resolve_check(move):
        # Temporary apply the move
        original_square = move[0].square
        target_square = move[1]
        piece = move[0]

        board.occupied_squares.remove(original_square)
        piece.square = target_square
        board.occupied_squares.append(target_square)

        # Recalculate opponent attacking squares after the move
        recalculated_opponent_attacking_squares = []
        for opponent_piece in board.pieces:
            if (current_player == 'w' and opponent_piece.color == 'black') or (current_player == 'b' and opponent_piece.color == 'white'):
                if opponent_piece.piece_type.lower() in ["r", "n", "b", "q", "p"]:
                    directions = {
                        'r': [(0, 1), (1, 0), (0, -1), (-1, 0)],
                        'n': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
                        'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'q': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'p': [(1, -1), (-1, -1)] if opponent_piece.color == 'black' else [(1, 1), (-1, 1)]
                    }[opponent_piece.piece_type.lower()]

                    for dx, dy in directions:
                        x, y = opponent_piece.square.x, opponent_piece.square.y
                        while True:
                            x += dx
                            y += dy
                            if 0 <= x < 8 and 0 <= y < 8:
                                next_square = Square(x, y, y * 8 + x + 1)
                                recalculated_opponent_attacking_squares.append(next_square)
                                if opponent_piece.piece_type.lower() in ['n', 'p']:
                                    break  # Knights and pawns move only once in each direction
                                if next_square in board.occupied_squares:
                                    break  #Stopp if an occupied square is encountered
                            else:
                                break

        #Check if the king is still in check
        king_safe = not is_square_attacked(current_king.square, recalculated_opponent_attacking_squares)

        # Revert the move
        board.occupied_squares.remove(target_square)
        piece.square = original_square
        board.occupied_squares.append(original_square)

        return king_safe

    # Generate possible moves for the current player
    for piece in board.pieces:
        if (current_player == 'w' and piece.color == 'white') or (current_player == 'b' and piece.color == 'black'):
            if piece.piece_type == "p":  # black pawn
                # Move forward
                forward_square = Square(piece.square.x, piece.square.y - 1, piece.square.idx - 8)
                if forward_square not in board.occupied_squares:
                    move = (piece, forward_square)
                    if (not king_in_check or can_move_resolve_check(move)):
                        possible_moves.append((piece, forward_square))
                        possible_moves_in_chess_notation.append(Move(piece.piece_type, piece.square.x, piece.square.y - 1))

                # Capture left
                if piece.square.x > 0:
                    capture_left_square = Square(piece.square.x - 1, piece.square.y - 1, piece.square.idx - 9)
                    if capture_left_square in [p.square for p in board.pieces if p.color == "white"]:
                        move = (piece, capture_left_square)
                        for p in board.pieces:
                            if p.square == capture_left_square:
                                captured_piece = p
                        if captured_piece != None and (not king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                            possible_moves.append((piece, capture_left_square))
                            possible_moves_in_chess_notation.append(Move(piece.piece_type, piece.square.x - 1, piece.square.y - 1, piece.square.x, True))

                # Capture right
                if piece.square.x < 7:
                    capture_right_square = Square(piece.square.x + 1, piece.square.y - 1, piece.square.idx - 7)
                    if capture_right_square in [p.square for p in board.pieces if p.color == "white"]:
                        move = (piece, capture_right_square)
                        for p in board.pieces:
                            if p.square == capture_right_square:
                                captured_piece = p
                        if captured_piece != None and (not king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                            possible_moves_in_chess_notation.append(Move(piece.piece_type, piece.square.x + 1, piece.square.y - 1, piece.square.x, True))
                            
            elif piece.piece_type == "P":  # white pawn
                # Move forward
                forward_square = Square(piece.square.x, piece.square.y + 1, piece.square.idx + 8)
                if forward_square not in board.occupied_squares:
                    move = (piece, forward_square)
                    if (not king_in_check or can_move_resolve_check(move)):
                        possible_moves.append((piece, forward_square))
                        possible_moves_in_chess_notation.append(Move(piece.piece_type, piece.square.x, piece.square.y + 1))

                # Capture left
                if piece.square.x > 0:
                    capture_left_square = Square(piece.square.x - 1, piece.square.y + 1, piece.square.idx + 7)
                    if capture_left_square in [p.square for p in board.pieces if p.color == "black"]:
                        move = (piece, capture_left_square)
                        for p in board.pieces:
                            if p.square == capture_left_square:
                                captured_piece = p
                                if captured_piece != None and (not king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                    possible_moves.append((piece, capture_left_square))
                                    possible_moves_in_chess_notation.append(Move(piece.piece_type, piece.square.x - 1, piece.square.y + 1, piece.square.x, True))

                # Capture right
                if piece.square.x < 7:
                    capture_right_square = Square(piece.square.x + 1, piece.square.y + 1, piece.square.idx + 9)
                    if capture_right_square in [p.square for p in board.pieces if p.color == "black"]:
                        move = (piece, capture_right_square)
                        for p in board.pieces:
                            if p.square == capture_right_square:
                                captured_piece = p
                                if captured_piece != None and (not king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                    possible_moves.append((piece, capture_right_square))
                                    possible_moves_in_chess_notation.append(Move(piece.piece_type, piece.square.x + 1, piece.square.y + 1, piece.square.x, True))
                                        
            elif piece.piece_type.lower() in ["r", "n", "b", "q"]:  # rooks, knights, bishops, queens
                directions = {
                    'r': [(0, 1), (1, 0), (0, -1), (-1, 0)],  # Rook directions
                    'n': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],  # Knight moves
                    'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],  # Bishop directions
                    'q': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # Queen directions
                }[piece.piece_type.lower()]

                for dx, dy in directions:
                    x, y = piece.square.x, piece.square.y
                    while True:
                        x += dx
                        y += dy
                        if 0 <= x < 8 and 0 <= y < 8:
                            next_square = Square(x, y, y * 8 + x + 1)
                            move = (piece, next_square)
                            if next_square not in board.occupied_squares:
                                if (not king_in_check or can_move_resolve_check(move)):
                                    possible_moves.append((piece, next_square))
                                    possible_moves_in_chess_notation.append(Move(piece.piece_type, x, y))
                                if piece.piece_type.lower() == 'n':  # Knights move only once in each direction
                                    break
                            else:
                                # Capture an opponent's piece
                                if next_square in [p.square for p in board.pieces if p.color != piece.color]:
                                    for p in board.pieces:
                                        if p.square == next_square:
                                            captured_piece = p
                                    if captured_piece != None and (not king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                        possible_moves.append((piece, next_square))
                                        possible_moves_in_chess_notation.append(Move(piece.piece_type, x, y, iscapture=True))
                                break
                        else:
                            break

            elif piece.piece_type.lower() == "k":  # both color kings
                king_moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # All adjacent squares
                for dx, dy in king_moves:
                    x = piece.square.x + dx
                    y = piece.square.y + dy
                    if 0 <= x < 8 and 0 <= y < 8:
                        next_square = Square(x, y, y * 8 + x + 1)
                        move = (piece, next_square)
                        if next_square not in board.occupied_squares and next_square not in opponent_king_squares and not is_square_attacked(next_square, opponent_attacking_squares):
                            if (not king_in_check or can_move_resolve_check(move)):
                                possible_moves.append((piece, next_square))
                                possible_moves_in_chess_notation.append(Move(piece.piece_type, x, y))
                        else:
                            # Capture an opponent's piece
                            if next_square in [p.square for p in board.pieces if p.color != piece.color] and next_square not in opponent_king_squares and not is_square_attacked(next_square, opponent_attacking_squares):
                                for p in board.pieces:
                                    if p.square == next_square:
                                        captured_piece = p
                                if (not king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                    possible_moves.append((piece, next_square))
                                    possible_moves_in_chess_notation.append(Move(piece.piece_type, x, y, iscapture=True))
                                    
    # Below statements were used when debugging                       
    # for p in possible_moves:
    #     print(p)
    # for p in possible_moves_in_chess_notation:
    #     print(p)
    # for o in board.occupied_squares:
    #     print(o)

    return possible_moves
    
# ______________________________Checkmate checker_________________________________________

def check_game_over(board, player):
    #Check if checkmate or stalemate
    possible_moves = generate_possible_moves(board, player)
    #print(board.pieces) -- for debugging
    #print(king_in_check) -- for debugging
    if not possible_moves and king_in_check:
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
        possible_moves = generate_possible_moves(board, player)
        
        for move in possible_moves:
            piece, square_to = move
            #print("FIRST MOVE ", move, 0)
            original_piece_square = piece.square
            board.update(piece, square_to)
            score, sequence = minimax(board, 0, False, max_depth, player, current_sequence=[move])  # Pass first move in the sequence
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
        
        for move in generate_possible_moves(board, player):
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
        
        for move in generate_possible_moves(board, player):
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
        possible_moves = generate_possible_moves(board, player)
        
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
        
        for move in generate_possible_moves(board, player):
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
        
        for move in generate_possible_moves(board, player):
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

        possible_moves = generate_possible_moves(board, player)
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
            
            possible_moves = generate_possible_moves(board, current_player)
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
                        
                    moves = generate_possible_moves(board, current_player)
                    if not moves and king_in_check:
                        print(highest_valued_piece_capturable)
                        print(piece, square)
                        move = Move(piece.piece_type, square.x, square.y, original_piece_x, iscapture=True, ischeckmate=True)
                        break
                    elif not moves and not king_in_check:
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
                        
                    moves = generate_possible_moves(board, current_player)
                    if not moves and king_in_check:
                        print(highest_valued_piece_capturable)
                        move = Move(piece.piece_type, square.x, square.y, iscapture=True, ischeckmate=True)
                        break
                    elif not moves and not king_in_check:
                        print(highest_valued_piece_capturable)
                        move = Move(piece.piece_type, square.x, square.y, iscapture=True)
                        break
                    else:
                        move = Move(piece.piece_type, square.x, square.y, iscapture=True)
            else:
                board.update(piece, square)
                moves = generate_possible_moves(board, current_player)
                move = Move(piece.piece_type, square.x, square.y)
                if not moves and king_in_check:
                    print("Checkmate!")
                    move = Move(piece.piece_type, square.x, square.y, ischeckmate=True)
                    screen.blit(font.render(str(count), True, COLOUR_NAMES["BLACK"]), (count_pos_x,count_pos_y))
                    screen.blit(font.render(str(move), True, COLOUR_NAMES["BLACK"]), (pos_x,pos_y))
                    return_set.append((move, pos_x, pos_y))
                    move_set_calculated = return_set
                    move_index = move_number
                    return return_set
                elif not moves and not king_in_check:
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
            if king_in_check:
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
    global display_indexes
    global paused
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
    board = Board(8, 8, images, row_pieces)
    algorithm = None
    
    board.draw_board()
    board.add_pieces(row_pieces)
    board.draw_pieces()
    
    #game_over = check_game_over(possible_moves, current_player) -- debugging purpose
    #g = generate_possible_moves(board, current_player)-- debugging purpose
    # print(g)-- debugging purpose
    
    running = True
    #Main pygame loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    display_indexes = not display_indexes
                elif event.key == pygame.K_p:  # Pause the game when 'p' is pressed
                    paused = not paused  # Toggle the paused state
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
            
        if not paused:  # Only update the game if it's not paused
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
            if display_indexes:
                board.draw_indexes()
            pygame.display.flip()
            clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
