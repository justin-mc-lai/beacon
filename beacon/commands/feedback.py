"""Beacon feedback command"""
import typer

app = typer.Typer(name="feedback", help="Feedback operations")


@app.command()
def sync(
    run_id: str = typer.Argument("latest", help="Run ID"),
):
    """Sync test feedback to requirements"""
    typer.echo(f"Syncing feedback for run: {run_id}")


if __name__ == "__main__":
    app()
