"""到期咚 CLI 主入口"""

import typer
from rich.console import Console
from dong import json_output
from . import __version__

console = Console()

app = typer.Typer(
    name="dong-expire",
    help="到期咚 - 服务到期日管理 CLI",
    no_args_is_help=True,
    add_completion=False,
)

# 导入命令
from .commands import (
    init,
    add,
    ls,
    remind,
    renew,
    history,
    stats,
    search,
    update,
    delete,
    get,
)

# 注册命令
app.command()(init.init)
app.command()(add.add)
app.command(name="list")(ls.list_expires)
app.command()(remind.remind)
app.command()(renew.renew)
app.command()(history.history)
app.command()(stats.stats)
app.command()(search.search)
app.command()(update.update)
app.command()(delete.delete)
app.command()(get.get)


def version_callback(value: bool) -> None:
    """版本号回调函数"""
    if value:
        console.print(f"dong-expire {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="显示版本",
        callback=version_callback,
        is_eager=True,
    ),
):
    """到期咚 - 服务到期日管理 CLI"""
    pass


