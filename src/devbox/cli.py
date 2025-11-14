import typer

from devbox.devcontainer import start_dev_container, stop_dev_container, container_cli


app = typer.Typer()
app.command("start")(start_dev_container)
app.command("stop")(stop_dev_container)
app.command("it")(container_cli)