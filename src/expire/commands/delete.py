"""delete 命令"""

import typer
from ..db import get_cursor, is_initialized
from dong import json_output, DongError


@json_output
def delete(
    expire_id: int = typer.Argument(..., help="到期项 ID"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，不确认"),
):
    """删除到期项"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    if not force:
        if not typer.confirm(f"确定要删除 ID={expire_id} 的到期项吗？"):
            return {"cancelled": True}
    
    with get_cursor() as cur:
        # 先检查是否存在
        cur.execute("SELECT name FROM expires WHERE id = ?", (expire_id,))
        row = cur.fetchone()
        
        if not row:
            raise DongError("NOT_FOUND", f"未找到 ID={expire_id} 的到期项")
        
        name = row[0]
        
        # 删除续费历史
        cur.execute("DELETE FROM renewals WHERE expire_id = ?", (expire_id,))
        
        # 删除到期项
        cur.execute("DELETE FROM expires WHERE id = ?", (expire_id,))
    
    return {"id": expire_id, "name": name, "deleted": True}
