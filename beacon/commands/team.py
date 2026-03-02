"""Beacon team command - Team collaboration with state machine"""
import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
from enum import Enum

app = typer.Typer(name="team", help="Team collaboration management")

# Team state machine states
class TeamState(str, Enum):
    TEAM_PLAN = "team-plan"
    TEAM_PRD = "team-prd"
    TEAM_EXEC = "team-exec"
    TEAM_VERIFY = "team-verify"
    TEAM_FIX = "team-fix"
    TERMINAL = "terminal"


# Terminal statuses
class TerminalStatus(str, Enum):
    PASS = "Pass"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"


# Runtime modes
class RuntimeMode(str, Enum):
    FILE = "file"
    TMUX = "tmux"
    AUTO = "auto"


# Team configuration
TEAM_STATE_FILE = "team-state.json"
MAX_FIX_LOOPS = 3


def get_team_dir(project_root: Path, team_name: str) -> Path:
    """Get team directory"""
    return project_root / ".beacon" / "team" / team_name


def get_team_state_file(project_root: Path, team_name: str) -> Path:
    """Get team state file path"""
    return get_team_dir(project_root, team_name) / "manifest.json"


def load_team_state(project_root: Path, team_name: str) -> dict:
    """Load team state"""
    state_file = get_team_state_file(project_root, team_name)
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {
        "active": False,
        "team_name": team_name,
        "task": None,
        "runtime": "file",
        "state": "team-plan",
        "terminal_status": None,
        "started_at": None,
        "workers": [],
        "tasks": [],
        "review_gates": {
            "spec": {"status": None, "reviewer": None},
            "quality": {"status": None, "reviewer": None},
        },
        "fix_loops": 0,
    }


def save_team_state(project_root: Path, team_name: str, state: dict):
    """Save team state"""
    state_file = get_team_state_file(project_root, team_name)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def generate_handoff_report(project_root: Path, team_name: str, from_state: str, to_state: str, state: dict):
    """Generate handoff report"""
    handoff_dir = project_root / ".beacon" / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    handoff_file = handoff_dir / f"{team_name}-{from_state}-to-{to_state}.md"
    content = f"""# Team Handoff Report

**Team**: {team_name}
**From**: {from_state}
**To**: {to_state}
**Timestamp**: {datetime.now().isoformat()}

## Task
{state.get('task', 'N/A')}

## Status Summary
- Current State: {state.get('state')}
- Runtime: {state.get('runtime')}
- Workers: {len(state.get('workers', []))}
- Fix Loops: {state.get('fix_loops', 0)}

## Review Gates
- Spec: {state.get('review_gates', {}).get('spec', {}).get('status', 'N/A')}
- Quality: {state.get('review_gates', {}).get('quality', {}).get('status', 'N/A')}

## Workers
"""
    for worker in state.get("workers", []):
        content += f"- {worker.get('id')}: {worker.get('status', 'unknown')}\n"

    handoff_file.write_text(content)
    return handoff_file


def advance_state(project_root: Path, team_name: str, state: dict, new_state: str) -> dict:
    """Advance team state"""
    old_state = state.get("state", "team-plan")

    # Check state transition validity
    valid_transitions = {
        "team-plan": "team-prd",
        "team-prd": "team-exec",
        "team-exec": "team-verify",
        "team-verify": ["team-fix", "terminal"],
        "team-fix": ["team-verify", "terminal"],
    }

    allowed = valid_transitions.get(old_state, [])
    if isinstance(allowed, list):
        if new_state not in allowed:
            typer.echo(f"Invalid state transition: {old_state} -> {new_state}")
            return state
    elif new_state != allowed:
        typer.echo(f"Invalid state transition: {old_state} -> {new_state}")
        return state

    state["state"] = new_state

    # Generate handoff report
    if new_state != TeamState.TERMINAL:
        generate_handoff_report(project_root, team_name, old_state, new_state, state)

    # Handle terminal state
    if new_state == TeamState.TERMINAL:
        state["ended_at"] = datetime.now().isoformat()
        typer.echo(f"Team {team_name} reached terminal state")
        typer.echo(f"Terminal Status: {state.get('terminal_status', 'N/A')}")

    save_team_state(project_root, team_name, state)
    return state


@app.command()
def start(
    task: str = typer.Argument(..., help="Team task description"),
    runtime: str = typer.Option("file", "--runtime", "-r", help="Runtime mode: file/tmux/auto"),
    members: int = typer.Option(3, "--members", "-m", help="Number of team members"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Start a team task"""
    project_root = Path(project) if project else Path.cwd()
    team_name = f"team-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Validate runtime mode
    try:
        RuntimeMode(runtime)
    except ValueError:
        typer.echo(f"Error: Invalid runtime '{runtime}'. Use file/tmux/auto")
        raise typer.Exit(1)

    state = load_team_state(project_root, team_name)

    if state["active"]:
        typer.echo("Team is already active")
        typer.echo(f"  Team: {state.get('team_name')}")
        typer.echo(f"  Task: {state.get('task', 'unknown')}")
        raise typer.Exit(1)

    # Initialize state
    state["active"] = True
    state["team_name"] = team_name
    state["task"] = task
    state["runtime"] = runtime
    state["state"] = TeamState.TEAM_PLAN.value
    state["started_at"] = datetime.now().isoformat()
    state["fix_loops"] = 0

    # Initialize workers
    state["workers"] = [
        {
            "id": f"worker-{i+1:03d}",
            "role": ["planner", "executor", "verifier"][i % 3],
            "status": "idle",
            "started_at": None,
        }
        for i in range(members)
    ]

    # Initialize tasks
    state["tasks"] = [
        {"id": i + 1, "description": f"Task {i + 1}", "status": "pending", "worker": None}
        for i in range(members)
    ]

    save_team_state(project_root, team_name, state)

    typer.echo(f"Team started: {team_name}")
    typer.echo(f"  Task: {task}")
    typer.echo(f"  Runtime: {runtime}")
    typer.echo(f"  Members: {members}")
    typer.echo(f"  State: {state['state']}")
    typer.echo(f"  Time: {state['started_at']}")


@app.command()
def status(
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Show team status"""
    project_root = Path(project) if project else Path.cwd()

    # Find active team if not specified
    if not team:
        team_dir = project_root / ".beacon" / "team"
        if team_dir.exists():
            for d in team_dir.iterdir():
                if d.is_dir():
                    state = load_team_state(project_root, d.name)
                    if state.get("active"):
                        team = d.name
                        break

    if not team:
        typer.echo("No active team found")
        return

    state = load_team_state(project_root, team)

    typer.echo(f"Team: {team}")
    typer.echo(f"  Task: {state.get('task', 'N/A')}")
    typer.echo(f"  State: {state.get('state', 'N/A')}")
    typer.echo(f"  Runtime: {state.get('runtime', 'N/A')}")
    typer.echo(f"  Members: {len(state.get('workers', []))}")

    if state.get("started_at"):
        typer.echo(f"  Started: {state.get('started_at')}")

    if state.get("ended_at"):
        typer.echo(f"  Ended: {state.get('ended_at')}")

    # Show review gates
    review_gates = state.get("review_gates", {})
    typer.echo(f"\nReview Gates:")
    typer.echo(f"  Spec: {review_gates.get('spec', {}).get('status', 'N/A')}")
    typer.echo(f"  Quality: {review_gates.get('quality', {}).get('status', 'N/A')}")

    # Show workers
    workers = state.get("workers", [])
    if workers:
        typer.echo(f"\nWorkers ({len(workers)}):")
        for w in workers:
            typer.echo(f"  - {w.get('id')}: {w.get('role')} ({w.get('status')})")

    # Show fix loops
    fix_loops = state.get("fix_loops", 0)
    if fix_loops > 0:
        typer.echo(f"\nFix Loops: {fix_loops}/{MAX_FIX_LOOPS}")


@app.command()
def advance(
    to_state: str = typer.Argument(..., help="Target state: team-prd/team-exec/team-verify/team-fix/terminal"),
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team name"),
    terminal_status: Optional[str] = typer.Option(None, "--terminal-status", help="Terminal status: Pass/Blocked/Cancelled"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Advance team to next state"""
    project_root = Path(project) if project else Path.cwd()

    # Find active team if not specified
    if not team:
        team_dir = project_root / ".beacon" / "team"
        if team_dir.exists():
            for d in team_dir.iterdir():
                if d.is_dir():
                    state = load_team_state(project_root, d.name)
                    if state.get("active"):
                        team = d.name
                        break

    if not team:
        typer.echo("No active team found")
        raise typer.Exit(1)

    state = load_team_state(project_root, team)

    if not state.get("active"):
        typer.echo(f"Team {team} is not active")
        raise typer.Exit(1)

    # Validate target state
    try:
        new_state = TeamState(to_state)
    except ValueError:
        typer.echo(f"Invalid state: {to_state}")
        typer.echo(f"Valid states: {[s.value for s in TeamState]}")
        raise typer.Exit(1)

    # Handle terminal status
    if new_state == TeamState.TERMINAL:
        if not terminal_status:
            typer.echo("Error: --terminal-status required for terminal state")
            raise typer.Exit(1)
        try:
            state["terminal_status"] = TerminalStatus(terminal_status).value
        except ValueError:
            typer.echo(f"Invalid terminal status: {terminal_status}")
            typer.echo(f"Valid statuses: {[s.value for s in TerminalStatus]}")
            raise typer.Exit(1)

    # Check fix loops limit
    if to_state == "team-fix":
        state["fix_loops"] = state.get("fix_loops", 0) + 1
        if state["fix_loops"] >= MAX_FIX_LOOPS:
            state["terminal_status"] = TerminalStatus.BLOCKED.value
            state["state"] = TeamState.TERMINAL.value
            state["blocked_reason"] = "max_fix_loops_exceeded"
            save_team_state(project_root, team, state)
            typer.echo(f"Max fix loops ({MAX_FIX_LOOPS}) exceeded")
            typer.echo(f"Team {team} is now BLOCKED")
            return

    # Advance state
    state = advance_state(project_root, team, state, new_state.value)

    typer.echo(f"Team advanced to: {new_state.value}")


@app.command()
def review(
    gate_type: str = typer.Argument(..., help="Gate type: spec/quality"),
    status: str = typer.Argument(..., help="Status: pass/fail"),
    reviewer: str = typer.Option("pm", "--reviewer", "-r", help="Reviewer type: pm/qa"),
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Submit review gate (spec or quality)"""
    project_root = Path(project) if project else Path.cwd()

    # Find active team if not specified
    if not team:
        team_dir = project_root / ".beacon" / "team"
        if team_dir.exists():
            for d in team_dir.iterdir():
                if d.is_dir():
                    state = load_team_state(project_root, d.name)
                    if state.get("active"):
                        team = d.name
                        break

    if not team:
        typer.echo("No active team found")
        raise typer.Exit(1)

    state = load_team_state(project_root, team)

    # Validate gate type
    if gate_type not in ["spec", "quality"]:
        typer.echo(f"Invalid gate type: {gate_type}. Use spec or quality")
        raise typer.Exit(1)

    # Validate status
    if status not in ["pass", "fail"]:
        typer.echo(f"Invalid status: {status}. Use pass or fail")
        raise typer.Exit(1)

    # Spec must pass before quality
    if gate_type == "quality" and state.get("review_gates", {}).get("spec", {}).get("status") != "pass":
        typer.echo("Error: Spec gate must pass before quality gate can be submitted")
        raise typer.Exit(1)

    # Update gate
    if "review_gates" not in state:
        state["review_gates"] = {}
    state["review_gates"][gate_type] = {
        "status": status,
        "reviewer": reviewer,
        "timestamp": datetime.now().isoformat(),
    }

    save_team_state(project_root, team, state)

    typer.echo(f"Review gate updated: {gate_type} = {status} (reviewer: {reviewer})")


@app.command()
def evaluate(
    critical_open: int = typer.Argument(0, help="Number of critical open issues"),
    high_open: int = typer.Argument(0, help="Number of high open issues"),
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Evaluate team readiness (gate evaluation)"""
    project_root = Path(project) if project else Path.cwd()

    # Find active team if not specified
    if not team:
        team_dir = project_root / ".beacon" / "team"
        if team_dir.exists():
            for d in team_dir.iterdir():
                if d.is_dir():
                    state = load_team_state(project_root, d.name)
                    if state.get("active"):
                        team = d.name
                        break

    if not team:
        typer.echo("No active team found")
        raise typer.Exit(1)

    state = load_team_state(project_root, team)

    # Check critical/high issues
    if critical_open > 0 or high_open > 0:
        typer.echo(f"Evaluation: BLOCKED")
        typer.echo(f"  Critical open: {critical_open}")
        typer.echo(f"  High open: {high_open}")

        # Auto-advance to fix if in verify state
        if state.get("state") == TeamState.TEAM_VERIFY.value:
            state = advance_state(project_root, team, state, TeamState.TEAM_FIX.value)
            typer.echo(f"Team advanced to: {TeamState.TEAM_FIX.value}")
    else:
        typer.echo(f"Evaluation: PASS")
        typer.echo(f"  All critical/high issues resolved")

        # Auto-advance to terminal if in verify state
        if state.get("state") == TeamState.TEAM_VERIFY.value:
            state["terminal_status"] = TerminalStatus.PASS.value
            state = advance_state(project_root, team, state, TeamState.TERMINAL.value)


@app.command()
def stop(
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team name"),
    terminal_status: str = typer.Option("Cancelled", "--terminal-status", help="Terminal status: Pass/Blocked/Cancelled"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Stop the team task"""
    project_root = Path(project) if project else Path.cwd()

    # Find active team if not specified
    if not team:
        team_dir = project_root / ".beacon" / "team"
        if team_dir.exists():
            for d in team_dir.iterdir():
                if d.is_dir():
                    state = load_team_state(project_root, d.name)
                    if state.get("active"):
                        team = d.name
                        break

    if not team:
        typer.echo("No active team found")
        return

    state = load_team_state(project_root, team)

    if not state.get("active"):
        typer.echo(f"Team {team} is not active")
        return

    # Validate terminal status
    try:
        status = TerminalStatus(terminal_status)
    except ValueError:
        typer.echo(f"Invalid terminal status: {terminal_status}")
        raise typer.Exit(1)

    state["active"] = False
    state["state"] = TeamState.TERMINAL.value
    state["terminal_status"] = status.value
    state["ended_at"] = datetime.now().isoformat()

    save_team_state(project_root, team, state)

    typer.echo(f"Team {team} stopped")
    typer.echo(f"  Terminal Status: {status.value}")


@app.command()
def report(
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team name"),
    format: str = typer.Option("text", "--format", "-f", help="Format: text/json/both"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Generate team report"""
    project_root = Path(project) if project else Path.cwd()

    # Find active team if not specified
    if not team:
        team_dir = project_root / ".beacon" / "team"
        if team_dir.exists():
            for d in team_dir.iterdir():
                if d.is_dir():
                    state = load_team_state(project_root, d.name)
                    if state.get("active"):
                        team = d.name
                        break

    if not team:
        typer.echo("No active team found")
        return

    state = load_team_state(project_root, team)

    report_data = {
        "team_name": team,
        "task": state.get("task"),
        "state": state.get("state"),
        "runtime": state.get("runtime"),
        "terminal_status": state.get("terminal_status"),
        "started_at": state.get("started_at"),
        "ended_at": state.get("ended_at"),
        "workers": state.get("workers", []),
        "review_gates": state.get("review_gates", {}),
        "fix_loops": state.get("fix_loops", 0),
    }

    if format in ["json", "both"]:
        typer.echo(json.dumps(report_data, indent=2, ensure_ascii=False))

    if format in ["text", "both"]:
        if format == "both":
            typer.echo("")
        typer.echo(f"Team Report: {team}")
        typer.echo(f"  Task: {report_data['task']}")
        typer.echo(f"  State: {report_data['state']}")
        typer.echo(f"  Runtime: {report_data['runtime']}")
        typer.echo(f"  Terminal: {report_data['terminal_status']}")
        typer.echo(f"  Fix Loops: {report_data['fix_loops']}")


@app.command("list")
def list_teams(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all teams"""
    project_root = Path(project) if project else Path.cwd()
    team_dir = project_root / ".beacon" / "team"

    if not team_dir.exists():
        typer.echo("No teams found")
        return

    teams = []
    for d in team_dir.iterdir():
        if d.is_dir():
            state = load_team_state(project_root, d.name)
            teams.append({
                "name": d.name,
                "active": state.get("active", False),
                "state": state.get("state"),
                "task": state.get("task"),
            })

    if not teams:
        typer.echo("No teams found")
        return

    typer.echo(f"Teams ({len(teams)}):")
    for t in teams:
        status_marker = "active" if t["active"] else "inactive"
        typer.echo(f"  - {t['name']} [{status_marker}]")
        typer.echo(f"    State: {t.get('state', 'N/A')}")
        typer.echo(f"    Task: {t.get('task', 'N/A')}")


if __name__ == "__main__":
    app()
