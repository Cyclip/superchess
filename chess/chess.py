import numpy as np
from . import pieces as chess_pieces
import colorama
import hashlib

class ChessBoard:
    """
    A chessboard is 16x16 represented as an array of pieces.
    The columns are labeled A-P
    Rows are labeled 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, A, B, C, D, E, F
    Piece characters are as follows:
        K - King ♔         ∞
        Q - Queen ♕        8
        W - Wormhole ⇆     7
        R - Rook ♖         5
        B - Bishop ♗       3
        N - Knight ♘       3
        P - Pawn ♙         1
    Color characters are as follows:
        W - White
        B - Black
    """
    def __init__(self):
        self.board = chess_pieces.gen_board()
        self.shape = self.board.shape
        self.last_moved_piece = None
        self.last_moved_piece_from = None
        self.last_moved_piece_to = None
        self.game_over = False
        self.winner = None

        print(self)
    
    def pos_key(self):
        """
        Returns a unique key for the current board position.
        """
        position = self.board_to_string_compact()
    
        return hashlib.sha256(position.encode("utf-8")).hexdigest()
    
    def board_to_string_compact(self):
        """
        Returns a compact string representation of the board.
        """
        board_string = ""

        for row in self.board:
            for piece in row:
                if piece:
                    board_string += piece.__repr__()
                else:
                    board_string += " "

        return board_string
    
    def __repr__(self):
        return self.board_to_string()
    
    def board_to_string(self):
        """
        Returns a string representation of the board.
        """
        # Prints all the pieces in a nice grid
        # Black pieces are printed in red
        # White pieces are printed in white
        # Last moved piece is printed in green
        # Moves from are printed in yellow background

        board_string = ""

        # Add column labels
        board_string += "   "
        for i in range(16):
            board_string += chr(i + 65) + " "
        board_string += "\n"

        for i, row in enumerate(self.board):
            # Add row labels
            board_string += f"{i+1:>2} "
            for j, piece in enumerate(row):
                if piece:
                    # Colour
                    if piece == self.last_moved_piece:
                        board_string += colorama.Fore.GREEN
                    elif piece.colour == "B":
                        board_string += colorama.Fore.RED
                    else:
                        board_string += colorama.Fore.WHITE

                    # Piece symbol
                    board_string += piece.__repr__()
                    
                    # Reset colour
                    board_string += colorama.Fore.RESET
                    board_string += colorama.Back.RESET
                elif (i, j) == self.last_moved_piece_from:
                    board_string += colorama.Back.BLACK
                    board_string += " "
                    board_string += colorama.Back.RESET
                else:
                    board_string += " "
                
                board_string += " " + colorama.Fore.RESET
            board_string += "\n"
        
        return board_string[:-1]
    
    def get_piece(self, pos):
        """
        Returns the piece at the given position.
        """
        try:
            return self.board[pos[0]][pos[1]]
        except IndexError:
            # print(f"IndexError: {pos} is not a valid position.")
            return None

 
    def is_empty(self, pos):
        """
        Returns True if the given position is empty.
        """
        return self.get_piece(pos) is None
    
    def set_piece(self, pos, piece):
        """
        Sets the piece at the given position.
        No checking is done to ensure the move is legal.
        """
        self.board[pos[0]][pos[1]] = piece
    
    def move_piece(self, start_pos, end_pos):
        """Move a piece without checking for legality."""
        piece = self.get_piece(start_pos)

        # Get captured piece if any
        captured_piece = self.get_piece(end_pos)

        self.set_piece(start_pos, None)
        self.set_piece(end_pos, piece)
        piece.has_moved = True
        piece.pos = end_pos

        self.last_moved_piece = piece
        self.last_moved_piece_from = tuple(start_pos)
        self.last_moved_piece_to = tuple(end_pos)

        # May be a pawn moving 2 spaces
        if isinstance(piece, chess_pieces.Pawn):
            piece.moved_two = abs(start_pos[0] - end_pos[0]) == 2
        
        # if king is captured
        if isinstance(piece, chess_pieces.King):
            self.game_over = True
            self.winner = piece.colour

        return captured_piece
    
    def get_legal_moves(self, pos):
        """
        Returns a list of legal moves for the piece at the given position.
        """
        piece = self.get_piece(pos)
        if not piece:
            return []
        
        moves = piece.get_moves(self)
        legal_moves = []
        for move in moves:
            if self.is_legal_move(piece, move):
                legal_moves.append(move)
        
        return legal_moves
    
    def get_legal_moves_by_piece(self, piece):
        """
        Returns a list of legal moves for the given piece.
        """
        return self.get_legal_moves(piece.pos)
    
    def is_legal_move(self, piece, move):
        """
        Returns True if the given move is legal for the given piece.
        Revealing your king is considered a legal move, just a very stupid blunder.
        I mean we give so much help by preventing that move, it's only fair.
        """
        # Global rules apply to every single piece
        # Move is illegal if it attempts to move off the board
        # Based on self.shape
        if move[0] < 0 or move[0] >= self.shape[0]:
            return False
        if move[1] < 0 or move[1] >= self.shape[1]:
            return False
        
        # Move is illegal if it attempts to move onto a friendly piece
        if self.get_piece(move):
            if self.get_piece(move).colour == piece.colour:
                return False
            
        return True
    
    def get_white_pieces(self):
        """
        Returns a list of all white pieces.
        """
        white_pieces = filter(
            lambda piece: piece and piece.colour == "W",
            np.array(self.board).flatten()
        )
        
        return np.array(list(white_pieces))
    
    def get_black_pieces(self):
        """
        Returns a list of all black pieces.
        """
        black_pieces = filter(
            lambda piece: piece and piece.colour == "B",
            np.array(self.board).flatten()
        )
        
        return np.array(list(black_pieces))
    
    """Some more methods to allow it to communicate with the client"""
    def pieces_to_json(self):
        """Create a JSON representation of the pieces on the board.
        Example output:
        {
            "white": [
                {
                    "type": "K",
                    "pos": [0, 4]
                },
                {
                    "type": "Q",
                    "pos": [0, 3]
                },
                ...
            ],
            "black": [
                {
                    "type": "K",
                    "pos": [7, 4]
                },
                {
                    "type": "Q",
                    "pos": [7, 3]
                },
                ...
            ]
        }
        """
        pieces = {
            "W": [],
            "B": []
        }
        
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece:
                    pieces[piece.colour.upper()].append({
                        "type": piece.key,
                        "pos": [i, j]
                    })
        
        return pieces
    
    def get_king(self, colour):
        """Returns the king of the given colour."""
        pieces = self.get_white_pieces() if colour == "W" else self.get_black_pieces()
        for piece in pieces:
            if isinstance(piece, chess_pieces.King):
                return piece
        
        return None
    
    def is_stalemate(self, colour):
        """Returns True if the given colour is in stalemate."""
        pieces = self.get_white_pieces() if colour == "W" else self.get_black_pieces()
        for piece in pieces:
            if self.get_legal_moves(piece.pos):
                return False
        
        return True
    
    def get_threatened_pieces(self, colour):
        """
        Returns a list of pieces which are threatened by the given colour.
        """
        pieces = self.get_white_pieces() if colour == "W" else self.get_black_pieces()

        threatened_pieces = []
        for piece in pieces:
            # Get all legal moves by piece
            moves = self.get_legal_moves_by_piece(piece)

            # Check if any of the moves threaten a piece
            for move in moves:
                if self.get_piece(move):
                    threatened_pieces.append(self.get_piece(move))
        
        return threatened_pieces
    
    def get_board_score(self):
        """
        Returns a score for the board.
        """
        score = 0
        for row in self.board:
            for piece in row:
                if piece:
                    score += piece.value
        
        return score
    
    def is_in_check(self, colour):
        """
        Returns True if the given colour is in check.
        """
        king = self.get_king(colour)
        threatened_pieces = self.get_threatened_pieces("W" if colour == "B" else "B")
        return king in threatened_pieces