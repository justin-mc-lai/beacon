"""Loom CLI surface — thin dual-install entry; does not overwrite beacon."""

from __future__ import annotations

import typer

from beacon.utils.loom_brand import naming_contract, public_entry_contract

app = typer.Typer(
    name="loom",
    help="Loom v2 evolution track (dual-install with Beacon). Not a default beacon replacement.",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        c = naming_contract()
        typer.echo(f"Loom {c['cli']} — dual-install with {c['beacon_cli']}; state={c['state_root']}")
        typer.echo("Public entry: loom goal run | $loom-goal")
        typer.echo("Does not replace beacon (UD-LOOM-005).")


@app.command("version")
def version() -> None:
    from loom import __version__

    typer.echo(__version__)


@app.command("brand")
def brand(json_output: bool = typer.Option(False, "--json")) -> None:
    import json

    payload = {"naming": naming_contract(), "entry": public_entry_contract()}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"pip={payload['naming']['pip']} cli={payload['naming']['cli']} skill={payload['naming']['public_skill']}")


# Mount goal facade under loom goal — reuses beacon goal runtime with brand labels
goal_app = typer.Typer(help="Loom Product Goal facade (same spine as beacon goal; isolated brand).")
app.add_typer(goal_app, name="goal")


@goal_app.command("run")
def goal_run(
    utterance: str = typer.Argument(...),
    project: str = typer.Option(".", "--project", "-p"),
    version: str = typer.Option("v2.0.0", "--version", "-v"),
    longrun: bool = typer.Option(False, "--longrun"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Unique public Loom entry equivalent to $loom-goal."""
    import json
    from pathlib import Path

    from beacon.utils.product_goal_runtime import run_goal_facade

    root = Path(project).expanduser().resolve()
    # Loom runs still use .beacon state for engine; brand is surface-only in Phase-1
    payload = run_goal_facade(
        root,
        utterance=utterance,
        version=version,
        longrun=longrun,
        driver_start=longrun,
        driver_run_loop=False,
    )
    payload["brand"] = "loom"
    payload["public_entry"] = "loom-goal"
    payload["state_note"] = "Phase-1 engine state under .beacon; brand surface is loom"
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    else:
        typer.echo(f"loom goal run_id={payload.get('run_id')} stage={payload.get('current_stage')}")


@goal_app.command("entry-contract")
def entry_contract(json_output: bool = typer.Option(True, "--json/--no-json")) -> None:
    import json

    payload = public_entry_contract()
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(payload["public_primary"])


def main() -> None:
    app()


if __name__ == "__main__":
    main()
