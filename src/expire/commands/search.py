"""search 命令"""

import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime, date
from ..db import get_cursor, is_initialized
from dong import json_output, DongError

console = Console()


@json_output
def search(
    query: str = typer.Argument(..., help="搜索关键词"),
    limit: int = typer.Option(20, "--limit", "-l", help="限制数量"),
):
    """搜索到期项"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    today = date.today()
    search_pattern = f"%{query}%"
    
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM expires
            WHERE name LIKE ? OR category LIKE ? OR note LIKE ?
            ORDER BY expire_date ASC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))
        
        rows = cur.fetchall()
    
    if not rows:
        console.print(f"未找到包含 '[yellow]{query}[/yellow]' 的到期项")
        return {"query": query, "items": [], "total": 0}
    
    # 渲染表格
    table = Table(title=f"搜索结果：{query}")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("服务名称", style="green")
    table.add_column("分类", style="blue")
    table.add_column("到期日期", style="yellow")
    table.add_column("剩余天数", justify="right")
    table.add_column("状态")
    
    items = []
    for row in rows:
        expire_id, name, category, expire_date_str, cost, currency, repeat, remind_days, status, note, created_at, updated_at = row
        
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d").date()
        days_left = (expire_date - today).days
        
        if days_left < 0:
            days_str = f"已过期"
        elif days_left == 0:
            days_str = "今天"
        else:
            days_str = f"{days_left}天"
        
        table.add_row(
            str(expire_id),
            name,
            category or "-",
            expire_date_str,
            days_str,
            status,
        )
        
        items.append({
            "id": expire_id,
            "name": name,
            "category": category,
            "expire_date": expire_date_str,
            "days_left": days_left,
            "status": status,
        })
    
    console.print(table)
    
    return {"query": query, "items": items, "total": len(items)}
