# 排列三 & 排列五 历史数据

> 中国体育彩票排列三、排列五历史开奖数据展示平台

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
- [x] 按期号搜索
- [x] 按年份筛选
- [x] 各位号码频率统计
- [x] 和值分布图
- [x] 跨度分布图
- [x] 冷热号分析（最近30期）
- [x] 当前遗漏值
- [x] GitHub Actions 每日自动更新数据

## 技术栈

- 纯静态：HTML + CSS + JavaScript
- 图表：Chart.js (CDN)
- 数据：JSON → JS 变量
- 部署：GitHub Pages
- 自动化：GitHub Actions (Python)

## 项目结构

```
lottory_pick/
├── .github/workflows/
│   └── update_data.yml      # GitHub Actions 定时爬取
├── docs/                     # GitHub Pages 站点
│   ├── index.html           # 主页面
│   ├── style.css            # 样式
│   ├── app.js               # 前端逻辑
│   └── data.js              # 数据文件（自动生成）
├── scripts/
│   └── fetch_lottery.py     # 数据爬取脚本
├── archive/                 # 历史脚本归档
└── README.md
```

## 自动更新

GitHub Actions 每天凌晨自动运行：
1. 从江苏体彩网爬取最新排列五数据
2. 提取前三位作为排列三数据
3. 更新 `docs/data.js`
4. 自动 commit & push

## 本地预览

```bash
cd docs
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 许可证

数据仅供参考，彩票有风险，投注需谨慎。
