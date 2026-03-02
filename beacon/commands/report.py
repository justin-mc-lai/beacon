"""Beacon report command"""
import typer

app = typer.Typer(name="report", help="Generate run reports")


@app.command()
def generate(
    run_id: str = typer.Argument("latest", help="Run ID"),
    human: bool = typer.Option(True, "--human/--machine", help="Report format"),
):
    """Generate run report"""
    typer.echo(f"Generating {human and 'human' or 'machine'} report for run: {run_id}")


if __name__ == "__main__":
    app()
