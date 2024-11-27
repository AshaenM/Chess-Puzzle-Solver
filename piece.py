GAP = 25

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