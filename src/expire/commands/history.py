"""history 命令 - 续费历史"""

import typer
from rich.console import Console
from rich.table import Table
from ..db import get_cursor, is_initialized
from dong import json_output, DongError

console = Console()


@json_output
def history(
    expire_id: int = typer.Argument(..., help="到期项 ID"),
):
    """查看续费历史"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    with get_cursor() as cur:
        # 获取服务名称
        cur.execute("SELECT name FROM expires WHERE id = ?", (expire_id,))
        row = cur.fetchone()
        
        if not row:
            raise DongError("NOT_FOUND", f"未找到 ID={expire_id} 的到期项")
        
        name = row[0]
        
        # 获取续费历史
        cur.execute("""
            SELECT id, old_date, new_date, cost, renewed_at
            FROM renewals
            WHERE expire_id = ?
            ORDER BY renewed_at DESC
        """, (expire_id,))
        
        rows = cur.fetchall()
    
    if not rows:
        console.print(f"[yellow]{name}[/yellow] 暂无续费历史")
        return {"name": name, "renewals": [], "total": 0}
    
    # 渲染表格
    table = Table(title=f"📝 {name} 续费历史")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("原到期日", style="yellow")
    table.add_column("新到期日", style="green")
    table.add_column("费用", justify="right", style="magenta")
    table.add_column("续费时间", style="blue")
    
    renewals = []
    for row in rows:
        renewal_id, old_date, new_date, cost, renewed_at = row
        cost_str = f"¥{cost}" if cost else "-"
        table.add_row(
            str(renewal_id),
            old_date,
            new_date,
            cost_str,
            renewed_at,
        )
        renewals.append({
            "id": renewal_id,
            "old_date": old_date,
            "new_date": new_date,
            "cost": cost,
            "renewed_at": renewed_at,
        })
    
    console.print(table)
    
    return {"name": name, "renewals": renewals, "total": len(renewals)}
