"""list 命令"""

import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime, date
from ..db import get_cursor, is_initialized
from dong import json_output, DongError

console = Console()


@json_output
def list_expires(
    category: str = typer.Option(None, "--category", "-c", help="按分类筛选"),
    status: str = typer.Option("active", "--status", "-s", help="按状态筛选"),
    limit: int = typer.Option(50, "--limit", "-l", help="限制数量"),
    all: bool = typer.Option(False, "--all", "-a", help="显示所有（包括已过期）"),
):
    """列出所有到期项"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    today = date.today()
    
    with get_cursor() as cur:
        if all:
            cur.execute("SELECT * FROM expires ORDER BY expire_date ASC")
        else:
            cur.execute(
                "SELECT * FROM expires WHERE status = ? ORDER BY expire_date ASC",
                (status,)
            )
        
        rows = cur.fetchall()
    
    if not rows:
        console.print("暂无到期项")
        return {"items": [], "total": 0}
    
    # 计算剩余天数并筛选
    items = []
    for row in rows:
        expire_id, name, cat, expire_date_str, cost, currency, repeat, remind_days, stat, note, created_at, updated_at = row
        
        if category and cat != category:
            continue
        
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        days_left = (expire_date - today).days
        
        items.append({
            "id": expire_id,
            "name": name,
            "category": cat,
            "expire_date": expire_date_str,
            "days_left": days_left,
            "cost": cost,
            "currency": currency,
            "repeat": repeat,
            "status": stat,
        })
    
    # 渲染表格
    table = Table(title="到期项列表")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("服务名称", style="green")
    table.add_column("分类", style="blue")
    table.add_column("到期日期", style="yellow")
    table.add_column("剩余天数", justify="right")
    table.add_column("费用", justify="right", style="magenta")
    table.add_column("状态")
    
    for item in items[:limit]:
        days = item["days_left"]
        if days < 0:
            days_str = f"已过期 {-days}天"
            status_style = "red"
        elif days == 0:
            days_str = "今天到期"
            status_style = "red"
        elif days <= 7:
            days_str = f"{days}天"
            status_style = "yellow"
        else:
            days_str = f"{days}天"
            status_style = "green"
        
        cost_str = f"¥{item['cost']}" if item['cost'] else "-"
        
        table.add_row(
            str(item["id"]),
            item["name"],
            item["category"] or "-",
            item["expire_date"],
            days_str,
            cost_str,
            item["status"],
        )
    
    console.print(table)
    
    return {"items": items, "total": len(items)}
