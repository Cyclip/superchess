import numpy as np
import colorama

# Directions
DIRECTION_HORIZONTAL = [
    [1, 0],
    [-1, 0]
]

DIRECTION_VERTICAL = [
    [0, 1],
    [0, -1]
]

DIRECTION_DIAGONAL = [
    [1, 1],
    [-1, -1],
    [1, -1],
    [-1, 1]
]

class Piece:
    def __init__(self, colour, pos):
        self.colour = colour
        self.pos = pos
        self.has_moved = False
        self.symbol = '' # optional (print)
        self.key = '' # required
    
    def colour_code(self, symbol):
        if self.colour == "W":
            return colorama.Fore.WHITE + symbol + colorama.Fore.RESET
        else:
            return colorama.Fore.RED + symbol + colorama.Fore.RESET

    def __repr__(self):
        return self.symbol
    
    def coloured_repr(self):
        return self.colour_code(self.symbol)
    
    def to_json(self):
        return {
            "colour": "white" if self.colour == "W" else "black",
            "pos": self.pos,
            "has_moved": self.has_moved,
            "key": self.key
        }

class King(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 1000
        self.symbol = "♔"
        self.key = "K"
    
    def get_moves(self, board):
        """
        Can move one space in any direction.
        """
        moves = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                moves.append([self.pos[0] + i, self.pos[1] + j])
        
        return moves

class Queen(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 9
        self.symbol = "♕"
        self.key = "Q"
    
    def get_moves(self, board):
        """
        Can move any number of spaces in any direction.
        Once it hits a piece, it cannot move past it.
        """
        moves = []
        
        # For each direction (horizontal, vertical, diagonal)
        for direction in DIRECTION_HORIZONTAL + DIRECTION_VERTICAL + DIRECTION_DIAGONAL:
            # For each step in that direction
            for i in range(1, 16):
                pos = [self.pos[0] + direction[0] * i, self.pos[1] + direction[1] * i]
                # If the position is off the board, stop
                if pos[0] < 0 or pos[0] > 15 or pos[1] < 0 or pos[1] > 15:
                    break
                
                on = board.get_piece(pos)

                # If its a friendly piece, stop non-inclusive
                if on:
                    if on.colour == self.colour:
                        break
                    # If its an enemy piece, add it and stop
                    else:
                        moves.append(pos)
                        break

                moves.append(pos)

        
        return moves
    
class Wormhole(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 7
        self.symbol = "⇆"
        self.key = "W"
    
    def get_moves(self, board):
        """
        Movement rules:
        1. Can move 1 step in any direction
        2. Can loop round the board
            a. Only on left and right sides
        3. Can jump over friendly pawns
            a. Destination *must* be empty
            b. Can only jump horizontally or vertically
        """
        # Rule 1: Move 1 step in any direction
        moves = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                pos = [self.pos[0] + i, self.pos[1] + j]

                # Rule 3: If it is on a pawn, it can jump over it
                # Is it on a pawn?
                on = board.get_piece(pos)
                if isinstance(on, Pawn):
                    # Is it a friendly pawn?
                    if on.colour == self.colour:
                        # Rule 3a: Destination (dir * 2) must be empty
                        direction = [i, j]
                        dest = [pos[0] + direction[0], pos[1] + direction[1]]
                        if board.get_piece(dest) is None:
                            # Rule 3b: Can only jump horizontally or vertically
                            if direction[0] == 0 or direction[1] == 0:
                                moves.append(dest)
                    else:
                        # Can capture enemy pawn
                        moves.append(pos)
                else:
                    # Can move to empty space or capture enemy piece
                    moves.append(pos)
        
        # Rule 2: Loop round the board
        # Position in form (y, x)
        for i in range(len(moves)):
            # If moving out of through right side
            if moves[i][1] > 15:
                # Teleport to left side
                moves[i][1] = 0
            # If moving out of through left side
            elif moves[i][1] < 0:
                # Teleport to right side
                moves[i][1] = 15
        
        return moves

class Rook(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 5
        self.symbol = "♖"
        self.key = "R"
    
    def get_moves(self, board):
        """
        Can move any number of spaces in any direction.
        Once it hits a piece, it cannot move past it.
        """
        directions = [
            [1, 0],
            [-1, 0],
            [0, 1],
            [0, -1]
        ]
        moves = []
        for direction in directions:
            # Move in direction until it hits a piece
            for k in range(16):
                pos = [self.pos[0] + direction[0] * (k + 1), self.pos[1] + direction[1] * (k + 1)]
                piece = board.get_piece(pos)
                if piece:
                    if piece.colour != self.colour:
                        # Can capture enemy piece
                        moves.append(pos)
                    # Cannot move past any piece
                    break
                else:
                    # Can move to empty space
                    moves.append(pos)
        
        return moves

class Bishop(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 3
        self.symbol = "♗"
        self.key = "B"
    
    def get_moves(self, board):
        """
        Can move any number of spaces in any direction.
        Once it hits a piece, it cannot move past it.
        """
        directions = [
            [1, 1],
            [-1, 1],
            [1, -1],
            [-1, -1]
        ]
        moves = []
        for direction in directions:
            # Move in direction until it hits a piece
            for k in range(16):
                pos = [self.pos[0] + direction[0] * (k + 1), self.pos[1] + direction[1] * (k + 1)]
                piece = board.get_piece(pos)
                if piece:
                    if piece.colour != self.colour:
                        # Can capture enemy piece
                        moves.append(pos)
                    # Cannot move past any piece
                    break
                else:
                    # Can move to empty space
                    moves.append(pos)
        
        return moves

class Knight(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 3
        self.symbol = "♘"
        self.key = "N"
    
    def get_moves(self, board):
        # Positions are in format (y, x)
        knight_moves = [
            [2, 1],
            [2, -1],
            [-2, 1],
            [-2, -1],
            [1, 2],
            [1, -2],
            [-1, 2],
            [-1, -2]
        ]
        moves = []
        for move in knight_moves:
            pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
            # we trust that the board will check if the move is valid
            # through global rules
            moves.append(pos)
        
        return moves

class Pawn(Piece):
    def __init__(self, colour, pos):
        super().__init__(colour, pos)
        self.value = 1
        self.has_moved_two_spaces = False
        self.symbol = "♙"
        self.key = "P"
    
    def get_moves(self, board):
        """
        Rules:
        1. Can move relatively forward one space
        2. Can move relatively forward two spaces if it has not moved yet
        3. Can capture diagonally forward one space
        4. Can en-passant capture diagonally forward one space
        """
        moves = []

        # Rule 1: Can move relatively forward one space
        direction = 1 if self.colour == "B" else -1
        pos = [self.pos[0] + direction, self.pos[1]]
        if board.is_empty(pos):
            moves.append(pos)
            # Rule 2: Can move relatively forward two spaces if it has not moved yet
            if not self.has_moved:
                pos = [self.pos[0] + direction * 2, self.pos[1]]
                if board.is_empty(pos):
                    moves.append(pos)
            
        # Rule 3: Can capture diagonally forward one space
        for i in [-1, 1]:
            # Move up in direction, and either left or right
            pos = [self.pos[0] + direction, self.pos[1] + i]
            piece = board.get_piece(pos)
            if piece and piece.colour != self.colour:
                moves.append(pos)
        
        # Rule 4: Can en-passant capture diagonally forward one space
        # Check if there is a pawn in same row, one space away
        for i in [-1, 1]:
            pos = [self.pos[0], self.pos[1] + i]
            piece = board.get_piece(pos)
            if isinstance(piece, Pawn) and piece.colour != self.colour:
                # Check if the pawn has moved two spaces
                if piece.has_moved_two_spaces:
                    moves.append([self.pos[0] + direction, self.pos[1] + i])

        return moves


def symbol_to_piece(symbol, pos):
    colour = "W" if symbol.isupper() else "B"
    symbol = symbol.upper()
    match symbol:
        case "K":
            return King(colour, pos)
        case "Q":
            return Queen(colour, pos)
        case "W":
            return Wormhole(colour, pos)
        case "R":
            return Rook(colour, pos)
        case "B":
            return Bishop(colour, pos)
        case "N":
            return Knight(colour, pos)
        case "P":
            return Pawn(colour, pos)
        case " ":
            return None
        case _:
            raise ValueError(f"Invalid symbol: {symbol}")


def gen_board():    
    # Position is (y, x)
    black_pieces = [symbol_to_piece(piece.lower(), (0, i)) for i, piece in enumerate(pieces)]
    black_pawns = [symbol_to_piece("p", (1, i)) for i in range(16)]

    white_pawns = [symbol_to_piece("P", (14, i)) for i in range(16)]
    white_pieces = [symbol_to_piece(piece, (15, i)) for i, piece in enumerate(pieces[::-1])]

    board = np.array([
        black_pieces,
        black_pawns,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        [None] * 16,
        white_pawns,
        white_pieces,
    ])

    return board

# Default position
pieces = ['R', 'B', 'N', 'W', 'B', 'R', 'N', 'Q', 'K', 'N', 'R', 'B', 'W', 'N', 'B', 'R']