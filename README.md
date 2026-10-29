<p align="center">
  <img src=".github/assets/banner.svg" alt="Chess CLI — شطرنج الطرفية" width="100%">
</p>

# Chess CLI — شطرنج الطرفية

<div align="center">

[![CI](https://github.com/tibatechapp-ship-it/chess-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/tibatechapp-ship-it/chess-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/tests-13%20passing-brightgreen)
![Lint](https://img.shields.io/badge/lint-ruff%20E9%2BF%20gate-FCC21B)

</div>

---

## 💡 ما هذا المشروع؟

لعبة شطرنج كاملة تعمل في الطرفية، مكتوبة بـ**بايثون نقي** لمنطق اللعبة دون أي اعتماد خارجي — تصلح للتشغيل على أي جهاز فيه بايثون 3.11 فأحدث، من الحاسوب المكتبي إلى Raspberry Pi. اللعبة تدعم ترميز **FEN** الكامل (تصدير واستيراد أي وضعية)، وإدخال الحركات بالتدوين الجبري (`e2e4`، والترقية مثل `e7e8Q`)، وجولة لعب تفاعلية تتحقق من شرعية كل نقلة قبل تنفيذها. ولمن يفضّل المتصفح، يأتي المشروع مع **واجهة ويب FastAPI** جاهزة تعرض الرقعة بمؤشر آخر نقلة وسجل كامل للحركات.

ولأن هذا المشروع وُلد من أحشاء [nexus-core](https://github.com/tibatechapp-ship-it/nexus-core) — إطار الوكلاء الذكي الذي نبنيه بأنفسنا — فإن كل سطر فيه مرّ عبر خط توليد من 3 مراحل مع تحقق آلي من CodeGuardian، ثم **13 اختباراً** منها اختبارات **Perft** المعيارية للتحقق من صحة توليد النقلات القانونية. مشروع صغير الحجم، كبير في الانضباط الهندسي.

## ✨ المزايا

- **رقعة 8×8 كاملة** بجميع القطع الست (ملك، وزير، رخ، فيل، حصان، بيدق) مع تبديل الأدوار تلقائياً بين الأبيض والأسود.
- **دعم FEN كامل**: `to_fen` / `from_fen` — احفظ أي وضعية أو ابدأ منها، ما يتيح مشاركة لعبة قائمة بين لاعبين أو أجهزة.
- **تدوين جبري مبسّط**: اكتب `e2e4` لتحريك القطعة من مربع إلى مربع، و`e7e8Q` لترقية البيدق إلى وزير.
- **واجهة ويب جاهزة** (اختيارية): رقعة HTML/JS أنيقة فوق FastAPI، مع `/api/state` و`/api/move` و`/api/reset` — تعمل كواجهة برمجية لأي عميل آخر.
- **بوابات جودة آلية**: 13 اختباراً + بوابة `ruff` صارمة (E9+F) على إصداري 3.11 و3.12 + فحص أسرار gitleaks في الـCI.

## 🖥️ لقطة حقيقية من الطرفية

مخرجات فعلية من جلسة تشغيل حقيقية (`e2e4` ثم رد الأسود `e7e5`):

```text
$ python main.py
All tests passed.

Current board:
8 r n b q k b n r
7 p p p p p p p p
6 . . . . . . . .
5 . . . . . . . .
4 . . . . . . . .
3 . . . . . . . .
2 P P P P P P P P
1 R N B Q K B N R
  a b c d e f g h
Turn: WHITE
Enter move (e.g. e2e4, e7e8Q) or 'quit': e2e4

Current board:
8 r n b q k b n r
7 p p p p p p p p
6 . . . . . . . .
5 . . . . . . . .
4 . . . . P . . .
3 . . . . . . . .
2 P P P P . P P P
1 R N B Q K B N R
  a b c d e f g h
Turn: BLACK
```

## 🚀 التشغيل السريع

### الطرفية (بلا أي اعتماديات)

```bash
git clone https://github.com/tibatechapp-ship-it/chess-cli.git
cd chess-cli
python main.py
```

### واجهة الويب (FastAPI)

```bash
pip install -r requirements.txt   # fastapi + pydantic + uvicorn
python web.py                     # يعمل على 0.0.0.0:8000
# غيّر المنفذ عبر متغير البيئة: PORT=9000 python web.py
```

ثم افتح `http://localhost:8000` — ستجد الرقعة قابلة للعب بالنقر، مع إبراز آخر نقلة وسجل الحركات وزر إعادة الضبط.

## 🎮 كيف تلعب؟

| الإدخال | المعنى |
|---|---|
| `e2e4` | حرّك القطعة من المربع `e2` إلى `e4` |
| `e7e8Q` | نفس الأمر مع **ترقية** البيدق إلى وزير (`Q`) |
| `quit` | الخروج من الجولة |

في كل دور تُعرض الرقعة من منظور الأبيض (الصفوف 8→1 والأعمدة a→h)، وتُرفض أي نقلة غير قانونية مع بقاء الدور للاعب نفسه. عند بدء التشغيل ينفّذ `main.py` فحصاً ذاتياً سريعاً ويطبع `All tests passed.` قبل الجولة — طمأنة أن منطق اللعبة سليم قبل أول نقلة.

## 🌐 واجهة برمجية (REST)

واجهة الويب ليست صفحة فقط — إنها API كامل يمكنك بناء بوت أو عميل موبايل فوقه:

| المسار | النوع | الوظيفة |
|---|---|---|
| `/api/state` | GET | الوضعية الحالية (FEN + الدور + السجل) |
| `/api/move` | POST | تنفيذ نقلة؛ يرفض غير القانوني مع رسالة خطأ |
| `/api/reset` | POST | إعادة اللعبة للوضعية الابتدائية |
| `/` | GET | واجهة HTML/JS التفاعلية |

## 🧪 الاختبارات

```bash
pip install -r requirements-dev.txt   # pytest + ruff
python -m pytest -q                   # 13 passed
ruff check --config ruff.toml .       # بوابة E9+F
```

أهم ما يميز مجموعة الاختبارات هنا وجود اختبارات **Perft** — المعيار العالمي للتحقق من مولّدات النقلات: تُحصى كل النقلات القانونية حتى عمق معين وتُقارن بأرقام مرجعية معروفة. أي خطأ في قواعد الحركة (كالاستحواذ أو الترقية) يظهر فوراً كفرق في العدّ، لا كعلّة غامضة أثناء اللعب.

## 🗂️ بنية الملفات

| الملف | الوظيفة |
|---|---|
| `board.py` | الرقعة 8×8، القطع والألوان، FEN (تصدير/استيراد)، تنفيذ النقلات |
| `game.py` | صنف `Game`: إدارة الحالة، تحليل الحركات الجبرية، الترقية، السجل |
| `main.py` | حلقة اللعب التفاعلية (REPL) + فحص ذاتي عند الإقلاع |
| `web.py` | واجهة FastAPI + صفحة HTML/JS مضمّنة |
| `tests/` | 13 اختباراً: perft (صحة توليد النقلات) + phase_a (منطق اللعبة) |

## 🤖 كيف وُلد هذا المشروع؟

بصدقٍ وكامل الشفافية: هذا المشروع توليد لـ**[Nexus Studio](https://github.com/tibatechapp-ship-it/nexus-core)** عبر خط الـ**Chunking pipeline** (v1.45.0) — خطة من 3 خطوات إلى 3 ملفات، يتحقق كل منها عبر CodeGuardian. المهمة البشرية كانت جملة واحدة: *«لعبة شطرنج بواجهة نصية»*، والعمود الفقري كان `openai/gpt-oss-20b` عبر Groq API. نؤمن أن أفضل طريقة لإثبات قدرة أدواتنا أن تبني بها أدوات حقيقية ننشرها — وهذا المشروع دليل حي على ذلك.

## 🤝 المساهمة

نرحب بأي مساهمة! اقرأ [CONTRIBUTING.md](CONTRIBUTING.md) أولاً، وابدأ بفتح Issue بصيغة القوالب الجاهزة. أي تغيير في منطق اللعبة **يجب** أن يمر عبر الاختبارات (وأضف اختباراً لسلوك جديد)، والـCI بوابة إلزامية قبل الدمج.

## 🔐 الأمان

راجع [SECURITY.md](SECURITY.md) — وللثغرات استخدم [الإبلاغ الخاص عبر Security Advisories](https://github.com/tibatechapp-ship-it/chess-cli/security/advisories/new) ولا تفتح Issue عاماً.

## 📜 السجل

تاريخ التغييرات موثق في [CHANGELOG.md](CHANGELOG.md).

## 📄 الترخيص

مشروع مفتوح المصدر تحت ترخيص [MIT](LICENSE) — © 2026 Vixona Technologies (tibatechapp-ship-it).
