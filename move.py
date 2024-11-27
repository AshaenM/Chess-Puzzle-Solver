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