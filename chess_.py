import gym
import gym_chess

import pygame
import chess

import random
import math
import time
import os

from typing import Optional, cast

from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut

TIME: int = 600


def evaluate(board: chess.Board) -> float:
    """
    Heuristic function to evaluate a chess position.
    Positive scores favor White, negative scores favor Black.
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
    mobility_score = board.legal_moves.count(
    ) if board.turn == chess.WHITE else board.legal_moves.count()

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

    return total_score


def minimax(board: chess.Board, depth: int, maximizing_player: bool) -> float:
    """
    @param board: chess.Board
    @param depth: int
    @param maximizing_player: bool
    @return: float
    Minimax algorithm with depth limit.
    """

    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing_player:
        max_eval: float = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = minimax(board, depth-1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval: float = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = minimax(board, depth-1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval


def alphabeta(board: chess.Board, isMaxNode: bool, depth: int = 3, alpha: float = -math.inf, beta: float = math.inf,) -> float:
    """
    @param board: chess.Board
    @param depth: int
    @param alpha: float
    @param beta: float
    @return: float
    Alpha-Beta pruning algorithm.
    """

    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if isMaxNode:
        max_eval: float = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval: float = alphabeta(board, False, depth-1, alpha, beta)
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
            eval: float = alphabeta(board, True, depth-1, alpha, beta)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(board: chess.Board, depth: int = 3, algorithm: str = "minimax") -> Optional[chess.Move]:
    best_move: Optional[chess.Move] = None
    best_value: float = -math.inf
    for move in board.legal_moves:
        board.push(move)
        if algorithm == "minimax":
            value: float = minimax(board, depth-1, False)
        else:
            value: float = alphabeta(board, True, depth-1, -math.inf, math.inf)
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
    return best_move


def draw_board() -> None:
    """
    @return: None
    Draw the chessboard using Pygame.
    """
    colors: list[tuple[int, int, int]] = [(238, 238, 210), (118, 150, 86)]
    for row in range(8):
        for col in range(8):
            color: tuple[int, int, int] = colors[(row + col) % 2]
            pygame.draw.rect(screen, color,
                             pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(board: chess.Board) -> None:
    """
    @param board: chess.Board
    @return: None
    Draw pieces on the board using Pygame.
    The pieces are represented by images loaded from the 'pieces' folder.
    """

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol: str = piece.symbol()
            piece_image: pygame.Surface = PIECE_IMAGES[symbol]
            x: int = chess.square_file(square) * SQ_SIZE
            y: int = (7 - chess.square_rank(square)) * SQ_SIZE
            screen.blit(pygame.transform.scale(
                piece_image, (SQ_SIZE, SQ_SIZE)), (x, y))


@func_set_timeout(TIME)
def evaluate_algorithm(env: gym.Env, algorithm: str, depth: int = 3) -> None:
    done: bool = False
    clock: pygame.time.Clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    break

        if env.unwrapped._board.turn == chess.WHITE:
            current_board: chess.Board = env.unwrapped._board.copy()  # type: ignore
            best_move: Optional[chess.Move] = get_best_move(
                current_board, depth=depth, algorithm=algorithm)
            print(f"Best move: {best_move}")
            if best_move:
                _, _, done, _ = env.step(best_move)
        else:
            legal_moves: list[chess.Move] = list(env.legal_moves)
            if legal_moves:
                random_move: chess.Move = random.choice(legal_moves)
                _, _, done, _ = env.step(random_move)
        draw_board()
        draw_pieces(env.unwrapped._board)
        pygame.display.flip()
        clock.tick(15)


if __name__ == "__main__":

    env = cast(gym.Env, gym.make('Chess-v0'))
    env.reset()

    pygame.init()
    WINDOW_SIZE: int = 640
    SQ_SIZE: int = WINDOW_SIZE // 8

    screen: pygame.Surface = pygame.display.set_mode(
        (WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Chess AI - Minimax")

    PIECES_FOLDER: str = os.path.join(os.path.dirname(__file__), 'pieces')
    PIECE_IMAGES: dict[str, pygame.Surface] = {}
    PIECES_DICT = {
        'r': 'black_rook.svg', 'n': 'black_knight.svg', 'b': 'black_bishop.svg', 'q': 'black_queen.svg', 'k': 'black_king.svg', 'p': 'black_pawn.svg',
        'R': 'white_rook.svg', 'N': 'white_knight.svg', 'B': 'white_bishop.svg', 'Q': 'white_queen.svg', 'K': 'white_king.svg', 'P': 'white_pawn.svg'
    }

    for piece, filename in PIECES_DICT.items():
        PIECE_IMAGES[piece] = pygame.image.load(
            os.path.join(PIECES_FOLDER, filename))

    evaluate_algorithm(env, "minimax")
    pygame.quit()
    env.close()
