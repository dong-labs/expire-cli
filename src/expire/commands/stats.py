"""stats 命令 - 统计"""

import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime
from ..db import get_cursor, is_initialized
from dong import json_output, DongError

console = Console()


@json_output
def stats(
    year: int = typer.Option(None, "--year", "-y", help="统计年份"),
):
    """统计费用"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    if not year:
        year = datetime.now().year
    
    with get_cursor() as cur:
        # 按分类统计
        cur.execute("""
            SELECT category, SUM(cost) as total_cost, COUNT(*) as count
            FROM expires
            WHERE cost IS NOT NULL AND status = 'active'
            GROUP BY category
            ORDER BY total_cost DESC
        """)
        
        category_stats = cur.fetchall()
        
        # 总计
        cur.execute("""
            SELECT SUM(cost) FROM expires WHERE cost IS NOT NULL AND status = 'active'
        """)
        total = cur.fetchone()[0] or 0
    
    if not category_stats:
        console.print("暂无费用数据")
        return {"categories": [], "total": 0}
    
    # 渲染表格
    table = Table(title=f"💰 费用统计")
    table.add_column("分类", style="blue")
    table.add_column("数量", justify="right", style="cyan")
    table.add_column("费用", justify="right", style="magenta")
    table.add_column("占比", justify="right", style="green")
    
    categories = []
    for row in category_stats:
        category, cost, count = row
        category = category or "未分类"
        percentage = (cost / total * 100) if total > 0 else 0
        table.add_row(
            category,
            str(count),
            f"¥{cost:.2f}",
            f"{percentage:.1f}%",
        )
        categories.append({
            "category": category,
            "count": count,
            "cost": cost,
            "percentage": percentage,
        })
    
    table.add_row("总计", "-", f"¥{total:.2f}", "100%")
    console.print(table)
    
    return {"categories": categories, "total": total}
