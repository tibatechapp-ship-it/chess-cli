#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
board.py – Chess board representation and basic manipulation.

This module defines the core data structures for a chess board:
* PieceType – enumeration of the six piece types.
* Color – enumeration of the two colours.
* Piece – immutable representation of a single piece.
* Board – 8×8 board with helper methods for construction, querying,
  moving pieces, and FEN conversion.

The module is self‑contained and includes a small test suite in
`__main__` that demonstrates the API.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, List

# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #

class PieceType(Enum):
    KING   = auto()
    QUEEN  = auto()
    ROOK   = auto()
    BISHOP = auto()
    KNIGHT = auto()
    PAWN   = auto()


class Color(Enum):
    WHITE = auto()
    BLACK = auto()


# --------------------------------------------------------------------------- #
# Piece
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Piece:
    """Immutable chess piece."""
    type: PieceType
    color: Color

    def symbol(self) -> str:
        """Return the single‑character symbol used in FEN and board printing."""
        symbols = {
            PieceType.KING:   'K',
            PieceType.QUEEN:  'Q',
            PieceType.ROOK:   'R',
            PieceType.BISHOP: 'B',
            PieceType.KNIGHT: 'N',
            PieceType.PAWN:   'P',
        }
        sym = symbols[self.type]
        return sym.upper() if self.color == Color.WHITE else sym.lower()


# --------------------------------------------------------------------------- #
# Board
# --------------------------------------------------------------------------- #

Position = Tuple[int, int]  # (row, col), 0‑based, row 0 is rank 8

class Board:
    """8×8 chess board."""

    def __init__(self, fen: Optional[str] = None) -> None:
        """
        Initialise a board.

        If *fen* is provided, the board is populated from the FEN string.
        Otherwise the standard starting position is used.
        """
        self._grid: List[List[Optional[Piece]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]
        if fen:
            self.from_fen(fen)
        else:
            self._setup_starting_position()

    # --------------------------------------------------------------------- #
    # Construction helpers
    # --------------------------------------------------------------------- #

    def _setup_starting_position(self) -> None:
        """Populate the board with the standard starting position."""
        # Helper to place a row of pieces
        def place_row(row: int, colour: Color, order: List[PieceType]) -> None:
            for col, ptype in enumerate(order):
                self._grid[row][col] = Piece(ptype, colour)

        # Back rank
        back = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP,
            PieceType.QUEEN, PieceType.KING, PieceType.BISHOP,
            PieceType.KNIGHT, PieceType.ROOK
        ]
        place_row(0, Color.BLACK, back)
        place_row(7, Color.WHITE, back)

        # Pawns
        for col in range(8):
            self._grid[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self._grid[6][col] = Piece(PieceType.PAWN, Color.WHITE)

    # --------------------------------------------------------------------- #
    # Querying
    # --------------------------------------------------------------------- #

    @staticmethod
    def _is_valid_position(pos: Position) -> bool:
        r, c = pos
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece(self, pos: Position) -> Optional[Piece]:
        """Return the piece at *pos* or None if empty."""
        if not self._is_valid_position(pos):
            raise ValueError(f"Invalid board position: {pos}")
        return self._grid[pos[0]][pos[1]]

    def set_piece(self, pos: Position, piece: Optional[Piece]) -> None:
        """Place *piece* at *pos*, overwriting any existing piece."""
        if not self._is_valid_position(pos):
            raise ValueError(f"Invalid board position: {pos}")
        self._grid[pos[0]][pos[1]] = piece

    # --------------------------------------------------------------------- #
    # Movement
    # --------------------------------------------------------------------- #

    def move_piece(self, src: Position, dst: Position) -> None:
        """Move a piece from src to dst. Raises ValueError if illegal."""
        if not (self._is_valid_position(src) and self._is_valid_position(dst)):
            raise ValueError(f"Invalid move from {src} to {dst}")
        piece = self.get_piece(src)
        if piece is None:
            raise ValueError(f"No piece at source position {src}")
        validators = {
            PieceType.PAWN: self._is_valid_pawn,
            PieceType.KNIGHT: self._is_valid_knight,
            PieceType.BISHOP: self._is_valid_bishop,
            PieceType.ROOK: self._is_valid_rook,
            PieceType.QUEEN: self._is_valid_queen,
            PieceType.KING: self._is_valid_king,
        }
        validator = validators.get(piece.type)
        if validator is None or not validator(src, dst):
            raise ValueError(f"Illegal move: {piece.type.name} from {src} to {dst}")
        self.set_piece(dst, piece)
        self.set_piece(src, None)

    # --------------------------------------------------------------------- #
    # FEN conversion
    # --------------------------------------------------------------------- #

    def _is_valid_pawn(self, src: Position, dst: Position) -> bool:
        """Check if a pawn move from src to dst is legal (no en passant, no promotion)."""
        piece = self.get_piece(src)
        if piece is None or piece.type != PieceType.PAWN:
            return False
        rs, cs = src
        rd, cd = dst
        row_delta = rd - rs
        col_delta = cd - cs
        if piece.color == Color.WHITE:
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1
        if col_delta == 0 and row_delta == direction:
            return self.get_piece(dst) is None
        if col_delta == 0 and row_delta == 2 * direction and rs == start_row:
            mid = (rs + direction, cs)
            return self.get_piece(dst) is None and self.get_piece(mid) is None
        if abs(col_delta) == 1 and row_delta == direction:
            target = self.get_piece(dst)
            return target is not None and target.color != piece.color
        return False

    def _is_path_clear(self, src: Position, dst: Position) -> bool:
        """Check all squares strictly between src and dst are empty."""
        rs, cs = src
        rd, cd = dst
        row_step = (rd > rs) - (rd < rs)
        col_step = (cd > cs) - (cd < cs)
        r, c = rs + row_step, cs + col_step
        while (r, c) != (rd, cd):
            if self.get_piece((r, c)) is not None:
                return False
            r += row_step
            c += col_step
        return True

    def _is_valid_knight(self, src: Position, dst: Position) -> bool:
        """Knight: L-shape to empty or enemy square."""
        piece = self.get_piece(src)
        if piece is None or piece.type != PieceType.KNIGHT:
            return False
        dr = abs(dst[0] - src[0])
        dc = abs(dst[1] - src[1])
        if (dr, dc) not in {(1, 2), (2, 1)}:
            return False
        target = self.get_piece(dst)
        return target is None or target.color != piece.color

    def _is_valid_bishop(self, src: Position, dst: Position) -> bool:
        """Bishop: diagonal, clear path, empty or enemy target."""
        piece = self.get_piece(src)
        if piece is None or piece.type != PieceType.BISHOP:
            return False
        dr = abs(dst[0] - src[0])
        dc = abs(dst[1] - src[1])
        if dr != dc or dr == 0:
            return False
        target = self.get_piece(dst)
        if target is not None and target.color == piece.color:
            return False
        return self._is_path_clear(src, dst)

    def _is_valid_rook(self, src: Position, dst: Position) -> bool:
        """Rook: straight line, clear path, empty or enemy target."""
        piece = self.get_piece(src)
        if piece is None or piece.type != PieceType.ROOK:
            return False
        if (src[0] == dst[0]) == (src[1] == dst[1]):
            return False
        target = self.get_piece(dst)
        if target is not None and target.color == piece.color:
            return False
        return self._is_path_clear(src, dst)

    def _is_valid_queen(self, src: Position, dst: Position) -> bool:
        """Queen: rook or bishop movement, clear path."""
        piece = self.get_piece(src)
        if piece is None or piece.type != PieceType.QUEEN:
            return False
        dr = abs(dst[0] - src[0])
        dc = abs(dst[1] - src[1])
        target = self.get_piece(dst)
        if target is not None and target.color == piece.color:
            return False
        if dr == dc and dr > 0:
            return self._is_path_clear(src, dst)
        if (src[0] == dst[0]) != (src[1] == dst[1]):
            return self._is_path_clear(src, dst)
        return False

    def _is_valid_king(self, src: Position, dst: Position) -> bool:
        """King: 1 square any direction to empty or enemy."""
        piece = self.get_piece(src)
        if piece is None or piece.type != PieceType.KING:
            return False
        if max(abs(dst[0] - src[0]), abs(dst[1] - src[1])) != 1:
            return False
        target = self.get_piece(dst)
        return target is None or target.color != piece.color

    def _is_square_attacked(self, pos: Position, by_color: Color) -> bool:
        """Check if pos is attacked by any piece of by_color (ignoring what is on pos)."""
        pr, pc = pos
        for r in range(8):
            for c in range(8):
                piece = self._grid[r][c]
                if piece is None or piece.color != by_color:
                    continue
                pt = piece.type
                dr = pr - r
                dc = pc - c
                if pt == PieceType.PAWN:
                    direction = -1 if by_color == Color.WHITE else 1
                    if dr == direction and abs(dc) == 1:
                        return True
                elif pt == PieceType.KNIGHT:
                    if (abs(dr), abs(dc)) in {(1, 2), (2, 1)}:
                        return True
                elif pt == PieceType.KING:
                    if max(abs(dr), abs(dc)) == 1:
                        return True
                elif pt == PieceType.BISHOP:
                    if abs(dr) == abs(dc) and dr != 0 and self._is_path_clear((r, c), pos):
                        return True
                elif pt == PieceType.ROOK:
                    if (dr == 0) != (dc == 0) and self._is_path_clear((r, c), pos):
                        return True
                elif pt == PieceType.QUEEN:
                    if abs(dr) == abs(dc) and dr != 0 and self._is_path_clear((r, c), pos):
                        return True
                    if (dr == 0) != (dc == 0) and self._is_path_clear((r, c), pos):
                        return True
        return False

    def to_fen(self) -> str:
        """
        Return the board state as a FEN string (only piece placement).

        Example: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        """
        rows = []
        for r in range(8):
            empty = 0
            row_str = ""
            for c in range(8):
                piece = self._grid[r][c]
                if piece is None:
                    empty += 1
                else:
                    if empty:
                        row_str += str(empty)
                        empty = 0
                    row_str += piece.symbol()
            if empty:
                row_str += str(empty)
            rows.append(row_str)
        return "/".join(rows)

    def from_fen(self, fen: str) -> None:
        """
        Populate the board from a FEN string (piece placement only).

        Raises ValueError if the FEN is malformed.
        """
        rows = fen.strip().split("/")
        if len(rows) != 8:
            raise ValueError(f"Invalid FEN: expected 8 rows, got {len(rows)}")
        for r, row in enumerate(rows):
            c = 0
            for ch in row:
                if ch.isdigit():
                    skip = int(ch)
                    if skip < 1 or skip > 8:
                        raise ValueError(f"Invalid digit '{ch}' in FEN")
                    c += skip
                else:
                    if c >= 8:
                        raise ValueError(f"Too many squares in row {r+1}")
                    color = Color.WHITE if ch.isupper() else Color.BLACK
                    try:
                        ptype = {
                            'K': PieceType.KING,
                            'Q': PieceType.QUEEN,
                            'R': PieceType.ROOK,
                            'B': PieceType.BISHOP,
                            'N': PieceType.KNIGHT,
                            'P': PieceType.PAWN,
                        }[ch.upper()]
                    except KeyError:
                        raise ValueError(f"Unknown piece symbol '{ch}' in FEN")
                    self._grid[r][c] = Piece(ptype, color)
                    c += 1
            if c != 8:
                raise ValueError(f"Row {r+1} does not contain 8 squares")

    # --------------------------------------------------------------------- #
    # Representation
    # --------------------------------------------------------------------- #

    def __str__(self) -> str:
        """Return a human‑readable board representation."""
        lines = []
        for r in range(8):
            line = f"{8 - r} "
            for c in range(8):
                piece = self._grid[r][c]
                line += piece.symbol() if piece else "."
                line += " "
            lines.append(line.rstrip())
        lines.append("  a b c d e f g h")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Board fen='{self.to_fen()}'>"

# --------------------------------------------------------------------------- #
# Test suite
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # Basic sanity checks
    board = Board()
    print("Initial board:")
    print(board)
    print("\nFEN:", board.to_fen())

    # Move white pawn from e2 to e4
    board.move_piece((6, 4), (4, 4))
    print("\nAfter e2-e4:")
    print(board)
    print("\nFEN:", board.to_fen())

    # Load a custom position via FEN
    custom_fen = "r1bqkbnr/pppppppp/2n5/8/8/5N2/PPPPPPPP/RNBQKB1R"
    board.from_fen(custom_fen)
    print("\nCustom position from FEN:")
    print(board)
    print("\nFEN:", board.to_fen())

    # Verify that to_fen/from_fen round‑trip works
    assert board.to_fen() == custom_fen, "Round‑trip FEN mismatch"

    print("\nAll tests passed.")