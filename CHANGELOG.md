# Changelog

كل التغييرات الجوهرية في هذا المشروع تُوثَّق هنا.
الصيغة مبنية على [Keep a Changelog](https://keepachangelog.com/ar/1.1.0/)، والإصدارات تتبع [Semantic Versioning](https://semver.org/lang/ar/).

## [Unreleased]

### Added
- حزمة مجتمع كاملة: README احترافي بلقطات حقيقية، قوالب Issues (علة/ميزة)، قالب PR، بانر SVG بهوية بصرية موحدة، وشارات shields.io حقيقية (CI + MIT + Python 3.11+ + 13 اختباراً + بوابة ruff).

## [0.1.0] — 2026-10-29

### Added
- نواة اللعب: `board.py` — رقعة 8×8، أصناف Piece/Color/PieceType، ترميز FEN كامل (`to_fen` / `from_fen`)، وتنفيذ النقلات عبر `move_piece`.
- منطق الجولة: `game.py` — صنف `Game` يدير الحالة والدور والسجل، مع تحليل الحركات الجبرية (`e2e4`) ودعم الترقية (`e7e8Q`).
- واجهة الطرفية: `main.py` — حلقة REPL تفاعلية مع فحص ذاتي عند الإقلاع يطبع `All tests passed.`.
- واجهة ويب: `web.py` — FastAPI + صفحة HTML/JS مضمّنة، بمسارات `GET /api/state` و`POST /api/move` و`POST /api/reset` و`GET /`، مع إبراز آخر نقلة وسجل الحركات، ومنفذ قابل للضبط عبر `PORT`.
- الاختبارات: 13 اختباراً (`tests/test_perft.py` — التحقق المعياري Perft من توليد النقلات القانونية، و`tests/test_phase_a.py` — منطق اللعبة والحركات).
- التبعيات: `requirements.txt` (fastapi, pydantic, uvicorn) و`requirements-dev.txt` (pytest, ruff) — معلنة صراحة.
- CI (`.github/workflows/ci.yml`): pytest + gitleaks + وظيفة lint مستقلة ببوابة `ruff` (E9+F) على مصفوفة Python 3.11/3.12.
- أدوات الجودة: `ruff.toml` (قواعد E9+F الحتمية) و`.gitignore`.
- ملفات المجتمع الأساسية: LICENSE (MIT)، CONTRIBUTING.md، SECURITY.md.
