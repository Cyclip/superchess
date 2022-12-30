import chess.pieces as chess_pieces
import json

VALUES = {
    # Game state values
    "CHECK": 1000,
    "STALEMATE": float("-inf"),

    # Capture values
    "PAWN_CAPTURE": 100,
    "KNIGHT_CAPTURE": 300,
    "BISHOP_CAPTURE": 300,
    "ROOK_CAPTURE": 500,
    "QUEEN_CAPTURE": 900,
    "WORMHOLE_CAPTURE": 800,
    "KING_CAPTURE": float("inf"),

    # Threaten values
    "PAWN_THREATEN": 10,
    "KNIGHT_THREATEN": 30,
    "BISHOP_THREATEN": 30,
    "ROOK_THREATEN": 50,
    "QUEEN_THREATEN": 90,
    "WORMHOLE_THREATEN": 80,

    "MOBILITY": 10,
}

def get_all_moves(board, colour):
    # Get all pieces
    pieces = board.get_white_pieces() if colour == "W" else board.get_black_pieces()

    # Get all the legal moves for each piece
    moves = {}

    for piece in pieces:
        legalMoves = board.get_legal_moves(piece.pos)
        if len(legalMoves) > 0:
            moves[piece] = legalMoves

    return pieces, moves

def get_capture_value(piece):
    """
    Returns the value of capturing a piece.
    """
    if isinstance(piece, chess_pieces.Pawn):
        return VALUES["PAWN_CAPTURE"]
    elif isinstance(piece, chess_pieces.Knight):
        return VALUES["KNIGHT_CAPTURE"]
    elif isinstance(piece, chess_pieces.Bishop):
        return VALUES["BISHOP_CAPTURE"]
    elif isinstance(piece, chess_pieces.Rook):
        return VALUES["ROOK_CAPTURE"]
    elif isinstance(piece, chess_pieces.Queen):
        return VALUES["QUEEN_CAPTURE"]
    elif isinstance(piece, chess_pieces.Wormhole):
        return VALUES["WORMHOLE_CAPTURE"]
    elif isinstance(piece, chess_pieces.King):
        return VALUES["KING_CAPTURE"]
    else:
        return 0

def get_threaten_value(piece):
    """
    Returns the value of threatening a piece.
    """
    if isinstance(piece, chess_pieces.Pawn):
        return VALUES["PAWN_THREATEN"]
    elif isinstance(piece, chess_pieces.Knight):
        return VALUES["KNIGHT_THREATEN"]
    elif isinstance(piece, chess_pieces.Bishop):
        return VALUES["BISHOP_THREATEN"]
    elif isinstance(piece, chess_pieces.Rook):
        return VALUES["ROOK_THREATEN"]
    elif isinstance(piece, chess_pieces.Queen):
        return VALUES["QUEEN_THREATEN"]
    elif isinstance(piece, chess_pieces.Wormhole):
        return VALUES["WORMHOLE_THREATEN"]
    else:
        return 0
    
def evaluate_board(board):
    """
    Determines a score for the current board state.
    Positive score is good for white, negative score is good for black.
    Score is determined by a number of factors:
    1. Total value of pieces
    2. Threatened pieces
    3. Check
    4. Mobility
    """
    score = 0

    # Get all pieces
    whitePieces = board.get_white_pieces()
    blackPieces = board.get_black_pieces()

    # Get all moves
    whitePieces, whiteMoves = get_all_moves(board, "W")
    blackPieces, blackMoves = get_all_moves(board, "B")

    # Get all threatened pieces
    whiteThreatenedPieces = board.get_threatened_pieces("W")
    blackThreatenedPieces = board.get_threatened_pieces("B")

    # Is in check?
    if board.is_in_check("W"):
        score += VALUES["CHECK"]
    elif board.is_in_check("B"):
        score -= VALUES["CHECK"]

    # Is in stalemate?
    if board.is_stalemate("W"):
        score += VALUES["STALEMATE"]
    elif board.is_stalemate("B"):
        score -= VALUES["STALEMATE"]

    # Get total value of pieces
    for piece in whitePieces:
        score += piece.value
    for piece in blackPieces:
        score -= piece.value

    # Get total value of threatened pieces
    for piece in whiteThreatenedPieces:
        score += get_threaten_value(piece)
    for piece in blackThreatenedPieces:
        score -= get_threaten_value(piece)

    # Get total value of moves
    for piece in whiteMoves:
        score += len(whiteMoves[piece]) * VALUES["MOBILITY"]
    for piece in blackMoves:
        score -= len(blackMoves[piece]) * VALUES["MOBILITY"]
    
    return score


def in_transposition_table(board):
    """
    Check if the current board position is
    in the transposition table. If not, return None.
    """
    posKey = board.pos_key()
    transposition = get_transposition()
    if posKey in transposition:
        return (
            transposition[posKey]["score"],
            transposition[posKey]["metadata"]
        )
    
    return None # explicit


def get_transposition():
    """
    Get the transposition table.
    """
    return json.load(
        open("transposition_table.json", "r")
    )

def save_transposition(t):
    """
    Save the transposition table.
    """
    json.dump(
        t,
        open("transposition_table.json", "w"),
        indent=4
    )

def add_transposition(board, score, bestMove, depth):
    """
    Add a new transposition to the transposition table.
    """
    # filename: transposition_table.json
    # format: {posKey: {"score": score, "metadata": {"best_move": bestMove, "depth": depth}}}
    posKey = board.pos_key()
    transposition = get_transposition()
    transposition[posKey] = {
        "score": score,
        "metadata": {
            "best_move": bestMove,
            "depth": depth
        }
    }
    
    save_transposition(transposition)