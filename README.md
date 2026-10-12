# 将来会有钱的

> 研究历史数据，期待未来财富。

中国彩票历史数据整理及可视化平台，目前包含排列三、排列五和超级大乐透，后续将增加更多彩种。

[![在线预览](https://img.shields.io/badge/在线预览-🌐_GitHub_Pages-blue?style=for-the-badge)](https://ahbencat.github.io/futurefortune/)

## 📊 数据概览

| 彩种 | 起始期号 | 最新期号 | 总期数 |
| :--- | :--- | :--- | ---: |
| 🎱 **排列三** | 04001 <sub>2004-11-14</sub> | **26270** <sub>2026-10-11</sub> | **7,745** |
| 🎲 **排列五** | 04009 <sub>2004-11-26</sub> | **26270** <sub>2026-10-11</sub> | **7,737** |
| 🎯 **超级大乐透** | 07001 <sub>2007-05-30</sub> | **26115** <sub>2026-10-10</sub> | **2,933** |

> 数据来源：公开开奖数据 · 每日自动更新

## 功能

- [x] 彩种切换（排列五 / 超级大乐透）
- [x] 全部历史数据表格展示（分页）
- [x] 按期号搜索、按年份筛选
- [x] 号码频率统计
- [x] 和值分布图
- [x] 跨度分布图
- [x] 冷热号分析（最近30期，排列五）
- [x] 当前遗漏值
- [x] GitHub Actions 每日自动更新数据

## 支持的彩种

- [x] 排列三（3位数）
- [x] 排列五（5位数）
- [x] 超级大乐透（前区5个 01-35 + 后区2个 01-12）
- [ ] 双色球（待添加）
- [ ] 七星彩（待添加）
- [ ] 其他彩种（规划中）

## 技术栈

- 纯静态：HTML + CSS + JavaScript
- 图表：Chart.js (CDN)
- 部署：GitHub Pages
- 自动化：GitHub Actions (Python)

## 项目结构

```
将来会有钱的/
├── .github/workflows/
│   └── update_data.yml      # GitHub Actions 定时爬取
├── docs/                     # GitHub Pages 站点
│   ├── index.html           # 主页面（含彩种切换）
│   └── assets/
│       ├── css/style.css    # 样式
│       ├── js/app.js        # 前端逻辑
│       └── data/            # 数据文件（自动生成）
│           ├── data.js       # 排列五数据
│           ├── data_p3.js    # 排列三数据
│           └── data_dlt.js   # 大乐透数据
├── scripts/
│   ├── lottery_common.py    # 公共函数（读写/合并/修正/摘要）
│   ├── fetch_lottery.py     # 排列5 抓取（兼容 --type p3）
│   ├── derive_p3.py         # 排列三派生（取排列五前三位，无需抓取）
│   ├── fetch_dlt.py         # 大乐透抓取
│   └── data_patches.json    # 数据修正表（源数据的已知错误/缺失期号）
├── datas/                   # 原始数据（抓取结果，单一事实来源）
│   ├── pl3_all_data.json     # 排列三
│   ├── pl5_all_data.json     # 排列五
│   └── dlt_all_data.json     # 大乐透
├── archive/                 # 历史脚本归档
├── .gitignore
└── README.md
```

## 自动更新

GitHub Actions 每天凌晨自动运行：
1. 抓取排列五最新开奖数据
2. 排列三由排列五前三位**派生**（不重复抓取，见 `scripts/derive_p3.py`）
3. 抓取超级大乐透最新开奖数据
4. 应用 `scripts/data_patches.json` 中的数据修正（源数据的日期错误、缺失期号）
5. 生成 `docs/assets/data/` 下的 `data.js`、`data_p3.js`、`data_dlt.js`
6. 自动 commit & push

> ⏰ 定时任务设定为每日 **02:00 UTC（北京时间 10:00）**。受 GitHub Actions 负载影响，实际触发时间**可能延迟数小时**。
> 抓取采用增量方式且幂等，延迟不会造成数据丢失，恢复运行后会自动追平最新开奖。

## 本地预览

```bash
cd docs
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 免责声明

数据仅供参考，彩票有风险，投注需谨慎。
