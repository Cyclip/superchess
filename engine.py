import copy
import engine_utils
import random

MAX_DEPTH = 2
SENTINEL_VALUE = None

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
        score, move = minimax(board, MAX_DEPTH, -999999, 999999, True)

        if move == SENTINEL_VALUE:
            # No moves available
            print(f"No moves available")
            print(f"Score: {score}")
            print(f"Game over: {board.game_over}")
            print(f"[!] DEBUG: Playing random move [!]")
            moves = engine_utils.get_all_moves(board, "B")
            move = random.choice(list(moves.values()))[0]

        # Add to transposition table
        engine_utils.add_transposition(board, score, move, MAX_DEPTH)

    print(f"Playing move {move} with score {score}")

    # Return the move in format (start_pos, end_pos)
    return move


def minimax(board, depth, alpha, beta, maximizingPlayer):
    """
    Minimax algorithm with alpha-beta pruning.
    """

    if depth == 0 or board.game_over:
        # negative score means black (us) is winning
        return -engine_utils.evaluate_board(board), None
    
    if maximizingPlayer:
        # We want to maximize the score
        bestValue = -999999

        # Get all possible moves
        pieces, moves = engine_utils.get_all_moves(board, "B")

        bestMove = None

        for piece, piece_moves in moves.items():
            # For each move, find the best score
            for move in piece_moves:
                # Copy the board
                newBoard = copy.deepcopy(board)

                # Make the move
                newBoard.move_piece(piece.pos, move)

                # Get the score
                value, _ = minimax(newBoard, depth - 1, alpha, beta, False)

                # Update the best score
                if value > bestValue:
                    bestValue = value
                    bestMove = (piece.pos, move)

                # Update alpha
                alpha = max(alpha, bestValue)

                # Prune
                if beta <= alpha:
                    break

        return bestValue, bestMove
    
    else:
        # We want to minimize the score
        bestValue = 999999

        # Get all possible moves
        pieces, moves = engine_utils.get_all_moves(board, "W")

        bestMove = None

        for piece, piece_moves in moves.items():
            # For each move, find the best score
            for move in piece_moves:
                # Copy the board
                newBoard = copy.deepcopy(board)

                # Make the move
                newBoard.move_piece(piece.pos, move)

                # Get the score
                value, _ = minimax(newBoard, depth - 1, alpha, beta, True)

                # Update the best score
                if value < bestValue:
                    bestValue = value
                    bestMove = (piece.pos, move)

                # Update beta
                beta = min(beta, bestValue)

                # Prune
                if beta <= alpha:
                    break

        return bestValue, bestMove