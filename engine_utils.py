import chess.pieces as chess_pieces
import json

VALUES = {
    # Game state values
    "CHECK": 150,
    "STALEMATE": float("-inf"),

    # Threaten values
    "PAWN_THREATEN": 10,
    "KNIGHT_THREATEN": 30,
    "BISHOP_THREATEN": 30,
    "ROOK_THREATEN": 60,
    "QUEEN_THREATEN": 120,
    "WORMHOLE_THREATEN": 100,

    # Potential captures
    "PAWN_CAPTURE": 20,
    "KNIGHT_CAPTURE": 40,
    "BISHOP_CAPTURE": 50,
    "ROOK_CAPTURE": 80,
    "QUEEN_CAPTURE": 150,
    "WORMHOLE_CAPTURE": 120,
    "KING_CAPTURE": float("inf"),

    # Pawn structure
    "PAWN_ISOLATED": -5,
    "PAWN_DOUBLED": -6,
    "PAWN_PASSED": 25,

    # Piece mobility
    "MOBILITY": 1,

    # Piece development
    "PAWN_DEVELOPMENT": 5,
    "KNIGHT_DEVELOPMENT": 10,
    "BISHOP_DEVELOPMENT": 10,
    "ROOK_DEVELOPMENT": 20,
    "QUEEN_DEVELOPMENT": 30,
    "WORMHOLE_DEVELOPMENT": 30,

    # Other
    "MOBILITY": 2,

    # King mobility
    "KING_MOBILITY": 10,
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

def get_development_value(piece):
    """
    Returns the value of developing a piece.
    """
    if isinstance(piece, chess_pieces.Pawn):
        return VALUES["PAWN_DEVELOPMENT"]
    elif isinstance(piece, chess_pieces.Knight):
        return VALUES["KNIGHT_DEVELOPMENT"]
    elif isinstance(piece, chess_pieces.Bishop):
        return VALUES["BISHOP_DEVELOPMENT"]
    elif isinstance(piece, chess_pieces.Rook):
        return VALUES["ROOK_DEVELOPMENT"]
    elif isinstance(piece, chess_pieces.Queen):
        return VALUES["QUEEN_DEVELOPMENT"]
    elif isinstance(piece, chess_pieces.Wormhole):
        return VALUES["WORMHOLE_DEVELOPMENT"]
    else:
        return 0

def evaluate_board(board, toPlay):
    """
    Determines a score for the current board state.
    Positive score is good for white, negative score is good for black.
    Score is determined by a number of factors:
    1. Total value of pieces
    2. Threatened pieces
    3. Check / stalemate
    4. Mobility
    5. Pawn structure
    6. Development
    7. Potential captures
    8. King safety
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

    # Get all pawns
    whitePawns = board.get_pawns("W")
    blackPawns = board.get_pawns("B")

    # Is in check?
    if board.is_in_check("W"):
        # DEBUG: print(f"[+{VALUES['CHECK']}] White is in check")
        score += VALUES["CHECK"]
    elif board.is_in_check("B"):
        # DEBUG: print(f"[-{VALUES['CHECK']}] Black is in check")
        score -= VALUES["CHECK"]

    # Is in stalemate?
    if board.is_stalemate("W"):
        # DEBUG: print(f"[+{VALUES['STALEMATE']}] White is in stalemate")
        score += VALUES["STALEMATE"]
    elif board.is_stalemate("B"):
        # DEBUG: print(f"[-{VALUES['STALEMATE']}] Black is in stalemate")
        score -= VALUES["STALEMATE"]

    # Get total value of pieces
    for piece in whitePieces:
        # DEBUG: print(f"[+{piece.value}] {piece} is on the board")
        score += piece.value
    for piece in blackPieces:
        # DEBUG: print(f"[-{piece.value}] {piece} is on the board")
        score -= piece.value

    # Get total value of threatened pieces
    for piece in whiteThreatenedPieces:
        if toPlay == "W":
            # DEBUG: print(f"[+{get_threaten_value(piece)}] {piece} is threatened with capture")
            score += get_capture_value(piece)
        else:
            # DEBUG: print(f"[+{get_capture_value(piece)}] {piece} is threatened")
            score += get_threaten_value(piece)
    for piece in blackThreatenedPieces:
        if toPlay == "B":
            # DEBUG: print(f"[-{get_threaten_value(piece)}] {piece} is threatened with capture")
            score -= get_capture_value(piece)
        else:
            # DEBUG: print(f"[-{get_capture_value(piece)}] {piece} is threatened")
            score -= get_threaten_value(piece)


    # Get total value of moves
    for piece in whiteMoves:
        # DEBUG: print(f"[+{len(whiteMoves[piece]) * VALUES['MOBILITY']}] {piece} has {len(whiteMoves[piece])} moves")
        score += len(whiteMoves[piece]) * VALUES["MOBILITY"]
    for piece in blackMoves:
        # DEBUG: print(f"[-{len(blackMoves[piece]) * VALUES['MOBILITY']}] {piece} has {len(blackMoves[piece])} moves")
        score -= len(blackMoves[piece]) * VALUES["MOBILITY"]
    

    # For each pawn, check if it is isolated, doubled, backward, or passed
    for piece in whitePieces:
        if isinstance(piece, chess_pieces.Pawn):
            # Isolated
            if not board.is_pawn_isolated(piece, whitePawns):
                # DEBUG: print(f"[+{VALUES['PAWN_ISOLATED']}] {piece} is isolated")
                score += VALUES["PAWN_ISOLATED"]

            # Doubled
            if board.is_pawn_doubled(piece, whitePawns):
                # DEBUG: print(f"[+{VALUES['PAWN_DOUBLED']}] {piece} is doubled")
                score += VALUES["PAWN_DOUBLED"]

            # Passed
            if board.is_pawn_passed(piece, whitePawns, blackPawns):
                # DEBUG: print(f"[+{VALUES['PAWN_PASSED']}] {piece} is passed")
                score += VALUES["PAWN_PASSED"]

    for piece in blackPieces:
        if isinstance(piece, chess_pieces.Pawn):
            # Isolated
            if not board.is_pawn_isolated(piece, blackPawns):
                # DEBUG: print(f"[-{VALUES['PAWN_ISOLATED']}] {piece} is isolated")
                score -= VALUES["PAWN_ISOLATED"]

            # Doubled
            if board.is_pawn_doubled(piece, blackPawns):
                # DEBUG: print(f"[-{VALUES['PAWN_DOUBLED']}] {piece} is doubled")
                score -= VALUES["PAWN_DOUBLED"]

            # Passed
            if board.is_pawn_passed(piece, whitePawns, blackPawns):
                # DEBUG: print(f"[-{VALUES['PAWN_PASSED']}] {piece} is passed")
                score -= VALUES["PAWN_PASSED"]

    # Development
    # Check which pieces are not in the starting position
    for piece in whitePieces:
        if piece.pos != piece.starting_pos:
            value = get_development_value(piece)
            # DEBUG: print(f"[+{value}] {piece} is developed")
            score += value
    
    for piece in blackPieces:
        if piece.pos != piece.starting_pos:
            value = get_development_value(piece)
            # DEBUG: print(f"[-{value}] {piece} is developed")
            score -= value

    # King safety
    # Check the threats to the king
    kingAttacksW = board.get_king_attacks("W")
    kingAttacksB = board.get_king_attacks("B")

    for piece in kingAttacksW:
        # DEBUG: print(f"[+{get_threaten_value(piece) * 1.5}] {piece} threatens the king")
        score += get_threaten_value(piece) * 1.5

    for piece in kingAttacksB:
        # DEBUG: print(f"[-{get_threaten_value(piece) * 1.5}] {piece} threatens the king")
        score -= get_threaten_value(piece) * 1.5
    
    # King mobility
    kingW = board.get_king("W")
    kingB = board.get_king("B")
    
    # Get all moves for the king that don't put it in check
    kingMovesW = list(filter(
        lambda x: board.is_pos_safe_for_king(x, "W"),
        board.get_legal_moves(kingW)
    ))

    kingMovesB = list(filter(
        lambda x: board.is_pos_safe_for_king(x, "B"),
        board.get_legal_moves(kingB)
    ))

    # DEBUG: print(f"[+{len(kingMovesW) * VALUES['KING_MOBILITY']}] White king has {len(kingMovesW)} safe moves")
    # DEBUG: print(f"[-{len(kingMovesB) * VALUES['KING_MOBILITY']}] Black king has {len(kingMovesB)} safe moves")
    score += len(kingMovesW) * VALUES["KING_MOBILITY"]
    score -= len(kingMovesB) * VALUES["KING_MOBILITY"]

    if score == float("inf"):
        return 9999999999
    elif score == float("-inf"):
        return -9999999999

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