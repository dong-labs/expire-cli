"""add 命令"""

import typer
from datetime import datetime
from ..db import get_cursor, is_initialized
from dong import json_output, DongError


@json_output
def add(
    name: str = typer.Argument(..., help="服务名称"),
    expire_date: str = typer.Option(..., "--expire", "-e", help="到期日期 (YYYY-MM-DD)"),
    category: str = typer.Option(None, "--category", "-c", help="分类"),
    cost: float = typer.Option(None, "--cost", help="费用"),
    currency: str = typer.Option("CNY", "--currency", help="币种"),
    repeat: str = typer.Option(None, "--repeat", "-r", help="重复周期 (monthly/yearly)"),
    remind_days: str = typer.Option("30,7,1", "--remind", help="提醒天数"),
    note: str = typer.Option(None, "--note", "-n", help="备注"),
):
    """添加到期项"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    # 验证日期格式
    try:
        datetime.strptime(expire_date, "%Y-%m-%d")
    except ValueError:
        raise DongError("INVALID_DATE", "日期格式错误，请使用 YYYY-MM-DD")
    
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO expires (name, category, expire_date, cost, currency, repeat, remind_days, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, expire_date, cost, currency, repeat, remind_days, note))
        
        expire_id = cur.lastrowid
    
    return {
        "id": expire_id,
        "name": name,
        "expire_date": expire_date,
        "category": category,
        "cost": cost,
        "currency": currency,
    }
