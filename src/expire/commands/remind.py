"""remind 命令 - 查看即将到期"""

import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime, date
from ..db import get_cursor, is_initialized
from dong import json_output, DongError

console = Console()


@json_output
def remind(
    days: int = typer.Option(30, "--days", "-d", help="提前多少天"),
):
    """查看即将到期的服务"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    today = date.today()
    
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM expires WHERE status = 'active' ORDER BY expire_date ASC"
        )
        rows = cur.fetchall()
    
    # 筛选即将到期的
    expiring = []
    for row in rows:
        expire_id, name, category, expire_date_str, cost, currency, repeat, remind_days, status, note, created_at, updated_at = row
        
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        days_left = (expire_date - today).days
        
        if 0 <= days_left <= days:
            expiring.append({
                "id": expire_id,
                "name": name,
                "category": category,
                "expire_date": expire_date_str,
                "days_left": days_left,
                "cost": cost,
                "currency": currency,
            })
    
    if not expiring:
        console.print(f"[green]✅ 未来 {days} 天内无到期服务[/green]")
        return {"items": [], "total": 0}
    
    # 渲染表格
    table = Table(title=f"⚠️ 即将到期（{days}天内）")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("服务名称", style="yellow")
    table.add_column("分类", style="blue")
    table.add_column("到期日期", style="red")
    table.add_column("剩余天数", justify="right", style="red")
    table.add_column("费用", justify="right", style="magenta")
    
    for item in expiring:
        cost_str = f"¥{item['cost']}" if item['cost'] else "-"
        table.add_row(
            str(item["id"]),
            item["name"],
            item["category"] or "-",
            item["expire_date"],
            f"{item['days_left']}天",
            cost_str,
        )
    
    console.print(table)
    
    return {"items": expiring, "total": len(expiring)}
