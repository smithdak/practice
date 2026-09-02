# New Terminal Pickup

Use this page when you open a fresh terminal and want the repository ready to
work in. It assumes you have a copy of the kit — either a Git clone or a
downloaded archive — and a POSIX shell with Python 3 available.

Set two variables once, then the rest of the page is copy-paste. Adjust the
paths to wherever you keep projects and downloads.

```bash
PRACTICE_DIR="$HOME/projects/practice"
PRACTICE_ARCHIVE="$HOME/Downloads/practice-swarm-kit.zip"   # only for the archive route
```

> On WSL, a Windows download usually lives under
> `/mnt/c/Users/<your-windows-user>/Downloads`.

## Get a working copy

From a Git clone:

```bash
mkdir -p "$(dirname "$PRACTICE_DIR")"
git clone <repository-url> "$PRACTICE_DIR"
cd "$PRACTICE_DIR"
./scripts/init.sh
```

From a downloaded archive (this **removes** any existing copy at the target
path — check it first if you have local work there):

```bash
mkdir -p "$(dirname "$PRACTICE_DIR")"
cd "$(dirname "$PRACTICE_DIR")"
rm -rf practice-swarm-kit "$PRACTICE_DIR"
unzip "$PRACTICE_ARCHIVE"
mv practice-swarm-kit "$PRACTICE_DIR"
cd "$PRACTICE_DIR"
./scripts/init.sh
```

Open or attach a persistent terminal session:

```bash
tmux new-session -A -s practice
```

Run the environment and repository checks:

```bash
cd "$PRACTICE_DIR"
make doctor
make validate
make status
make ready
```

## Recommended first move

Use one high-capability model as the director. Give it the complete contents of `prompts/ORCHESTRATOR.md` while its working directory is this repository.

The director should create up to ten isolated task worktrees from the currently ready set:

```bash
python3 scripts/taskctl.py ready
python3 scripts/taskctl.py worktree F001 --agent worker-01
python3 scripts/taskctl.py prompt F001 --output .worktrees/F001/TASK_PROMPT.md
```

Run a lower-cost worker in each `.worktrees/<TASK_ID>` directory. Workers must commit their work. Integrate only after deterministic validation:

```bash
python3 scripts/taskctl.py integrate F001
python3 scripts/taskctl.py status
python3 scripts/taskctl.py ready
```

## Configure Buzz only after the content baseline exists

Copy the environment file and fill the relay URL. Keep the owner key local and never give it to a community agent.

```bash
cp -n .env.example .env
$EDITOR .env
python3 scripts/buzz_bootstrap.py --dry-run
```

After reviewing the dry run:

```bash
set -a
. ./.env
set +a
python3 scripts/buzz_bootstrap.py --apply
```

The bootstrapper creates or updates channels, canvases, and seed messages. It never deletes channels and does not create scheduled workflows.
