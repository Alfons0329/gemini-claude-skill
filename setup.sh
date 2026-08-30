#!/usr/bin/env bash
# Install this repo's skills onto a new machine.
#
#   ./setup.sh              # install the work skills (loop-eng, writing-skills, interview-me)
#   ./setup.sh --all        # every skill in the repo, including interview prep
#   ./setup.sh --dry-run    # print what would happen, change nothing
#
# Safe to run twice. Every step checks before it acts.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRESS_ROOT="${LOOP_ENG_PROGRESS_ROOT:-$HOME/progress}"
DRY=0
PROFILE=work

for arg in "$@"; do
  case "$arg" in
    --all)     PROFILE=all ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown flag: $arg (try --help)" >&2; exit 2 ;;
  esac
done

run() { if [ "$DRY" = 1 ]; then echo "  would run: $*"; else "$@"; fi; }
say() { printf '%s\n' "$*"; }

WORK_SKILLS=(productivity/loop-eng productivity/writing-skills productivity/interview-me)
ALL_SKILLS=(
  productivity/loop-eng productivity/writing-skills productivity/interview-me
  productivity/notion-to-notebooklm
  interview/leetcode-discuss interview/leetcode-note interview/leetcode-roadmap
  interview/resume-jd-interview interview/sys-design-interview
)

if [ "$PROFILE" = all ]; then SKILLS=("${ALL_SKILLS[@]}"); else SKILLS=("${WORK_SKILLS[@]}"); fi

say "repo:     $REPO"
say "profile:  $PROFILE"
[ "$DRY" = 1 ] && say "mode:     DRY RUN — nothing will change"
say ""

# ---------------------------------------------------------------- 1. symlinks
# Every agent that reads a skills directory gets the same links. A directory
# that does not exist is skipped, not created — installing Gemini's skills on a
# machine with no Gemini is noise.
AGENT_DIRS=("$HOME/.claude/skills")
[ -d "$HOME/.gemini" ] && AGENT_DIRS+=("$HOME/.gemini/skills")
[ -d "$HOME/.antigravity" ] && AGENT_DIRS+=("$HOME/.antigravity/skills")

for dir in "${AGENT_DIRS[@]}"; do
  say "==> $dir"
  run mkdir -p "$dir"
  for rel in "${SKILLS[@]}"; do
    name="$(basename "$rel")"
    src="$REPO/$rel"
    dst="$dir/$name"
    if [ ! -d "$src" ] || [ ! -f "$src/SKILL.md" ]; then
      say "    skip $name (no SKILL.md — placeholder)"
      continue
    fi
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
      say "    SKIP $name — a real file/dir is already there, not overwriting"
      continue
    fi
    run ln -sfn "$src" "$dst"
    say "    link $name"
  done
  say ""
done

# ------------------------------------------------------- 2. the progress repo
# Private by design. Real ticket IDs, service names, and RCA writeups land here.
say "==> $PROGRESS_ROOT"
if [ -d "$PROGRESS_ROOT/.git" ]; then
  say "    already a git repo — left alone"
else
  run mkdir -p "$PROGRESS_ROOT"
  run git -C "$PROGRESS_ROOT" init -q
  if [ "$DRY" = 0 ]; then
    cat > "$PROGRESS_ROOT/README.md" <<'PROG_EOF'
# progress

Loop-eng artifacts. One directory per ticket ID.

Private. Real ticket IDs, service names, and root-cause writeups live here.
NEVER add a public remote to this repo.
PROG_EOF
    git -C "$PROGRESS_ROOT" add -A
    git -C "$PROGRESS_ROOT" -c user.name=setup -c user.email=setup@local commit -qm "init" || true
  fi
  say "    created + git init"
fi

if git -C "$PROGRESS_ROOT" remote 2>/dev/null | grep -q .; then
  say "    !! WARNING: this repo has a remote. Confirm it is private."
fi
say ""

# ----------------------------------------------- 3. the personal context file
# Layer 2: facts true on THIS machine only. Never committed to a team repo.
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
LINE="Loop-eng artifacts live under $PROGRESS_ROOT/, one directory per ticket ID."
say "==> $CLAUDE_MD"
if [ -f "$CLAUDE_MD" ] && grep -qF "Loop-eng artifacts live under" "$CLAUDE_MD"; then
  say "    progress-root line already present"
elif [ "$DRY" = 1 ]; then
  say "    would append: $LINE"
else
  mkdir -p "$HOME/.claude"
  { [ -f "$CLAUDE_MD" ] && printf '\n'; printf '# Personal context\n\n%s\n' "$LINE"; } >> "$CLAUDE_MD"
  say "    progress-root line added"
fi
say ""

say "Done."
say ""
say "Next:"
say "  1. Restart your agent session — skills load at startup."
say "  2. Check it took:  ls -l ${AGENT_DIRS[0]}"
say "  3. First ticket:   mkdir -p $PROGRESS_ROOT/<id> && \$EDITOR $PROGRESS_ROOT/<id>/<id>-ticket.md"
say "     then:           /loop-eng spec <id>"
