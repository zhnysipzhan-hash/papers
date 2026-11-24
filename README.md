# papers

Репозиторий для написания научных статей с помощью навыков **PaperOrchestra**.

Навыки скачаны из [Ar9av/PaperOrchestra](https://github.com/Ar9av/PaperOrchestra)
(коммит `6a31913`, лицензия MIT — см. `LICENSE`). Оригинальное описание
проекта — в `README.PaperOrchestra.md`.

## Что внутри

| Папка / файл | Что это |
|---|---|
| `skills/` | 9 навыков + общая папка `shared` |
| `.claude/skills/` | ссылки на навыки, чтобы Claude Code видел их в каждой сессии |
| `papers/` | сюда кладём статьи, одна папка на статью |
| `examples/` | готовые примеры: минимальный и полностью написанная статья с PDF |
| `docs/` | документация PaperOrchestra (архитектура, интеграция) |
| `requirements.txt` | Python-библиотеки для вспомогательных скриптов |

## Навыки

| Навык | Что делает |
|---|---|
| `paper-orchestra` | главный: запускает весь конвейер от идеи до PDF |
| `outline-agent` | шаг 1: план статьи |
| `plotting-agent` | шаг 2: графики и схемы |
| `literature-review-agent` | шаг 3: поиск литературы, Введение и Обзор |
| `section-writing-agent` | шаг 4: остальные разделы, таблицы |
| `content-refinement-agent` | шаг 5: имитация рецензии и доработка |
| `paper-autoraters` | оценка качества статьи и цитирования |
| `paper-writing-bench` | сделать тестовый набор из готовой статьи |
| `agent-research-aggregator` | собрать идею и результаты из заметок, если их нет |

## Как начать статью

1. Скажите Claude: «Создай папку для статьи `название`».
   Он выполнит:
   ```bash
   python skills/paper-orchestra/scripts/init_workspace.py --out papers/название/
   ```
2. Заполните (или попросите Claude помочь заполнить) файлы в `papers/название/inputs/`:
   - `idea.md` — идея статьи;
   - `experimental_log.md` — эксперименты и результаты;
   - `template.tex` — LaTeX-шаблон журнала или конференции;
   - `conference_guidelines.md` — требования: объём, обязательные разделы.
3. Скажите: «Запусти paper-orchestra на `papers/название`».

Готовая статья появится в `papers/название/final/`.
