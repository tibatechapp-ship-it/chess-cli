#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
game.py – Core game logic for a text‑based chess application.

This module defines a :class:`Game` class that manages a chess board,
the current player, move history and basic game state checks.
It relies on the :class:`Board` implementation from ``board.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional

# Import the board implementation and related enums.
# The module is expected to expose the following names:
#   - Board
#   - Color
#   - PieceType
#   - Piece
try:
    from board import Board, Color, PieceType, Piece
except Exception as exc:  # pragma: no cover
    raise ImportError("board module not found or missing required symbols") from exc


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def algebraic_to_index(pos: str) -> Tuple[int, int]:
    """
    Convert a position in algebraic notation (e.g. 'e2') to a (row, col) index.
    Row 0 corresponds to rank 8, column 0 to file 'a'.
    """
    if len(pos) != 2:
        raise ValueError(f"Invalid position: {pos}")
    file_char, rank_char = pos[0], pos[1]
    if file_char not in "abcdefgh" or rank_char not in "12345678":
        raise ValueError(f"Invalid position: {pos}")
    col = ord(file_char) - ord("a")
    row = 8 - int(rank_char)  # rank 8 -> row 0
    return row, col


def index_to_algebraic(row: int, col: int) -> str:
    """Inverse of :func:`algebraic_to_index`."""
    return f"{chr(ord('a') + col)}{8 - row}"


# --------------------------------------------------------------------------- #
# Game
# --------------------------------------------------------------------------- #

@dataclass
class Move:
    """Simple representation of a move."""
    src: Tuple[int, int]
    dst: Tuple[int, int]
    promotion: Optional[PieceType] = None


class Game:
    """
    Encapsulates the state of a chess game.

    The class does **not** perform full move legality checks; it merely
    updates the board and toggles the active colour.  This is sufficient
    for a text‑based demo and for unit tests that exercise the API.
    """

    def __init__(self, fen: Optional[str] = None) -> None:
        """
        Initialise a new game.

        Parameters
        ----------
        fen : str, optional
            FEN string to initialise the board.  If omitted, the standard
            starting position is used.
        """
        self.board = Board(fen)
        self.turn = Color.WHITE
        self.history: List[Move] = []

    # --------------------------------------------------------------------- #
    # Move handling
    # --------------------------------------------------------------------- #

    def parse_move(self, move_str: str) -> Move:
        """
        Parse a move string in the form 'e2e4' or 'e7e8Q'.

        The promotion piece is optional and must be one of 'Q', 'R', 'B', 'N'.
        """
        if len(move_str) < 4:
            raise ValueError(f"Move string too short: {move_str}")

        src_str, dst_str = move_str[:2], move_str[2:4]
        promotion = None
        if len(move_str) > 4:
            promo_char = move_str[4].upper()
            promo_map = {
                "Q": PieceType.QUEEN,
                "R": PieceType.ROOK,
                "B": PieceType.BISHOP,
                "N": PieceType.KNIGHT,
            }
            if promo_char not in promo_map:
                raise ValueError(f"Invalid promotion piece: {promo_char}")
            promotion = promo_map[promo_char]

        src = algebraic_to_index(src_str)
        dst = algebraic_to_index(dst_str)
        return Move(src, dst, promotion)

    def make_move(self, move_str: str) -> bool:
        """
        Execute a move given in algebraic notation.

        Returns
        -------
        bool
            ``True`` if the move was applied, ``False`` otherwise.
        """
        try:
            move = self.parse_move(move_str)
        except ValueError:
            return False

        src_row, src_col = move.src
        dst_row, dst_col = move.dst

        # Retrieve the piece at the source square.
        piece = self.board._grid[src_row][src_col]  # type: ignore[attr-defined]
        if piece is None:
            return False
        if piece.color != self.turn:
            return False

        # Handle promotion: replace the piece with a new one of the same colour.
        if move.promotion:
            promoted_piece = Piece(move.promotion, self.turn)
            self.board._grid[dst_row][dst_col] = promoted_piece  # type: ignore[attr-defined]
        else:
            self.board._grid[dst_row][dst_col] = piece  # type: ignore[attr-defined]

        # Clear the source square.
        self.board._grid[src_row][src_col] = None  # type: ignore[attr-defined]

        # Record the move.
        self.history.append(move)

        # Toggle the active colour.
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
        return True

    # --------------------------------------------------------------------- #
    # Game state queries
    # --------------------------------------------------------------------- #

    def is_game_over(self) -> bool:
        """
        Determine if the game has ended.

        This method attempts to call ``is_checkmate`` or ``is_stalemate`` on
        the underlying board.  If those methods are not present, it simply
        returns ``False``.
        """
        try:
            if self.board.is_checkmate(self.turn):  # type: ignore[attr-defined]
                return True
            if self.board.is_stalemate(self.turn):  # type: ignore[attr-defined]
                return True
        except AttributeError:
            pass
        return False

    def get_winner(self) -> Optional[Color]:
        """
        Return the colour of the winner if the game is over.

        If the game is not over, ``None`` is returned.
        """
        if not self.is_game_over():
            return None
        # The player who just moved is the winner.
        return Color.BLACK if self.turn == Color.WHITE else Color.WHITE

    # --------------------------------------------------------------------- #
    # Convenience
    # --------------------------------------------------------------------- #

    def __str__(self) -> str:
        """Return a string representation of the board."""
        return str(self.board)

    def print_board(self) -> None:
        """Print the board to stdout."""
        print(self.__str__())


# --------------------------------------------------------------------------- #
# Demo / tests
# --------------------------------------------------------------------------- #

if __name__ == "__main__":  # pragma: no cover
    # Simple demonstration of the Game class.
    game = Game()
    print("Initial position:")
    game.print_board()

    # Make a few moves.
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "d2d3", "f8c5"]
    for mv in moves:
        if not game.make_move(mv):
            print(f"Failed to make move: {mv}")
        else:
            print(f"\nAfter move {mv}:")
            game.print_board()

    # Attempt a promotion.
    # Place a pawn on e7 for white to promote.
    # For demonstration, we manually set the board state.
    game.board._grid[1][4] = Piece(PieceType.PAWN, Color.WHITE)  # e7
    game.turn = Color.WHITE
    print("\nBefore promotion:")
    game.print_board()
    if game.make_move("e7e8Q"):
        print("\nAfter promotion to Queen:")
        game.print_board()
    else:
        print("Promotion move failed.")

    # Check game over status (should be False).
    print("\nGame over?", game.is_game_over())
    print("Winner:", game.get_winner())