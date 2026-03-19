# TOOLS.md - 工具箱

我的核心工具是 `dong-expire` CLI。

## 安装

```bash
pipx install dong-expire
```

## 命令列表

### 初始化

```bash
dong-expire init
```

### 添加到期项

```bash
dong-expire add "阿里云ECS" --expire 2027-04-15 --cost 1200 --category "云服务" --repeat yearly
dong-expire add "智谱AI套餐" --expire 2026-04-15 --cost 99 --category "AI服务" --repeat monthly
dong-expire add "gudong.site域名" --expire 2027-03-20 --cost 68 --category "域名"
```

### 列出所有

```bash
dong-expire list                    # 列出所有
dong-expire list --category 云服务  # 按分类筛选
dong-expire list --all              # 包括已过期
```

### 查看即将到期

```bash
dong-expire remind              # 默认30天内
dong-expire remind --days 7     # 7天内
```

### 续费

```bash
dong-expire renew 1 --auto              # 自动延长一个周期
dong-expire renew 1 --to 2028-04-15     # 指定新日期
dong-expire renew 1 --auto --cost 1300  # 指定续费金额
```

### 查看续费历史

```bash
dong-expire history 1
```

### 统计费用

```bash
dong-expire stats
```

### 搜索

```bash
dong-expire search "阿里云"
```

### 更新

```bash
dong-expire update 1 --name "新名称"
dong-expire update 1 --expire 2028-01-01
dong-expire update 1 --cost 1500
```

### 删除

```bash
dong-expire delete 1 --force
```

### 获取详情

```bash
dong-expire get 1
```

## JSON 输出

所有命令支持 JSON 输出，方便 AI 解析：

```bash
dong-expire add "xxx" --expire 2027-01-01
dong-expire list
dong-expire remind --days 30
dong-expire stats
```

## 数据库

数据存储在 `~/.dong/expire.db`

---

*⏰ 到期不慌，续费有方*
