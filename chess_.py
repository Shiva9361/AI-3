import gym
import gym_chess

import chess
import chess.svg

import math
import time
import argparse

from typing import Optional, cast

from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut

TIME: int = 600


def evaluate(board: chess.Board, iswhite: bool = True) -> float:
    """
    Heuristic function to evaluate a chess position.
    Positive scores favor minmaxed player, negative scores favor opponent.
    """
    # Piece values
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    # Evaluate material
    material_score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            material_score += value if piece.color == chess.WHITE else -value

    # Evaluate mobility (number of legal moves)
    mobility_score = board.legal_moves.count()
    mobility_score = mobility_score * \
        10 if board.turn == chess.WHITE else -mobility_score * 10

    # Evaluate pawn structure (penalize doubled and isolated pawns)
    pawn_structure_score = 0
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        files = [chess.square_file(p) for p in pawns]
        for file in files:
            if files.count(file) > 1:  # Doubled pawns penalty
                pawn_structure_score += -20 if color == chess.WHITE else 20
            # Isolated pawns penalty
            if file not in files and (file - 1 not in files and file + 1 not in files):
                pawn_structure_score += -15 if color == chess.WHITE else 15

    # Combine scores
    total_score = material_score + mobility_score + pawn_structure_score

    return total_score if iswhite else -total_score


def minimax(board: chess.Board, depth: int, maximizing_player: bool, iswhite: bool = True) -> float:
    """
    @param board: chess.Board   
    @param depth: int
    @param maximizing_player: bool
    @return: float
    Minimax algorithm with depth limit.
    """

    if depth == 0 or board.is_game_over():
        return evaluate(board, iswhite)

    if maximizing_player:
        max_eval: float = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = minimax(board, depth-1, False, iswhite)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval: float = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = minimax(board, depth-1, True, iswhite)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval


def alphabeta(board: chess.Board, isMaxNode: bool, depth: int = 3, alpha: float = -math.inf, beta: float = math.inf, iswhite: bool = True) -> float:
    """
    @param board: chess.Board
    @param depth: int
    @param alpha: float
    @param beta: float
    @return: float
    Alpha-Beta pruning algorithm.
    """

    if depth == 0 or board.is_game_over():
        return evaluate(board, iswhite)

    if isMaxNode:
        max_eval: float = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = alphabeta(
                board, False, depth-1, alpha, beta, iswhite)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval: float = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = alphabeta(board, True, depth-1, alpha, beta, iswhite)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(board: chess.Board, depth: int = 3, algorithm: str = "minimax", iswhite: bool = True) -> Optional[chess.Move]:
    """
    @param board: chess.Board
    @param depth: int
    @param algorithm: str
    @return: Optional[chess.Move]
    Get the best move for the current player using the specified algorithm.
    """
    best_move: Optional[chess.Move] = None
    best_value: float = -math.inf
    for move in board.legal_moves:
        board.push(move)
        if algorithm == "minimax":
            value: float = minimax(board, depth-1, False, iswhite)
        else:
            value: float = alphabeta(
                board, False, depth-1, -math.inf, math.inf, iswhite)
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
    return best_move


@func_set_timeout(TIME)
def evaluate_algorithm(env: gym.Env, algorithm: str, depth: int = 3) -> list[chess.Move]:
    """
    @param env: gym.Env
    @param algorithm: str
    @param depth: int
    @return: list[chess.Move]
    Evaluate the algorithm using the chess environment.
    """
    done: bool = False
    moves: list[chess.Move] = []

    while not done:
        current_board: chess.Board = env.unwrapped._board.copy()
        best_move: Optional[chess.Move] = get_best_move(
            current_board, depth=depth, algorithm=algorithm, iswhite=env.unwrapped._board.turn == chess.WHITE)
        if best_move:
            _, _, done, _ = env.step(best_move)
            moves.append(best_move)
    return moves


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        "Evaluation of Minimax and Alpha-Beta pruning")
    parser.add_argument("--algorithm", type=str, default="minimax")

    args = parser.parse_args()

    env = cast(gym.Env, gym.make('Chess-v0'))
    env.reset()

    start_time: float = time.time()
    moves: list[chess.Move] = []
    try:
        print(f"Evaluating {args.algorithm}")
        moves = evaluate_algorithm(env, args.algorithm)
        end_time: float = time.time()
        elapsed_time: float = end_time - start_time
        print(f"Algorithm executed in {elapsed_time:.2f} seconds.")
    except FunctionTimedOut:
        print("Algorithm timed out.")

    env.reset()

    with open(f"gameplay_frames/{args.algorithm}_frame_000.svg", "w") as f:
        f.write(chess.svg.board(env.unwrapped._board, size=500))

    for idx, move in enumerate(moves):
        env.step(move)
        with open(f"gameplay_frames/{args.algorithm}_frame_{idx+1:03d}.svg", "w") as f:
            f.write(chess.svg.board(env.unwrapped._board, size=500))

    env.close()
