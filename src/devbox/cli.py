import typer

from devbox.devcontainer import start_dev_container


app = typer.Typer()
app.command()(start_dev_container)