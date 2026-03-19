"""update 命令"""

import typer
from datetime import datetime
from ..db import get_cursor, is_initialized
from dong import json_output, DongError


@json_output
def update(
    expire_id: int = typer.Argument(..., help="到期项 ID"),
    name: str = typer.Option(None, "--name", "-n", help="服务名称"),
    category: str = typer.Option(None, "--category", "-c", help="分类"),
    expire_date: str = typer.Option(None, "--expire", "-e", help="到期日期"),
    cost: float = typer.Option(None, "--cost", help="费用"),
    repeat: str = typer.Option(None, "--repeat", "-r", help="重复周期"),
    note: str = typer.Option(None, "--note", help="备注"),
    status: str = typer.Option(None, "--status", "-s", help="状态"),
):
    """更新到期项"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    # 构建更新语句
    updates = []
    params = []
    
    if name:
        updates.append("name = ?")
        params.append(name)
    if category:
        updates.append("category = ?")
        params.append(category)
    if expire_date:
        try:
            datetime.strptime(expire_date, "%Y-%m-%d")
        except ValueError:
            raise DongError("INVALID_DATE", "日期格式错误，请使用 YYYY-MM-DD")
        updates.append("expire_date = ?")
        params.append(expire_date)
    if cost is not None:
        updates.append("cost = ?")
        params.append(cost)
    if repeat:
        updates.append("repeat = ?")
        params.append(repeat)
    if note:
        updates.append("note = ?")
        params.append(note)
    if status:
        updates.append("status = ?")
        params.append(status)
    
    if not updates:
        raise DongError("NO_UPDATES", "没有指定要更新的字段")
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(expire_id)
    
    with get_cursor() as cur:
        cur.execute(
            f"UPDATE expires SET {', '.join(updates)} WHERE id = ?",
            params
        )
        
        if cur.rowcount == 0:
            raise DongError("NOT_FOUND", f"未找到 ID={expire_id} 的到期项")
    
    return {"id": expire_id, "updated": True}
