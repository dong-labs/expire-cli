"""renew 命令 - 续费"""

import typer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ..db import get_cursor, is_initialized
from dong import json_output, DongError


@json_output
def renew(
    expire_id: int = typer.Argument(..., help="到期项 ID"),
    to_date: str = typer.Option(None, "--to", "-t", help="新到期日期"),
    auto: bool = typer.Option(False, "--auto", "-a", help="自动延长一个周期"),
    cost: float = typer.Option(None, "--cost", help="续费金额"),
):
    """续费到期项"""
    if not is_initialized():
        raise DongError("NOT_INITIALIZED", "请先运行 dong-expire init")
    
    if not to_date and not auto:
        raise DongError("MISSING_DATE", "请指定 --to 日期或使用 --auto 自动延长")
    
    with get_cursor() as cur:
        # 获取原记录
        cur.execute("SELECT * FROM expires WHERE id = ?", (expire_id,))
        row = cur.fetchone()
        
        if not row:
            raise DongError("NOT_FOUND", f"未找到 ID={expire_id} 的到期项")
        
        old_date = row[3]  # expire_date
        repeat = row[6]    # repeat
        
        # 计算新日期
        if auto:
            old_dt = datetime.strptime(old_date, "%Y-%m-%d")
            if repeat == "monthly":
                new_dt = old_dt + relativedelta(months=1)
            elif repeat == "yearly":
                new_dt = old_dt + relativedelta(years=1)
            else:
                raise DongError("NO_REPEAT", "该服务未设置重复周期，请使用 --to 指定日期")
            new_date = new_dt.strftime("%Y-%m-%d")
        else:
            new_date = to_date
            # 验证日期格式
            try:
                datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                raise DongError("INVALID_DATE", "日期格式错误，请使用 YYYY-MM-DD")
        
        # 更新到期日期
        cur.execute(
            "UPDATE expires SET expire_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_date, expire_id)
        )
        
        # 记录续费历史
        cur.execute("""
            INSERT INTO renewals (expire_id, old_date, new_date, cost)
            VALUES (?, ?, ?, ?)
        """, (expire_id, old_date, new_date, cost))
        
        renewal_id = cur.lastrowid
    
    return {
        "id": expire_id,
        "old_date": old_date,
        "new_date": new_date,
        "renewal_id": renewal_id,
        "cost": cost,
    }
