"""Beacon debug command"""
import typer

app = typer.Typer(name="debug", help="Debug helpers")


@app.command()
def watch(
    run_id: str = typer.Argument("", help="Run ID"),
    tail: int = typer.Option(20, "--tail", "-n", help="Tail lines"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow mode"),
):
    """Watch run events"""
    typer.echo(f"Debug watch for run: {run_id or 'latest'}")


if __name__ == "__main__":
    app()
