# 文档要点总结

## ?? 架构洞察

- **双语言设计**：Go 调度器 + Python 爬虫（而非纯 Python cron），便于 Windows 用户无需额外配置就能运行后台服务
- **数据流向**：config.json → Go 每日 3 次随机调度 → Python Selenium 爬取 → JSON + Excel 输出

## ? 关键模式

- **城市代码系统**：使用 IATA 三字母代码 + `CITY_LABELS` 字典映射中文名称
- **反爬虫策略**：多层 CSS 选择器回退、UA 伪装、禁用自动化标识
- **直飞过滤逻辑**：三层验证（航班号数量、关键词、时间对数量）
- **Excel 设计**：每个航班单独 sheet，追踪历史价格变化

## ?? 工作流程

- 手动运行命令（虚拟环境路径）
- 构建 Go 调度器的具体步骤
- 调试网页抓取问题的 4 步检查流程

## ? 特定约定

- 统一使用 `log_print()` 带时间戳的日志格式
- Unicode 符号约定（?/?/?/?）
- 价格范围过滤（1000-50000 元）避免误识别

## 项目核心组件

### Python 爬虫 (`query.py`)
- Selenium + ChromeDriver 自动化
- 多层反爬虫保护机制
- 直飞航班智能过滤
- 双格式输出（JSON + Excel）

### Go 调度器 (`AirTicket.go`)
- 后台服务，每日 3 个时间窗口随机执行
- 自动查找 Python 虚拟环境
- 日志记录到 `logs/scheduler.log`

### 配置文件 (`config.json`)
- 定义要监控的航班查询任务
- 支持多条路线和日期

## 快速命令参考

```bash
# 手动查询航班
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25

# 调试模式（显示浏览器）
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25 --no-headless --debug

# 编译调度器
go build -o AirTicket.exe AirTicket.go

# 启动后台服务
.\start.bat

# 停止服务
.\stop.bat
```

## 常见问题排查

### 查询返回 0 条结果
1. 检查 `debug_page.html` 查看页面源码
2. 验证 CSS 选择器是否匹配
3. 使用 `--no-headless` 可视化调试
4. 确认携程 URL 格式未变化

### 反爬虫被触发
- 调整时间窗口的随机化范围
- 更新 User-Agent 字符串
- 增加等待时间（`time.sleep`）
- 检查是否需要处理 CAPTCHA
