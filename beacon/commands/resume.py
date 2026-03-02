"""Beacon resume command"""
import typer

app = typer.Typer(name="resume", help="Resume/inspect run state")


@app.command()
def restore(
    run_id: str = typer.Argument(..., help="Run ID to resume"),
):
    """Resume a previous run"""
    typer.echo(f"Resuming run: {run_id}")


if __name__ == "__main__":
    app()
