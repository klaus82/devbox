import typer

from devbox.devcontainer import start, stop_dev_container, container_cli


app = typer.Typer()
app.command("start")(start)
app.command("stop")(stop_dev_container)
app.command("it")(container_cli)
