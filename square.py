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