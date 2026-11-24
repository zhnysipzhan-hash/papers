# papers

Repository for writing research papers with the PaperOrchestra skill pack
(vendored from github.com/Ar9av/PaperOrchestra, commit 6a31913, MIT license).

- Skills live in `skills/`; `.claude/skills/*` are symlinks to them, so the
  `python skills/<skill>/scripts/...` commands inside every SKILL.md work as
  written when run from the repository root.
- Each paper gets its own workspace folder: `papers/<short-name>/`.
  Use it wherever a skill says `workspace/`, e.g.
  `python skills/paper-orchestra/scripts/init_workspace.py --out papers/<short-name>/`.
- Commit the inputs and the results (`inputs/`, `outline.json`, `figures/`,
  `final/paper.tex`, `final/paper.pdf`, `refs.bib`) so work survives between sessions.
- The user writes in Russian; reply in Russian.
