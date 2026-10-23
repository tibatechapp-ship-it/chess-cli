"""Phase A tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from board import Board, Color, Piece, PieceType


def _clear(b):
    for r in range(8):
        for c in range(8):
            b.set_piece((r, c), None)


def test_square_attacked_by_pawn():
    b = Board()
    assert b._is_square_attacked((5, 3), Color.WHITE)
    assert b._is_square_attacked((5, 5), Color.WHITE)
    assert not b._is_square_attacked((4, 4), Color.WHITE)


def test_square_attacked_by_knight():
    b = Board()
    assert b._is_square_attacked((5, 2), Color.WHITE)
    assert b._is_square_attacked((5, 0), Color.WHITE)


def test_no_check_initial():
    b = Board()
    assert not b.is_in_check(Color.WHITE)
    assert not b.is_in_check(Color.BLACK)


def test_pinned_knight_rejected():
    b = Board(); _clear(b)
    b.set_piece((0, 4), Piece(PieceType.ROOK, Color.BLACK))
    b.set_piece((6, 4), Piece(PieceType.KNIGHT, Color.WHITE))
    b.set_piece((7, 4), Piece(PieceType.KING, Color.WHITE))
    b.turn = Color.WHITE
    try:
        b.move_piece((6, 4), (4, 3))
        assert False
    except ValueError as e:
        assert "check" in str(e).lower()
    assert b.get_piece((6, 4)) is not None


def test_legal_moves_initial():
    b = Board()
    assert len(b._legal_moves_for(Color.WHITE)) == 20
    assert len(b._legal_moves_for(Color.BLACK)) == 20


def test_fools_mate():
    b = Board()
    b.move_piece((6, 5), (5, 5))
    b.move_piece((1, 4), (3, 4))
    b.move_piece((6, 6), (4, 6))
    b.move_piece((0, 3), (4, 7))
    assert b.is_checkmate(Color.WHITE)
    assert b.game_status() == "checkmate_white"


def test_stalemate():
    b = Board(); _clear(b)
    b.set_piece((0, 0), Piece(PieceType.KING, Color.BLACK))
    b.set_piece((2, 1), Piece(PieceType.QUEEN, Color.WHITE))
    b.set_piece((1, 2), Piece(PieceType.KING, Color.WHITE))
    b.turn = Color.BLACK
    assert not b.is_in_check(Color.BLACK)
    assert b.is_stalemate(Color.BLACK)
    assert b.game_status() == "stalemate_black"


def test_turn_tracking():
    b = Board()
    assert b.turn == Color.WHITE
    b.move_piece((6, 4), (4, 4))
    assert b.turn == Color.BLACK
    try:
        b.move_piece((6, 3), (4, 3))
        assert False
    except ValueError as e:
        assert "turn" in str(e).lower()
    b.move_piece((1, 4), (3, 4))
    assert b.turn == Color.WHITE


def test_ongoing():
    assert Board().game_status() == "ongoing"
