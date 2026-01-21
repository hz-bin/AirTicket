# AirTicket 项目 - AI 编程助手指南

## 项目概述
这是一个航班票价监控系统，自动查询携程网国际航班价格并生成历史趋势图表。

**核心组件:**
- **AirTicket.go**: Go 调度器，每天在随机时间窗口（10-12点、14-16点、18-20点）执行查询
- **query.py**: Selenium 爬虫，从携程网抓取直飞航班价格和时刻信息
- **chart.py**: 数据可视化，从 Excel 历史记录生成交互式 HTML 图表
- **config.json**: 查询配置，定义监控的航线和日期

## 架构特点

### 数据流
1. Go 调度器 → 调用 Python 爬虫（带 `--headless` 参数）
2. 爬虫 → 保存 JSON 快照（`flights_{from}_{to}_{date}.json`）+ 追加到 Excel（`flights_history.xlsx`）
3. 图表生成器 → 读取 Excel 历史数据 → 输出 `flights_chart.html`

### 时间窗口调度设计
- 每个时间窗口内随机选择时刻执行（反爬虫）
- 跨日调度：当天窗口都过期后自动计划次日
- 日志输出到 `logs/scheduler.log` 和控制台

## 关键约定

### Python 环境
- **必须使用虚拟环境**: `.venv/Scripts/python.exe`（Go 代码优先查找此路径）
- 依赖：`selenium`, `webdriver-manager`, `beautifulsoup4`, `openpyxl`, `pandas`
- 安装：`python -m venv .venv && .\.venv\Scripts\pip.exe install selenium webdriver-manager beautifulsoup4 openpyxl pandas`

### 城市代码映射
在 `query.py` 的 `CITY_LABELS` 字典中维护（例：`'sha': '上海'`, `'akl': '奥克兰'`）。添加新城市时必须同步更新此映射。

### 爬虫反检测策略
- 启用 Chrome 无头模式 + 伪装 User-Agent
- 禁用自动化标识：`excludeSwitches: ["enable-automation"]`
- 直飞过滤：排除包含 `['经停', '中转', '转机', '联程']` 关键词的航班
- 价格提取范围：¥1000-50000（避免误识别序号/税费）

### Excel 数据结构
- **Sheet 命名**: `{from}→{to} {date}` (例：`sha→akl 2026-09-25`)
- **列**: `查询时间`, `价格(¥)`, `出发日期`, `出发时间`, `到达时间`, `航班号`, `航空公司`, `飞行时长`
- 同一航线+日期的所有历史查询记录追加到同一 Sheet

## 开发工作流

### 启动/停止服务
```batch
# 启动后台调度器（Windows）
start.bat  # 后台运行 AirTicket.exe

# 停止调度器
stop.bat   # 杀掉 AirTicket.exe 进程
```

### 手动测试单次查询
```powershell
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25
# 添加 --no-headless 可查看浏览器操作过程
# 添加 --debug 保存页面源码到 debug_page.html
```

### 生成图表
```powershell
.\.venv\Scripts\python.exe .\chart.py
# 自动打开 flights_chart.html 在浏览器中
```

### 构建调度器
```powershell
go build -o AirTicket.exe AirTicket.go
```

## 修改指南

### 添加新航线
编辑 `config.json`，在 `queries` 数组中添加：
```json
{"from": "pek", "to": "syd", "date": "2026-10-01"}
```

### 调整时间窗口
修改 `AirTicket.go` 中的 `timeWindows` 变量：
```go
var timeWindows = [][2]int{
    {10, 12},  // 上午
    {14, 16},  // 下午
    {18, 20},  // 傍晚
}
```

### 处理携程页面结构变化
1. 运行带 `--debug` 的查询保存页面源码
2. 检查 `query.py` 中的 CSS 选择器（`.item-inner`, `.product` 等）
3. 更新正则表达式（航班号、价格、时间提取）

## 常见问题

### 爬虫返回空结果
- 检查网络连接和 ChromeDriver 版本
- 尝试 `--no-headless` 模式观察页面加载
- 携程可能临时无该航线数据

### Excel 文件锁定
关闭所有 Excel 实例后重试，程序使用 `openpyxl` 需要独占访问。

### 日志位置
- 调度器：`logs/scheduler.log`
- Python 爬虫输出会被重定向到调度器日志
