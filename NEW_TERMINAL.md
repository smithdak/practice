# New Terminal Pickup

These commands assume the downloaded ZIP is in the Windows Downloads folder and the working copy should live in Dakota's WSL projects directory.

```bash
mkdir -p /home/dakota/projects
cd /home/dakota/projects
rm -rf practice-swarm-kit practice
unzip /mnt/c/Users/dakot/Downloads/practice-swarm-kit.zip
mv practice-swarm-kit practice
cd practice
./scripts/init.sh
```

Open or attach the persistent terminal session:

```bash
tmux new-session -A -s practice
```

Run the environment and repository checks:

```bash
cd /home/dakota/projects/practice
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
