import os
import sys
from typing import List

# Ensure the project root is on the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from board import Board, Piece, PieceType, Color


def count_pieces(board: Board) -> int:
    return sum(1 for row in board._grid for p in row if p is not None)


def test_32_pieces() -> None:
    board = Board()
    assert count_pieces(board) == 32, "Starting position must contain 32 pieces"


def test_fen_roundtrip() -> None:
    original = Board()
    fen = original.to_fen()
    restored = Board(fen)
    assert restored.to_fen() == fen, "FEN round‑trip should produce identical string"
    # Verify piece placement matches original
    for r in range(8):
        for c in range(8):
            assert restored._grid[r][c] == original._grid[r][c]


def test_white_queen_d1() -> None:
    board = Board()
    queen = board.get_piece((7, 3))  # row 7 (rank 1), col 3 (file d)
    assert isinstance(queen, Piece), "Expected a piece at d1"
    assert queen.type == PieceType.QUEEN
    assert queen.color == Color.WHITE
    assert queen.symbol() == "Q"


def test_black_king_e8() -> None:
    board = Board()
    king = board.get_piece((0, 4))  # row 0 (rank 8), col 4 (file e)
    assert isinstance(king, Piece), "Expected a piece at e8"
    assert king.type == PieceType.KING
    assert king.color == Color.BLACK
    assert king.symbol() == "k"