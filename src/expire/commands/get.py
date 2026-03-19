"""get 命令"""

import typer
from rich.console import Console
from datetime import datetime, date
from ..db import get_cursor, is_initialized
from dong import json_output, DongError

console = Console()


@json_output
def get(
    expire_id: int = typer.Argument(..., help="到期项 ID"),
):
    """获取到期项详情"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    today = date.today()
    
    with get_cursor() as cur:
        cur.execute("SELECT * FROM expires WHERE id = ?", (expire_id,))
        row = cur.fetchone()
        
        if not row:
            raise DongError("NOT_FOUND", f"未找到 ID={expire_id} 的到期项")
        
        expire_id, name, category, expire_date_str, cost, currency, repeat, remind_days, status, note, created_at, updated_at = row
        
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        days_left = (expire_date - today).days
    
    # 渲染详情
    console.print(f"\n[bold green]{name}[/bold green]")
    console.print(f"  ID: {expire_id}")
    console.print(f"  分类: {category or '-'}")
    console.print(f"  到期日期: [yellow]{expire_date_str}[/yellow]")
    
    if days_left < 0:
        console.print(f"  状态: [red]已过期 {-days_left} 天[/red]")
    elif days_left == 0:
        console.print(f"  状态: [red]今天到期[/red]")
    elif days_left <= 7:
        console.print(f"  状态: [yellow]还有 {days_left} 天到期[/yellow]")
    else:
        console.print(f"  状态: [green]还有 {days_left} 天到期[/green]")
    
    console.print(f"  费用: ¥{cost}" if cost else "  费用: -")
    console.print(f"  重复周期: {repeat or '-'}")
    console.print(f"  提醒天数: {remind_days}")
    console.print(f"  状态: {status}")
    console.print(f"  备注: {note or '-'}")
    console.print(f"  创建时间: {created_at}")
    console.print(f"  更新时间: {updated_at}")
    
    return {
        "id": expire_id,
        "name": name,
        "category": category,
        "expire_date": expire_date_str,
        "days_left": days_left,
        "cost": cost,
        "currency": currency,
        "repeat": repeat,
        "remind_days": remind_days,
        "status": status,
        "note": note,
        "created_at": created_at,
        "updated_at": updated_at,
    }
