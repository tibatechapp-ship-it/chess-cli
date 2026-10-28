#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py – Text‑based chess game loop.

This module demonstrates the use of :class:`Game` from ``game.py``.
It provides a simple REPL that prints the board, accepts moves in
algebraic notation (e.g. ``e2e4`` or ``e7e8Q`` for promotion), and
updates the game state.  Basic unit tests are executed when the file
is run directly.
"""

from __future__ import annotations


# Import the core game logic and board representation.
try:
    from game import Game, Color, PieceType
    from board import Board
except Exception as exc:  # pragma: no cover
    raise ImportError("Required modules not found") from exc


def _apply_move(game: Game, move: "Game.Move") -> None:
    """
    Apply a parsed move to the board.

    The :class:`Board` class is expected to expose either a ``move_piece``
    or ``move`` method that accepts ``src``, ``dst`` and an optional
    ``promotion`` argument.  If neither method is available an
    ``AttributeError`` is raised.
    """
    board = game.board
    if hasattr(board, "move_piece"):
        board.move_piece(move.src, move.dst)
    elif hasattr(board, "move"):
        board.move(move.src, move.dst)
    else:
        raise AttributeError("Board has no method to apply a move")


def main() -> None:
    """
    Main REPL loop for the text‑based chess game.

    The loop prints the current board, prompts the user for a move,
    applies the move, toggles the active colour, and repeats until
    the user enters ``quit`` or ``exit``.
    """
    game = Game()
    while True:
        print("\nCurrent board:")
        print(game.board)
        print(f"Turn: {game.turn.name}")
        move_str = input("Enter move (e.g. e2e4, e7e8Q) or 'quit': ").strip()
        if move_str.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        try:
            move = game.parse_move(move_str)
            _apply_move(game, move)
            game.turn = Color.BLACK if game.turn == Color.WHITE else Color.WHITE
            game.history.append(move)
        except Exception as exc:
            print(f"Error: {exc}")


# --------------------------------------------------------------------------- #
# Simple unit tests
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    def run_tests() -> None:
        """Run a handful of sanity checks on the API."""
        g = Game()
        assert g.turn == Color.WHITE, "Initial turn should be WHITE"
        assert isinstance(g.board, Board), "Game should contain a Board instance"

        # Test move parsing
        m1 = g.parse_move("e2e4")
        assert m1.src == (6, 4), f"Expected src (6,4), got {m1.src}"
        assert m1.dst == (4, 4), f"Expected dst (4,4), got {m1.dst}"
        assert m1.promotion is None, "No promotion expected"

        m2 = g.parse_move("e7e8Q")
        assert m2.promotion == PieceType.QUEEN, "Promotion should be QUEEN"

        # Test board string representation
        board_str = str(g.board)
        assert isinstance(board_str, str) and len(board_str) > 0, "Board string should be non‑empty"

        print("All tests passed.")

    run_tests()
    main()