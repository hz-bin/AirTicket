#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import webbrowser
import json
from datetime import datetime
from collections import defaultdict

def log_print(msg):
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f"{timestamp} {msg}")

def generate_flight_charts():
    excel_file = 'flights_history.xlsx'
    
    if not os.path.exists(excel_file):
        log_print(f"❌ 文件 {excel_file} 不存在")
        return
    
    try:
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        
        if not sheet_names:
            log_print("❌ Excel文件中没有sheet")
            return
        
        log_print(f"✅ 找到 {len(sheet_names)} 个sheet")
        
        # Organize data by departure date
        date_data = defaultdict(lambda: defaultdict(list))
        
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                if df.empty:
                    log_print(f"⚠️ Sheet '{sheet_name}' 是空的，跳过")
                    continue
                
                # Handle Chinese column names
                query_col = '查询时间' if '查询时间' in df.columns else 'query_time'
                price_col = '价格(¥)' if '价格(¥)' in df.columns else 'price'
                date_col = '出发日期' if '出发日期' in df.columns else 'flight_date'
                dep_time_col = '出发时间' if '出发时间' in df.columns else 'departure_time'
                arr_time_col = '到达时间' if '到达时间' in df.columns else 'arrival_time'
                
                if query_col not in df.columns or price_col not in df.columns:
                    log_print(f"⚠️ Sheet '{sheet_name}' 缺少必要的列，跳过")
                    continue
                
                df['query_time'] = pd.to_datetime(df[query_col], errors='coerce')
                df['price'] = pd.to_numeric(df[price_col], errors='coerce')
                
                # Extract departure and arrival times
                dep_time = df[dep_time_col].iloc[0] if dep_time_col in df.columns and not df.empty else ''
                arr_time = df[arr_time_col].iloc[0] if arr_time_col in df.columns and not df.empty else ''
                
                # Extract flight date
                if date_col in df.columns:
                    df['flight_date'] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
                else:
                    import re
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', sheet_name)
                    flight_date = match.group(1) if match else '2026-01-01'
                    df['flight_date'] = flight_date
                
                df = df.dropna(subset=['query_time', 'price', 'flight_date'])
                df = df.sort_values('query_time')
                
                if df.empty:
                    log_print(f"⚠️ Sheet '{sheet_name}' 没有有效数据，跳过")
                    continue
                
                # Group by flight date
                for flight_date, group_df in df.groupby('flight_date'):
                    data_points = []
                    for idx, row in group_df.iterrows():
                        data_points.append({
                            'time': row['query_time'].strftime('%H:%M:%S'),
                            'price': float(row['price'])
                        })
                    
                    date_data[flight_date][sheet_name] = {
                        'data': data_points,
                        'dep_time': dep_time,
                        'arr_time': arr_time
                    }
                
                log_print(f"✅ 已处理sheet '{sheet_name}'")
                
            except Exception as e:
                log_print(f"❌ 处理sheet '{sheet_name}' 时出错: {str(e)}")
                continue
        
        # Convert to list for JSON serialization - each sheet gets its own chart
        charts_data = []
        for flight_date in sorted(date_data.keys()):
            flights = date_data[flight_date]
            
            # Create a chart for each flight
            for flight_name, flight_info in flights.items():
                data_points = flight_info['data']
                dep_time = flight_info['dep_time']
                arr_time = flight_info['arr_time']
                
                if data_points:
                    times = [p['time'] for p in data_points]
                    prices = [p['price'] for p in data_points]
                    
                    charts_data.append({
                        'name': flight_name,
                        'date': flight_date,
                        'times': times,
                        'prices': prices,
                        'dep_time': dep_time,
                        'arr_time': arr_time
                    })
        
        log_print(f"✅ 已组织 {len(charts_data)} 个航班的数据")
        
        # Generate HTML with ECharts
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>航班价格历史分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.0/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }
        
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .chart-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }
        
        @media (max-width: 1400px) {
            .charts-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 900px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .chart-title {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        
        .chart {
            width: 100%;
            height: 240px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✈️ 航班价格历史分析</h1>
    </div>
    
    <div id="charts-container" class="charts-grid">
        <!-- Charts will be generated here -->
    </div>
    
    <script>
        const chartsData = """ + json.dumps(charts_data) + """;
        
        function generateCharts() {
            const container = document.getElementById('charts-container');
            
            chartsData.forEach((chartData, index) => {
                const chartDiv = document.createElement('div');
                chartDiv.className = 'chart-container';
                
                const title = document.createElement('div');
                title.className = 'chart-title';
                
                // Add flight name and time info in the same line
                if (chartData.dep_time && chartData.arr_time) {
                    title.innerHTML = chartData.name + '<span style="margin-left: 15px;">' + chartData.dep_time + ' → ' + chartData.arr_time + '</span>';
                } else {
                    title.textContent = chartData.name;
                }
                
                chartDiv.appendChild(title);
                
                const chartElem = document.createElement('div');
                chartElem.className = 'chart';
                chartElem.id = 'chart-' + index;
                
                chartDiv.appendChild(chartElem);
                container.appendChild(chartDiv);
                
                initChart(index, chartData);
            });
        }
        
        function initChart(index, chartData) {
            const chartDom = document.getElementById('chart-' + index);
            const myChart = echarts.init(chartDom);
            
            // Prepare single series data
            const seriesData = [{
                name: chartData.name,
                type: 'line',
                data: chartData.prices,
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: {
                    width: 2
                }
            }];
            
            const option = {
                title: {
                    text: '',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: 'rgba(0, 0, 0, 0.95)',
                    borderColor: '#777',
                    borderWidth: 1,
                    textStyle: {
                        color: '#fff',
                        fontSize: 12
                    },
                    axisPointer: {
                        type: 'line',
                        lineStyle: {
                            color: '#999',
                            width: 1,
                            type: 'dashed'
                        }
                    },
                    formatter: function(params) {
                        let html = '<div style="font-weight: bold; margin-bottom: 8px;">' + params[0].axisValue + '</div>';
                        params.forEach(param => {
                            html += '<div style="margin: 4px 0;"><span style="display:inline-block; width: 10px; height: 10px; background-color: ' + param.color + '; border-radius: 2px; margin-right: 6px;"></span>' 
                                + param.seriesName + ': <strong style="color: ' + param.color + ';">' + param.value + ' 元</strong></div>';
                        });
                        return html;
                    }
                },
                legend: {
                    show: false,
                    data: [chartData.name],
                    top: 30,
                    textStyle: {
                        fontSize: 12
                    },
                    type: 'scroll',
                    orient: 'horizontal'
                },
                grid: {
                    left: '5%',
                    right: '5%',
                    bottom: '10%',
                    top: '15%',
                    containLabel: true
                },
                toolbox: {
                    feature: {
                        saveAsImage: {
                            pixelRatio: 2,
                            backgroundColor: '#fff'
                        },
                        dataZoom: {},
                        restore: {}
                    },
                    top: 10,
                    right: 20
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: chartData.times,
                    axisLabel: {
                        fontSize: 11
                    },
                    splitLine: {
                        show: true,
                        lineStyle: {
                            color: '#eee',
                            type: 'dashed'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    name: '价格 (元)',
                    scale: true,
                    min: function(value) {
                        return Math.floor(value.min * 0.95);
                    },
                    max: function(value) {
                        return Math.ceil(value.max * 1.02);
                    },
                    nameTextStyle: {
                        fontSize: 11
                    },
                    axisLabel: {
                        fontSize: 11
                    },
                    splitLine: {
                        show: true,
                        lineStyle: {
                            color: '#eee',
                            type: 'dashed'
                        }
                    }
                },
                series: seriesData
            };
            
            myChart.setOption(option);
            
            // Handle window resize
            window.addEventListener('resize', () => {
                myChart.resize();
            });
        }
        
        // Initialize when page loads
        window.addEventListener('load', generateCharts);
    </script>
</body>
</html>
"""
        
        output_file = 'flights_chart.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        log_print(f"✅ HTML文件已生成: {output_file}")
        
        webbrowser.open(os.path.abspath(output_file))
        log_print(f"✅ 正在打开HTML文件...")
        
    except Exception as e:
        log_print(f"❌ 错误: {str(e)}")

# .venv\Scripts\python.exe chart.py
if __name__ == '__main__':
    generate_flight_charts()
