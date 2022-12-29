import copy
import engine_utils

MAX_DEPTH = 2

def get_move(board):
    """
    Returns a move for the bot (black) to make.

    Returns:
        A tuple of the form (start_pos, end_pos)
    """

    # Check if in transposition table
    transposition = engine_utils.in_transposition_table(board)
    if transposition:
        score, metadata = transposition
        move = metadata["best_move"]
        depth = metadata["depth"]
        print(f"Transposition table hit at depth {depth}")
    else:
        # Get the best move
        score, move = minimax(board, MAX_DEPTH, True)

        # Add to transposition table
        engine_utils.add_transposition(board, score, move, MAX_DEPTH)

    print(f"Playing move {move} with score {score}")

    # Return the move in format (start_pos, end_pos)
    return move


def minimax(board, depth, is_maximizing):
    """
    Returns the best move for the bot (black) to make.

    Arguments:
        board: The current state of the board
        depth: The current depth of the search
        is_maximizing: True if we are maximizing, False if we are minimizing

    Returns:
        A tuple of the form (start_pos, end_pos)
    """

    # DEBUG: print(f"minimax(depth={depth}, is_maximizing={is_maximizing})")
    # If we have reached the maximum depth or the game is over, return the score
    if depth == 0 or board.game_over:
        return engine_utils.get_board_score(board)

    # If we are maximizing, we want to find the move that maximizes the score
    if is_maximizing:
        # Get all the black pieces
        pieces, moves = engine_utils.get_all_moves(board, "B")

        # The best score we have found so far
        best_score = float("-inf")

        # The best move we have found so far
        best_move = None

        # For each piece, find the best move
        for piece, piece_moves in moves.items():
            # For each move, find the best score
            for move in piece_moves:
                # Make a copy of the board
                new_board = copy.deepcopy(board)

                # Make the move
                new_board.move_piece(piece.pos, move)

                # Get the score for this move
                tmp = minimax(new_board, depth - 1, False)
                try:
                    score = tmp[0]
                except TypeError:
                    score = tmp

                # If this score is better than the best score, update the best score
                # DEBUG: print(f"[maximising] checking score: {score} (move: {piece.pos} -> {move})")
                if score > best_score:
                    # DEBUG: print(f"[maximising] UPDATING best_score: {best_score} -> {score} (move: {piece.pos} -> {move})")
                    best_score = score
                    best_move = (piece.pos, move)
        
        # DEBUG: print(f"[maximising] RETURNING best_score: {best_score} (move: {best_move})")
        return best_score, best_move

    # If we are minimizing, we want to find the move that minimizes the score
    else:
        # Get all the white pieces
        pieces, moves = engine_utils.get_all_moves(board, "W")

        # The best score we have found so far
        best_score = float("inf")

        # The best move we have found so far
        best_move = None

        # For each piece, find the best move
        for piece, piece_moves in moves.items():
            # For each move, find the best score
            for move in piece_moves:
                # Make a copy of the board
                new_board = copy.deepcopy(board)

                # Make the move
                new_board.move_piece(piece.pos, move)

                # Get the score for this move
                tmp = minimax(new_board, depth - 1, True)
                try:
                    score = tmp[0]
                except TypeError:
                    score = tmp

                # If this score is better than the best score, update the best score
                # DEBUG: print(f"[minimising] checking score: {score} (move: {piece.pos} -> {move})")
                if score < best_score:
                    # DEBUG: print(f"[minimising] UPDATING best_score: {best_score} -> {score} (move: {piece.pos} -> {move})")
                    best_score = score
                    best_move = (piece.pos, move)
                
        # DEBUG: print(f"[minimising] RETURNING best_score: {best_score} (move: {best_move})")
        return best_score, best_move