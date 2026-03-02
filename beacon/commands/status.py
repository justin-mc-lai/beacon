"""Beacon status command"""
import typer

app = typer.Typer(name="status", help="Show workflow status")


@app.command()
def show_status(
    board: bool = typer.Option(False, "--board", "-b", help="Render human board"),
):
    """Show current workflow status"""
    typer.echo("Beacon Status")
    typer.echo("=" * 40)
    typer.echo("No active workflow")


if __name__ == "__main__":
    app()
