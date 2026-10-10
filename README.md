# 将来会有钱的 (FutureFortune)

> 研究历史数据，期待未来财富。

中国彩票历史数据可视化平台，目前包含排列三、排列五和超级大乐透，后续将增加更多彩种。

**[在线预览](https://ahbencat.github.io/futurefortune/)**

## 数据概览

| 项目 | 排列三 | 排列五 | 超级大乐透 |
|------|--------|--------|-----------|
| 起始期号 | 04009 (2004-11-26) | 04009 (2004-11-26) | 07001 (2007-05-30) |
| 最新期号 | 26268 (2026-10-09) | 26268 (2026-10-09) | 26114 (2026-10-07) |
| 总期数 | 7,735 | 7,735 | 2,932 |
| 数据来源 | 江苏体彩网 | 江苏体彩网 | 中国体彩网 |

> 排列三数据 = 排列五前三位号码

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
FutureFortune/
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
│   ├── lottery_common.py    # 公共函数（读写/合并/摘要）
│   ├── fetch_lottery.py     # 排列3/5 抓取（江苏体彩网）
│   └── fetch_dlt.py         # 大乐透抓取（中国体彩网接口）
├── archive/                 # 历史脚本归档
├── pl3_all_data.json         # 排列三原始数据
├── pl5_all_data.json         # 排列五原始数据
├── dlt_all_data.json         # 大乐透原始数据
├── .gitignore
└── README.md
```

## 自动更新

GitHub Actions 每天凌晨自动运行：
1. 从江苏体彩网爬取排列五、排列三数据
2. 从中国体彩网接口爬取超级大乐透数据
3. 生成 `docs/assets/data/` 下的 `data.js`、`data_p3.js`、`data_dlt.js`
4. 自动 commit & push

## 本地预览

```bash
cd docs
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 免责声明

数据仅供参考，彩票有风险，投注需谨慎。
