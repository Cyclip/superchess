import copy
from chess import pieces as chess_pieces

import random

MAX_DEPTH = 2
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
}

def get_move(board):
    """
    Returns a move for the bot (black) to make.

    Returns:
        A tuple of the form (start_pos, end_pos)
    """
    # Get all the black pieces
    pieces, moves = get_all_moves(board)

    # Get value of each move
    move_values = {}
    length = len(moves)
    for i, piece in enumerate(moves):
        for move in moves[piece]:
            move_values[(tuple(piece.pos), tuple(move))] = get_value(board, piece, move, 0)
            print(f"[{i+1}/{length}] Move: {piece} at {piece.pos} to {move} has value {move_values[(tuple(piece.pos), tuple(move))]}")

    print(move_values)
    # print(json.dumps(move_values, indent=4))

    # json.dump(
    #     move_values,
    #     open("move_values.json", "w"),
    #     indent=4
    # )

    # Get the move with the highest value
    try:
        return max(move_values, key=move_values.get)
    except:
        # random (from, to)
        return random.choice(list(moves.items()))[1][0]


def get_all_moves(board, filter=True):
    # Get all the black pieces
    pieces = board.get_black_pieces()

    # Get all the legal moves for each piece
    moves = {}

    for piece in pieces:
        if filter:
            # 10% chance piece is accepted
            if random.random() < 0.75:
                continue
            
        legalMoves = board.get_legal_moves(piece.pos)
        if len(legalMoves) > 0:
            moves[piece] = legalMoves

    return pieces, moves

def get_value(board, piece, move, depth, value=0):
    # print(f"\n\n[{depth}] Evaluating {piece} at {piece.pos} to {move}")
    """
    Returns the value of a move for the bot (black).
    """
    if depth == MAX_DEPTH:
        return value

    # Make a copy of the board
    board_copy = copy.deepcopy(board)

    # Make the move
    capture = board_copy.move_piece(piece.pos, move)
    if capture:
        # print(f"[{depth}] Capture {capture.coloured_repr()}")
        pass
    
    # Is stalemate?
    if board_copy.is_stalemate("B") or board_copy.is_stalemate("W"):
        # print(f"[{depth}] Stalemate")
        return VALUES["STALEMATE"]
    
    # Is capture?
    if capture:
        # Is it our piece captured?
        if capture.colour == "B":
            # print(f"[{depth}] Captured {capture.coloured_repr()}")
            value -= get_capture_value(capture)
        # Is it their piece captured?
        else:
            # print(f"[{depth}] Captured {capture.coloured_repr()}")
            value += get_capture_value(capture)
    
    # Get threatened enemy pieces (includes check)
    threatened_pieces = board_copy.get_threatened_pieces("W")
    for piece in threatened_pieces:
        # print(f"[{depth}] Threatened {piece.coloured_repr()}")
        value += get_threaten_value(piece)
    
    # Are our pieces threatened? (includes check)
    threatened_pieces = board_copy.get_threatened_pieces("B")
    for piece in threatened_pieces:
        # print(f"[{depth}] Threatened {piece.coloured_repr()}")
        value -= get_threaten_value(piece)
    
    # Get all the black pieces
    pieces, moves = get_all_moves(board_copy)

    # Get value of each move
    move_values = {}
    for piece in moves:
        for move in moves[piece]:
            move_values[(tuple(piece.pos), tuple(move))] = get_value(board_copy, piece, move, depth + 1, value)

    try:
        return max(move_values.values())
    except:
        return value

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