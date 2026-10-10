# FutureFortune

> 研究历史数据，期待未来财富。

中国彩票历史数据可视化平台，目前包含排列三和排列五，后续将增加更多彩种。

## 数据概览

| 项目 | 排列三 | 排列五 |
|------|--------|--------|
| 起始期号 | 04009 (2004-11-26) | 04009 (2004-11-26) |
| 最新期号 | 26268 (2026-10-09) | 26268 (2026-10-09) |
| 总期数 | 7,735 | 7,735 |
| 数据来源 | 江苏体彩网 | 江苏体彩网 |

> 排列三数据 = 排列五前三位号码

## 功能

- [x] 全部历史数据表格展示（分页）
- [x] 按期号搜索、按年份筛选
- [x] 各位号码频率统计
- [x] 和值分布图
- [x] 跨度分布图
- [x] 冷热号分析（最近30期）
- [x] 当前遗漏值
- [x] GitHub Actions 每日自动更新数据

## 支持的彩种

- [x] 排列三（3位数）
- [x] 排列五（5位数）
- [ ] 大乐透（待添加）
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
│   ├── index.html           # 主页面
│   ├── style.css            # 样式
│   ├── app.js               # 前端逻辑
│   ├── data.js              # 排列五数据（自动生成）
│   └── data_p3.js           # 排列三数据（自动生成）
├── scripts/
│   └── fetch_lottery.py     # 数据爬取脚本
├── archive/                 # 历史脚本归档
├── pl3_all_data.json         # 排列三原始数据
├── pl5_all_data.json         # 排列五原始数据
├── .gitignore
└── README.md
```

## 自动更新

GitHub Actions 每天凌晨自动运行：
1. 从江苏体彩网爬取最新排列五数据
2. 提取前三位作为排列三数据
3. 更新 `docs/data.js` 和 `docs/data_p3.js`
4. 自动 commit & push

## 本地预览

```bash
cd docs
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 免责声明

数据仅供参考，彩票有风险，投注需谨慎。
