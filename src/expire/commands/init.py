"""init 命令"""

import typer
from ..db import init_database
from dong import json_output


@json_output
def init():
    """初始化数据库"""
    return init_database()
