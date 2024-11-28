from square import Square
from move import Move
from piece import Piece
from graphics import COLOUR_NAMES
import pygame
pygame.init()
GAP = 25
font = pygame.font.SysFont('Comic Sans MS', 20)

class Board:
    """The main object in this project. Board class containing the rows, columns, images, fen position and most of the main functions."""
    def __init__(self, rows, columns, images, screen, fen):
        self.rows = rows
        self.columns = columns
        self.squares = []
        self.occupied_squares = []
        self.square_size = 65
        self.colors = [COLOUR_NAMES["LIGHT_WHITE"], COLOUR_NAMES["LIGHT_GREEN"]]
        self.pieces = []
        self.images = images
        self.screen = screen
        self.initial_fen = fen
        self.captured_piece = None
        self.captured_pieces = []
        self.display_indexes = False
        self.king_in_check = False
        self.checking_piece = None
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
                pygame.draw.rect(self.screen, color, [GAP + col * self.square_size, GAP + row * self.square_size, self.square_size, self.square_size])
                       
        for row in range(self.rows + 1):
            pygame.draw.line(self.screen, COLOUR_NAMES["BLACK"], (GAP, GAP + row * self.square_size), (GAP + width, GAP + row * self.square_size), border_width)
        
        for col in range(self.columns + 1):
            pygame.draw.line(self.screen, COLOUR_NAMES["BLACK"], (GAP + col * self.square_size, GAP), (GAP + col * self.square_size, GAP + height), border_width)
        
        for i in range(8):
            rank_text = font.render(str(8 - i), True, COLOUR_NAMES["BLACK"])
            file_text = font.render(chr(ord('a') + i), True, COLOUR_NAMES["BLACK"])
            self.screen.blit(rank_text, (5, GAP + i * self.square_size + self.square_size // 2 - rank_text.get_height() // 2))
            self.screen.blit(file_text, (GAP + i * self.square_size + self.square_size // 2 - file_text.get_width() // 2, GAP + height + GAP // 4))


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
            piece.draw(self.screen)
            
    def draw_indexes(self):
        #Draw the indexes of each box if toggled. (Press 'i')
        if self.display_indexes:
            for square in self.squares:
                idx_text = font.render(str(square.idx), True, COLOUR_NAMES["BLACK"])
                text_rect = idx_text.get_rect(center=(GAP + square.x * self.square_size + self.square_size // 2, GAP + (7 - square.y) * self.square_size + self.square_size // 2))
                self.screen.blit(idx_text, text_rect)
                        
    def update(self, piece_from, square_to):
        #update all data when a move is made
        if square_to in self.occupied_squares:
            #handle captures
            self.pieces.remove(piece_from)
            self.occupied_squares.remove(piece_from.square)
            
            for piece_to in self.pieces:
                if piece_to.square == square_to:
                    self.pieces.remove(piece_to)
                    self.occupied_squares.remove(piece_to.square)
                    new_p = Piece(piece_from.piece_type, piece_from.color, square_to, self.images)
                    self.pieces.append(new_p)
                    self.occupied_squares.append(new_p.square)
                    break
        else:
            #normal move
            self.occupied_squares.remove(piece_from.square)
            self.pieces.remove(piece_from)
            new_p = Piece(piece_from.piece_type, piece_from.color, square_to, self.images)
            self.pieces.append(new_p)
            self.occupied_squares.append(new_p.square)
    
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

    def generate_possible_moves(self, current_player):
        """The most vital function in this project.
        Generates a list of all possible moves at a given position.
        """
        
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
        for piece in self.pieces:
            if piece.piece_type.lower() == "k" and ((current_player == 'w' and piece.color == 'black') or (current_player == 'b' and piece.color == 'white')):
                opponent_king_moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
                for dx, dy in opponent_king_moves:
                    x = piece.square.x + dx
                    y = piece.square.y + dy
                    if 0 <= x < 8 and 0 <= y < 8:
                        opponent_king_squares.append(Square(x, y, y * 8 + x + 1))
                        
        
        
        def get_attacking_squares():
            #Determine all possible attacking moves of the opponent
            for piece in self.pieces:
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
                                    for p in self.pieces:
                                        if p.square == next_square:
                                            attacking_piece = piece
                                            all_attacking_squares.append((attacking_piece, next_square))

                                    opponent_attacking_squares.append(next_square)
                                    if piece.piece_type.lower() in ['n', 'p']:
                                        break  #Knights and pawns move only once in each direction
                                    if next_square in self.occupied_squares:
                                        break  #Stop if an occupied square is encountered
                                else:
                                    break
                                
        get_attacking_squares()

        # Find the current player's king
        current_king = None
        for piece in self.pieces:
            if piece.piece_type.lower() == "k" and ((current_player == 'w' and piece.color == 'white') or (current_player == 'b' and piece.color == 'black')):
                current_king = piece
                break
                    
        def if_check(square, opponent_moves):
            #Check if the king is in check and returns the bool
            for attack_square in opponent_moves:
                attacking_piece, s = attack_square
                if s == square:
                    pieces_saying_check.append(attacking_piece)
                    self.king_in_check = True
                    return True
            self.king_in_check = False
            return False
        
        self.king_in_check = if_check(current_king.square, all_attacking_squares)
            
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

            self.occupied_squares.remove(original_square)
            piece.square = target_square
            self.occupied_squares.append(target_square)

            # Recalculate opponent attacking squares after the move
            recalculated_opponent_attacking_squares = []
            for opponent_piece in self.pieces:
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
                                    if next_square in self.occupied_squares:
                                        break  #Stopp if an occupied square is encountered
                                else:
                                    break

            #Check if the king is still in check
            king_safe = not is_square_attacked(current_king.square, recalculated_opponent_attacking_squares)

            # Revert the move
            self.occupied_squares.remove(target_square)
            piece.square = original_square
            self.occupied_squares.append(original_square)

            return king_safe

        # Generate possible moves for the current player
        for piece in self.pieces:
            if (current_player == 'w' and piece.color == 'white') or (current_player == 'b' and piece.color == 'black'):
                if piece.piece_type == "p":  # black pawn
                    # Move forward
                    forward_square = Square(piece.square.x, piece.square.y - 1, piece.square.idx - 8)
                    if forward_square not in self.occupied_squares:
                        move = (piece, forward_square)
                        if (not self.king_in_check or can_move_resolve_check(move)):
                            possible_moves.append((piece, forward_square))
                            possible_moves_in_chess_notation.append(Move(piece, piece.square.x, piece.square.y - 1))

                    # Capture left
                    if piece.square.x > 0:
                        capture_left_square = Square(piece.square.x - 1, piece.square.y - 1, piece.square.idx - 9)
                        if capture_left_square in [p.square for p in self.pieces if p.color == "white"]:
                            move = (piece, capture_left_square)
                            for p in self.pieces:
                                if p.square == capture_left_square:
                                    captured_piece = p
                            if captured_piece != None and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                possible_moves.append((piece, capture_left_square))
                                possible_moves_in_chess_notation.append(Move(piece, piece.square.x - 1, piece.square.y - 1, piece.square.x, True))

                    # Capture right
                    if piece.square.x < 7:
                        capture_right_square = Square(piece.square.x + 1, piece.square.y - 1, piece.square.idx - 7)
                        if capture_right_square in [p.square for p in self.pieces if p.color == "white"]:
                            move = (piece, capture_right_square)
                            for p in self.pieces:
                                if p.square == capture_right_square:
                                    captured_piece = p
                            if captured_piece != None and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                possible_moves_in_chess_notation.append(Move(piece, piece.square.x + 1, piece.square.y - 1, piece.square.x, True))
                                
                elif piece.piece_type == "P":  # white pawn
                    # Move forward
                    forward_square = Square(piece.square.x, piece.square.y + 1, piece.square.idx + 8)
                    if forward_square not in self.occupied_squares:
                        move = (piece, forward_square)
                        if (not self.king_in_check or can_move_resolve_check(move)):
                            possible_moves.append((piece, forward_square))
                            possible_moves_in_chess_notation.append(Move(piece, piece.square.x, piece.square.y + 1))

                    # Capture left
                    if piece.square.x > 0:
                        capture_left_square = Square(piece.square.x - 1, piece.square.y + 1, piece.square.idx + 7)
                        if capture_left_square in [p.square for p in self.pieces if p.color == "black"]:
                            move = (piece, capture_left_square)
                            for p in self.pieces:
                                if p.square == capture_left_square:
                                    captured_piece = p
                                    if captured_piece != None and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                        possible_moves.append((piece, capture_left_square))
                                        possible_moves_in_chess_notation.append(Move(piece, piece.square.x - 1, piece.square.y + 1, piece.square.x, True))

                    # Capture right
                    if piece.square.x < 7:
                        capture_right_square = Square(piece.square.x + 1, piece.square.y + 1, piece.square.idx + 9)
                        if capture_right_square in [p.square for p in self.pieces if p.color == "black"]:
                            move = (piece, capture_right_square)
                            for p in self.pieces:
                                if p.square == capture_right_square:
                                    captured_piece = p
                                    if captured_piece != None and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                        possible_moves.append((piece, capture_right_square))
                                        possible_moves_in_chess_notation.append(Move(piece, piece.square.x + 1, piece.square.y + 1, piece.square.x, True))
                                            
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
                                if next_square not in self.occupied_squares:
                                    if (not self.king_in_check or can_move_resolve_check(move)):
                                        possible_moves.append((piece, next_square))
                                        possible_moves_in_chess_notation.append(Move(piece, x, y))
                                    if piece.piece_type.lower() == 'n':  # Knights move only once in each direction
                                        break
                                else:
                                    # Capture an opponent's piece
                                    if next_square in [p.square for p in self.pieces if p.color != piece.color]:
                                        for p in self.pieces:
                                            if p.square == next_square:
                                                captured_piece = p
                                        if captured_piece != None and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                            possible_moves.append((piece, next_square))
                                            possible_moves_in_chess_notation.append(Move(piece, x, y, iscapture=True))
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
                            if next_square not in self.occupied_squares and next_square not in opponent_king_squares and not is_square_attacked(next_square, opponent_attacking_squares):
                                if (not self.king_in_check or can_move_resolve_check(move)):
                                    possible_moves.append((piece, next_square))
                                    possible_moves_in_chess_notation.append(Move(piece, x, y))
                            else:
                                # Capture an opponent's piece
                                if next_square in [p.square for p in self.pieces if p.color != piece.color] and next_square not in opponent_king_squares and not is_square_attacked(next_square, opponent_attacking_squares):
                                    for p in self.pieces:
                                        if p.square == next_square:
                                            captured_piece = p
                                    if (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                        possible_moves.append((piece, next_square))
                                        possible_moves_in_chess_notation.append(Move(piece, x, y, iscapture=True))
        for piece, square in possible_moves:
            if square in self.occupied_squares:
                    for p in self.pieces:
                        if p.piece_type.lower() == "k" and p.square == square:
                            possible_moves.remove((piece,square))   
                                  
        return possible_moves
    
    def check_for_differences(self, legal_moves_uci, possible_moves):
        
        x_piece = {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3,
            "e": 4,
            "f": 5,
            "g": 6,
            "h": 7
        }
        
        letters = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h"
        }
    
        #Add Moves
        for move in legal_moves_uci:
            chars = list(move)
            starting_x = x_piece[chars[0]]
            starting_y = int(chars[1])-1
            ending_x = x_piece[chars[2]]
            ending_y = int(chars[3])-1
            
            starting_square = next((square for square in self.squares if square.x == starting_x and square.y == starting_y), None)
            ending_square = next((square for square in self.squares if square.x == ending_x and square.y == ending_y), None)
            
            starting_piece = next((piece for piece in self.pieces if piece.square == starting_square), None)
            
            if (starting_piece, ending_square) not in possible_moves:
                possible_moves.append((starting_piece, ending_square))
                
        #Remove Moves
        to_remove = []
        for piece, square_to in possible_moves:
            starting_x = piece.square.x
            starting_y = piece.square.y+1
            ending_x = square_to.x
            ending_y = square_to.y+1
            starting_letter = letters[starting_x]
            ending_letter = letters[ending_x]
            
            uci = starting_letter + str(starting_y) + ending_letter + str(ending_y)
            
            if uci not in legal_moves_uci:
                to_remove.append((piece, square_to))

        for item in to_remove:
            possible_moves.remove(item)
            
        return possible_moves

    
    def convert_to_uci(self, moves):

        x_piece = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h"
        }

        moves_in_uci = []
        
        for move in moves:
            square_from_x = move.piece.square.x
            letter_from_x = x_piece[square_from_x]
            square_from_y = move.piece.square.y
            part1 = f"{letter_from_x}{square_from_y}"
            letter_to_x = x_piece[move.x]
            letter_to_y = move.y
            part2 = f"{letter_to_x}{letter_to_y}"
            uci = part1+part2
            moves_in_uci.append((move,uci))

        return moves_in_uci