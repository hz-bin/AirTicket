# AirTicket - 航班价格监控系统

<div align="center">

📊 自动监控携程网国际航班价格，生成历史趋势图表

[![Go Version](https://img.shields.io/badge/Go-1.16+-00ADD8?style=flat&logo=go)](https://golang.org/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## ✨ 功能特点

- 🤖 **全自动调度** - Go 调度器在每天多个时间窗口自动执行查询
- 🎯 **直飞筛选** - 智能过滤中转航班，只保留直飞选项
- 📈 **价格趋势** - 生成可视化图表，追踪价格历史变化
- 🛡️ **反爬虫策略** - 随机时间执行、无头浏览器、User-Agent 伪装
- 💾 **数据持久化** - JSON 快照 + Excel 历史记录双重保存
- 🌏 **国际航线** - 支持国内外主要城市航班查询

## 🚀 快速开始

### 环境要求

- **Go** 1.16+ (用于调度器)
- **Python** 3.8+ (用于爬虫和图表)
- **Chrome/Chromium** 浏览器 (Selenium 依赖)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/AirTicket.git
cd AirTicket
```

2. **创建 Python 虚拟环境**
```bash
python -m venv .venv
.\.venv\Scripts\pip.exe install selenium webdriver-manager beautifulsoup4 openpyxl pandas plotly
```

3. **配置查询航线**

编辑 `config.json` 文件，添加需要监控的航线：
```json
{
  "queries": [
    {
      "from": "sha",
      "to": "akl",
      "date": "2026-09-25"
    },
    {
      "from": "pek",
      "to": "syd",
      "date": "2026-10-01"
    }
  ]
}
```

4. **构建调度器**
```bash
go build -o AirTicket.exe AirTicket.go
```

### 使用方法

#### 启动自动监控（Windows）

```batch
# 后台启动调度服务
start.bat

# 停止调度服务
stop.bat
```

调度器将在每天以下时间窗口随机执行查询：
- 上午：10:00 - 12:00
- 下午：14:00 - 16:00
- 傍晚：18:00 - 20:00

#### 手动单次查询

```bash
# 查询上海到奥克兰的航班
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25

# 显示浏览器窗口（调试模式）
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25 --no-headless

# 保存页面源码用于调试
.\.venv\Scripts\python.exe .\query.py --from sha --to akl --date 2026-09-25 --debug
```

#### 生成价格趋势图表

```bash
.\.venv\Scripts\python.exe .\chart.py
```

生成的 `flights_chart.html` 将自动在浏览器中打开，展示交互式价格趋势图。

## 📋 支持的城市代码

| 代码  | 城市   | 代码  | 城市   | 代码  | 城市   |
|-------|--------|-------|--------|-------|--------|
| `sha` | 上海   | `pek` | 北京   | `can` | 广州   |
| `hgh` | 杭州   | `szx` | 深圳   | `ctu` | 成都   |
| `akl` | 奥克兰 | `syd` | 悉尼   | `mel` | 墨尔本 |

*添加更多城市：编辑 `query.py` 中的 `CITY_LABELS` 字典*

## 📊 数据输出

### JSON 快照
每次查询生成独立文件：
```
flights_sha_akl_2026-09-25.json
```

### Excel 历史记录
所有查询结果追加到 `flights_history.xlsx`：
- **Sheet 命名**：`sha→akl 2026-09-25`
- **包含字段**：查询时间、价格、航班号、航空公司、出发/到达时间、飞行时长

### 可视化图表
`flights_chart.html` - 基于 Plotly 的交互式价格趋势图

## 🛠️ 技术架构

```
┌──────────────┐
│  AirTicket.go │  ← Go 调度器（定时任务）
└───────┬──────┘
        │ 调用
        ↓
┌──────────────┐
│   query.py   │  ← Selenium 爬虫（数据采集）
└───────┬──────┘
        │ 保存
        ↓
┌──────────────────────────┐
│ JSON + Excel            │  ← 数据持久化
└───────┬──────────────────┘
        │ 读取
        ↓
┌──────────────┐
│  chart.py    │  ← 数据可视化（Plotly）
└──────────────┘
```

## ⚙️ 高级配置

### 修改时间窗口

编辑 `AirTicket.go`：
```go
var timeWindows = [][2]int{
    {10, 12},  // 上午 10-12 点
    {14, 16},  // 下午 14-16 点
    {18, 20},  // 傍晚 18-20 点
    {22, 23},  // 可添加更多时间窗口
}
```

### 爬虫参数调整

`query.py` 中的关键参数：
- **价格范围**：`1000 <= price <= 50000` (过滤无效价格)
- **直飞关键词**：`['经停', '中转', '转机', '联程']` (排除中转)
- **等待超时**：`WebDriverWait(driver, 15)` (页面加载超时)

## 📝 日志查看

```bash
# 查看调度器日志
tail -f logs/scheduler.log

# Windows 使用记事本打开
notepad logs\scheduler.log
```

日志包含：
- 调度执行时间
- 查询成功/失败状态
- Python 爬虫输出

## ❓ 常见问题

<details>
<summary><b>爬虫返回空结果怎么办？</b></summary>

1. 检查网络连接和携程网站访问
2. 使用 `--no-headless` 查看浏览器实际操作
3. 使用 `--debug` 保存页面源码分析
4. 携程可能临时无该日期的航班数据
</details>

<details>
<summary><b>Excel 文件无法写入？</b></summary>

关闭所有打开的 Excel 实例，`openpyxl` 需要独占文件访问。
</details>

<details>
<summary><b>ChromeDriver 版本不匹配？</b></summary>

项目使用 `webdriver-manager` 自动管理驱动，确保网络连接正常以便自动下载匹配版本。
</details>

<details>
<summary><b>如何添加新城市？</b></summary>

1. 在 携程网 查找城市代码（URL 中的三字母代码）
2. 编辑 `query.py`：
```python
CITY_LABELS = {
    'sha': '上海',
    'nrt': '东京',  # 新增
    # ...
}
```
3. 在 `config.json` 中添加查询配置
</details>

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本项目仅用于学习和个人使用。请遵守携程网的使用条款和 robots.txt 规则，合理控制请求频率。

---

<div align="center">
Made with ❤️ for travelers | 为旅行者打造
</div>
