// 全局状态
let activeLottery = 'pl5';   // 'pl5' | 'dlt'
let currentPage = 1;
let pageSize = 50;
let filteredData = [];
let charts = {};

// 彩种元信息
const LOTTERY_META = {
    pl5: { title: '排列五(含排列三)历史数据' },
    dlt: { title: '超级大乐透历史数据' },
    qxc: { title: '7星彩历史数据' },
    ssq: { title: '双色球历史数据' }
};

// 当前彩种的数据集
function activeData() {
    if (activeLottery === 'dlt') {
        return typeof LOTTERY_DATA_DLT !== 'undefined' ? LOTTERY_DATA_DLT : [];
    }
    if (activeLottery === 'qxc') {
        return typeof LOTTERY_DATA_QXC !== 'undefined' ? LOTTERY_DATA_QXC : [];
    }
    if (activeLottery === 'ssq') {
        return typeof LOTTERY_DATA_SSQ !== 'undefined' ? LOTTERY_DATA_SSQ : [];
    }
    return LOTTERY_DATA;
}

// 按期号倒序（最新在前）
function sortByIssueDesc(data) {
    return [...data].sort((a, b) => parseInt(b.issue_no) - parseInt(a.issue_no));
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setLottery('pl5');
});

// 切换彩种
function setLottery(type) {
    activeLottery = type;
    currentPage = 1;
    filteredData = sortByIssueDesc(activeData());

    document.getElementById('searchInput').value = '';
    document.getElementById('yearFilter').value = '';
    initYearFilter();
    updateHeader();
    toggleSections();

    renderTable();
    renderCharts();
    renderOmitValues();
}

// 标题与副标题
function updateHeader() {
    const data = activeData();
    document.getElementById('pageTitle').textContent = LOTTERY_META[activeLottery].title;
    if (data.length) {
        const first = data[0];
        const last = data[data.length - 1];
        document.getElementById('pageSubtitle').textContent =
            `${first.date} 至 ${last.date} | 共 ${data.length.toLocaleString()} 期`;
    }

    document.querySelectorAll('.switch-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lottery === activeLottery);
    });
}

// 切换表格与图表的显示
function toggleSections() {
    const isDlt = activeLottery === 'dlt';
    const isQxc = activeLottery === 'qxc';
    const isSsq = activeLottery === 'ssq';
    document.getElementById('pl5TableContainer').hidden = isDlt || isQxc || isSsq;
    document.getElementById('dltTableContainer').hidden = !isDlt;
    document.getElementById('qxcTableContainer').hidden = !isQxc;
    document.getElementById('ssqTableContainer').hidden = !isSsq;
    document.getElementById('chartsPl5').hidden = isDlt || isQxc || isSsq;
    document.getElementById('chartsDlt').hidden = !isDlt;
    document.getElementById('chartsQxc').hidden = !isQxc;
    document.getElementById('chartsSsq').hidden = !isSsq;

    const omitTitle = document.getElementById('omitTitle');
    if (isDlt) omitTitle.textContent = '当前遗漏值（前区 01-35 / 后区 01-12）';
    else if (isQxc) omitTitle.textContent = '当前遗漏值（前6位 0-9 / 特别号 0-14）';
    else if (isSsq) omitTitle.textContent = '当前遗漏值（红球 01-33 / 蓝球 01-16）';
    else omitTitle.textContent = '当前遗漏值（距离上次开出期数）';
    document.getElementById('omitGrid').classList.toggle('wide', isDlt || isQxc || isSsq);
}

// 初始化年份筛选
function initYearFilter() {
    const years = [...new Set(activeData().map(d => d.issue_no.substring(0, 2)))].sort();
    const select = document.getElementById('yearFilter');
    select.innerHTML = '<option value="">全部</option>';
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = '20' + year + '年';
        select.appendChild(option);
    });
}

// 渲染表格
function renderTable() {
    if (activeLottery === 'dlt') {
        renderDltTable();
    } else if (activeLottery === 'qxc') {
        renderQxcTable();
    } else if (activeLottery === 'ssq') {
        renderSsqTable();
    } else {
        renderPl5Table();
    }
    renderPagination();
}

// 排列三数据按期号索引（真实开奖号码）
let p3ByIssue = null;
function getP3Map() {
    if (p3ByIssue === null) {
        p3ByIssue = {};
        if (typeof LOTTERY_DATA_P3 !== 'undefined') {
            LOTTERY_DATA_P3.forEach(d => { p3ByIssue[d.issue_no] = d.numbers; });
        }
    }
    return p3ByIssue;
}

// 渲染排列五表格
function renderPl5Table() {
    const tbody = document.getElementById('tableBody');
    const p3Map = getP3Map();

    tbody.innerHTML = currentPageData().map(item => {
        const nums = item.numbers.map(n => parseInt(n));
        const sum = nums.reduce((a, b) => a + b, 0);
        const span = Math.max(...nums) - Math.min(...nums);

        // 04009-04020 期间排列三与排列五独立摇奖，前三位并不等于排列三开奖号码
        const p3 = p3Map[item.issue_no];
        const differs = p3 && p3.join('') !== item.numbers.slice(0, 3).join('');

        // 数据相同：左侧排列三框取排列五前三位 + 右侧后两位（常规格式）
        // 数据不同：左侧排列三框显示真实开奖号码 + 右侧完整显示排列五
        const p3Numbers = differs ? p3.map(Number) : nums.slice(0, 3);
        const pl5Numbers = differs ? nums : nums.slice(3);

        // 颜色按数字（n0-n9）统一配色，与位置无关
        const pl3Balls = p3Numbers.map(n => `<span class="pl3-ball n${n}">${n}</span>`).join('');
        const pl5Balls = pl5Numbers.map(n => `<span class="pl5-ball n${n}">${n}</span>`).join('');

        return `<tr>
            <td>${item.issue_no}</td>
            <td>${item.date}</td>
            <td colspan="5" class="pl5-cell">
                <div class="pl5-group">
                    <div class="pl3-cell"${differs ? ' title="2004年早期排列三与排列五独立摇奖，前三位不相同"' : ''}>
                        <div class="pl3-group">${pl3Balls}</div>
                    </div>
                    <div class="pl5-only">${pl5Balls}</div>
                </div>
            </td>
            <td>${sum}</td>
            <td>${span}</td>
        </tr>`;
    }).join('');
}

// 渲染大乐透表格
function renderDltTable() {
    const tbody = document.getElementById('dltTableBody');
    const pageData = currentPageData();

    tbody.innerHTML = pageData.map(item => {
        const front = item.front.map(n => parseInt(n));
        const sum = front.reduce((a, b) => a + b, 0);
        const span = Math.max(...front) - Math.min(...front);
        const frontBalls = item.front.map(n => `<span class="dlt-front-ball">${n}</span>`).join('');
        const backBalls = item.back.map(n => `<span class="dlt-back-ball">${n}</span>`).join('');

        return `<tr>
            <td>${item.issue_no}</td>
            <td>${item.date}</td>
            <td colspan="5" class="dlt-front-cell"><div class="dlt-group">${frontBalls}</div></td>
            <td colspan="2" class="dlt-back-cell"><div class="dlt-group">${backBalls}</div></td>
            <td>${sum}</td>
            <td>${span}</td>
        </tr>`;
    }).join('');
}

// 渲染7星彩表格（6位号码 + 特别号）
function renderQxcTable() {
    const tbody = document.getElementById('qxcTableBody');

    tbody.innerHTML = currentPageData().map(item => {
        const nums = item.numbers.map(n => parseInt(n));
        const front = nums.slice(0, 6);
        const special = nums[6];
        const sum = front.reduce((a, b) => a + b, 0);
        const span = Math.max(...front) - Math.min(...front);

        // 颜色按数字（n0-n9）统一配色
        const frontBalls = front.map(n => `<span class="qxc-ball n${n}">${n}</span>`).join('');
        const specialBall = `<span class="qxc-special-ball">${special}</span>`;

        return `<tr>
            <td>${item.issue_no}</td>
            <td>${item.date}</td>
            <td colspan="6" class="qxc-front-cell"><div class="qxc-group">${frontBalls}</div></td>
            <td class="qxc-special-cell"><div class="qxc-group"><span class="qxc-plus">+</span>${specialBall}</div></td>
            <td>${sum}</td>
            <td>${span}</td>
        </tr>`;
    }).join('');
}

// 当前页数据
function currentPageData() {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
}

// 分页信息
function renderPagination() {
    const totalPages = Math.ceil(filteredData.length / pageSize);
    document.getElementById('pageInfo').textContent =
        `第 ${currentPage} 页 / 共 ${totalPages} 页 (共 ${filteredData.length} 条)`;
}

// 搜索
function searchData() {
    const query = document.getElementById('searchInput').value.trim();
    const data = activeData();
    filteredData = sortByIssueDesc(query ? data.filter(d => d.issue_no.includes(query)) : data);
    currentPage = 1;
    renderTable();
}

// 年份筛选
function filterByYear() {
    const year = document.getElementById('yearFilter').value;
    const data = activeData();
    filteredData = sortByIssueDesc(year ? data.filter(d => d.issue_no.startsWith(year)) : data);
    currentPage = 1;
    renderTable();
}

// 改变每页条数
function changePageSize() {
    pageSize = parseInt(document.getElementById('pageSize').value);
    currentPage = 1;
    renderTable();
}

// 分页
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderTable();
    }
}

function nextPage() {
    const totalPages = Math.ceil(filteredData.length / pageSize);
    if (currentPage < totalPages) {
        currentPage++;
        renderTable();
    }
}

// 往后跳转10页
function jumpForward10() {
    const totalPages = Math.ceil(filteredData.length / pageSize);
    currentPage = Math.min(totalPages, currentPage + 10);
    renderTable();
}

// 往前跳转10页
function jumpBack10() {
    currentPage = Math.max(1, currentPage - 10);
    renderTable();
}

// 渲染图表
function renderCharts() {
    // 切换彩种时销毁旧图表，避免 canvas 复用冲突
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    if (activeLottery === 'dlt') {
        renderDltFrontFreqChart();
        renderDltSumChart();
        renderDltSpanChart();
        renderDltBackFreqChart();
    } else if (activeLottery === 'qxc') {
        renderQxcFreqChart();
        renderQxcSumChart();
        renderQxcSpanChart();
        renderQxcSpecialFreqChart();
    } else if (activeLottery === 'ssq') {
        renderSsqFrontFreqChart();
        renderSsqSumChart();
        renderSsqSpanChart();
        renderSsqBackFreqChart();
    } else {
        renderFreqChart();
        renderSumChart();
        renderSpanChart();
        renderHotColdChart();
    }
}

// 号码频率统计
function renderFreqChart() {
    const ctx = document.getElementById('freqChart').getContext('2d');
    
    // 计算各位号码频率
    const positions = ['万位', '千位', '百位', '十位', '个位'];
    const datasets = [];
    const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];
    
    for (let pos = 0; pos < 5; pos++) {
        const freq = Array(10).fill(0);
        activeData().forEach(item => {
            freq[parseInt(item.numbers[pos])]++;
        });
        datasets.push({
            label: positions[pos],
            data: freq,
            backgroundColor: colors[pos] + '80',
            borderColor: colors[pos],
            borderWidth: 1
        });
    }

    charts.freq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 和值分布
function renderSumChart() {
    const ctx = document.getElementById('sumChart').getContext('2d');
    const sumFreq = {};

    activeData().forEach(item => {
        const sum = item.numbers.reduce((a, b) => a + parseInt(b), 0);
        sumFreq[sum] = (sumFreq[sum] || 0) + 1;
    });

    const labels = Object.keys(sumFreq).sort((a, b) => a - b);
    const data = labels.map(l => sumFreq[l]);

    charts.sum = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: data,
                backgroundColor: '#667eea80',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 跨度分布
function renderSpanChart() {
    const ctx = document.getElementById('spanChart').getContext('2d');
    const spanFreq = {};

    activeData().forEach(item => {
        const nums = item.numbers.map(n => parseInt(n));
        const span = Math.max(...nums) - Math.min(...nums);
        spanFreq[span] = (spanFreq[span] || 0) + 1;
    });

    const labels = Object.keys(spanFreq).sort((a, b) => a - b);
    const data = labels.map(l => spanFreq[l]);

    charts.span = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: data,
                backgroundColor: '#43e97b80',
                borderColor: '#43e97b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 冷热号分析（最近30期）
function renderHotColdChart() {
    const ctx = document.getElementById('hotColdChart').getContext('2d');
    const recentData = activeData().slice(-30);
    
    // 统计各位号码出现次数
    const hotColdData = [];
    for (let pos = 0; pos < 5; pos++) {
        const freq = Array(10).fill(0);
        recentData.forEach(item => {
            freq[parseInt(item.numbers[pos])]++;
        });
        hotColdData.push(freq);
    }

    // 计算平均出现次数
    const avg = 30 / 10;
    
    // 分类：热号(>avg*1.3)、冷号(<avg*0.7)、温号(其他)
    const hotCounts = Array(10).fill(0);
    const warmCounts = Array(10).fill(0);
    const coldCounts = Array(10).fill(0);
    
    for (let num = 0; num < 10; num++) {
        let totalFreq = 0;
        for (let pos = 0; pos < 5; pos++) {
            totalFreq += hotColdData[pos][num];
        }
        if (totalFreq > avg * 5 * 1.3) hotCounts[num] = totalFreq;
        else if (totalFreq < avg * 5 * 0.7) coldCounts[num] = totalFreq;
        else warmCounts[num] = totalFreq;
    }

    charts.hotCold = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            datasets: [
                {
                    label: '热号',
                    data: hotCounts,
                    backgroundColor: '#ff6b6b80',
                    borderColor: '#ff6b6b',
                    borderWidth: 1
                },
                {
                    label: '温号',
                    data: warmCounts,
                    backgroundColor: '#ffd93d80',
                    borderColor: '#ffd93d',
                    borderWidth: 1
                },
                {
                    label: '冷号',
                    data: coldCounts,
                    backgroundColor: '#6bcf7f80',
                    borderColor: '#6bcf7f',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 计算遗漏值：号码 -> 距离上次开出的期数（数据按期号升序）
function calcOmitValues(data, numbers, pickAll) {
    const lastAppear = {};
    numbers.forEach(n => { lastAppear[n] = -1; });

    data.forEach((item, i) => {
        pickAll(item).forEach(n => { lastAppear[n] = i; });
    });

    const total = data.length;
    const omitValues = {};
    numbers.forEach(n => {
        omitValues[n] = lastAppear[n] >= 0 ? total - 1 - lastAppear[n] : total;
    });
    return omitValues;
}

// 遗漏值球体 HTML（按遗漏大小分热/温/冷）
function omitBallsHtml(omitValues, numbers, format) {
    const values = numbers.map(n => omitValues[n]);
    const maxOmit = Math.max(...values);
    const minOmit = Math.min(...values);
    const threshold = (maxOmit - minOmit) / 3;

    return numbers.map(n => {
        let className = 'cold';
        if (omitValues[n] > maxOmit - threshold) className = 'hot';
        else if (omitValues[n] > minOmit + threshold) className = 'warm';

        const label = format ? format(n) : n;
        return `<div class="omit-ball ${className}" title="遗漏${omitValues[n]}期">${label}<br><small>${omitValues[n]}</small></div>`;
    }).join('');
}

// 渲染遗漏值
function renderOmitValues() {
    if (activeLottery === 'dlt') {
        renderDltOmitValues();
    } else if (activeLottery === 'qxc') {
        renderQxcOmitValues();
    } else if (activeLottery === 'ssq') {
        renderSsqOmitValues();
    } else {
        renderPl5OmitValues();
    }
}

// 排列五遗漏值（按 万/千/百/十/个 位分别统计）
function renderPl5OmitValues() {
    const grid = document.getElementById('omitGrid');
    const data = activeData();
    const positions = ['万位', '千位', '百位', '十位', '个位'];
    const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

    let html = '';
    for (let pos = 0; pos < 5; pos++) {
        const omitValues = calcOmitValues(data, numbers, item => [parseInt(item.numbers[pos])]);

        html += `<div class="omit-position">
            <h4>${positions[pos]}</h4>
            <div class="omit-balls">${omitBallsHtml(omitValues, numbers)}</div>
        </div>`;
    }

    grid.innerHTML = html;
}

// 大乐透遗漏值（前区 01-35 / 后区 01-12）
function renderDltOmitValues() {
    const grid = document.getElementById('omitGrid');
    const data = activeData();
    const pad2 = n => (n < 10 ? '0' + n : String(n));
    const range = (from, to) => Array.from({ length: to - from + 1 }, (_, i) => from + i);

    const frontNumbers = range(1, 35);
    const backNumbers = range(1, 12);

    const frontOmit = calcOmitValues(data, frontNumbers, item => item.front.map(Number));
    const backOmit = calcOmitValues(data, backNumbers, item => item.back.map(Number));

    grid.innerHTML = `<div class="omit-position">
            <h4>前区 (01-35)</h4>
            <div class="omit-balls">${omitBallsHtml(frontOmit, frontNumbers, pad2)}</div>
        </div>
        <div class="omit-position">
            <h4>后区 (01-12)</h4>
            <div class="omit-balls">${omitBallsHtml(backOmit, backNumbers, pad2)}</div>
        </div>`;
}

// 大乐透前区号码频率（01-35）
function renderDltFrontFreqChart() {
    const ctx = document.getElementById('dltFrontFreqChart').getContext('2d');
    const numbers = Array.from({ length: 35 }, (_, i) => i + 1);
    const freq = {};
    numbers.forEach(n => { freq[n] = 0; });

    activeData().forEach(item => {
        item.front.map(Number).forEach(n => { freq[n]++; });
    });

    charts.dltFrontFreq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: numbers.map(n => (n < 10 ? '0' + n : String(n))),
            datasets: [{
                label: '出现期数',
                data: numbers.map(n => freq[n]),
                backgroundColor: '#ff6b6b80',
                borderColor: '#ff6b6b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 大乐透前区和值分布
function renderDltSumChart() {
    const ctx = document.getElementById('dltSumChart').getContext('2d');
    const sumFreq = {};

    activeData().forEach(item => {
        const sum = item.front.reduce((a, b) => a + parseInt(b), 0);
        sumFreq[sum] = (sumFreq[sum] || 0) + 1;
    });

    const labels = Object.keys(sumFreq).sort((a, b) => a - b);

    charts.dltSum = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: labels.map(l => sumFreq[l]),
                backgroundColor: '#667eea80',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 大乐透前区跨度分布
function renderDltSpanChart() {
    const ctx = document.getElementById('dltSpanChart').getContext('2d');
    const spanFreq = {};

    activeData().forEach(item => {
        const nums = item.front.map(n => parseInt(n));
        const span = Math.max(...nums) - Math.min(...nums);
        spanFreq[span] = (spanFreq[span] || 0) + 1;
    });

    const labels = Object.keys(spanFreq).sort((a, b) => a - b);

    charts.dltSpan = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: labels.map(l => spanFreq[l]),
                backgroundColor: '#43e97b80',
                borderColor: '#43e97b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 大乐透后区号码频率（01-12）
function renderDltBackFreqChart() {
    const ctx = document.getElementById('dltBackFreqChart').getContext('2d');
    const numbers = Array.from({ length: 12 }, (_, i) => i + 1);
    const freq = {};
    numbers.forEach(n => { freq[n] = 0; });

    activeData().forEach(item => {
        item.back.map(Number).forEach(n => { freq[n]++; });
    });

    charts.dltBackFreq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: numbers.map(n => (n < 10 ? '0' + n : String(n))),
            datasets: [{
                label: '出现期数',
                data: numbers.map(n => freq[n]),
                backgroundColor: '#3498db80',
                borderColor: '#3498db',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// ===== 7星彩图表 =====

// 各位号码频率统计（6位，0-9）
function renderQxcFreqChart() {
    const ctx = document.getElementById('qxcFreqChart').getContext('2d');
    const positions = ['第1位', '第2位', '第3位', '第4位', '第5位', '第6位'];
    const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#ff6b6b'];
    const datasets = [];

    for (let pos = 0; pos < 6; pos++) {
        const freq = Array(10).fill(0);
        activeData().forEach(item => {
            freq[parseInt(item.numbers[pos])]++;
        });
        datasets.push({
            label: positions[pos],
            data: freq,
            backgroundColor: colors[pos] + '80',
            borderColor: colors[pos],
            borderWidth: 1
        });
    }

    charts.qxcFreq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 和值分布（前6位）
function renderQxcSumChart() {
    const ctx = document.getElementById('qxcSumChart').getContext('2d');
    const sumFreq = {};

    activeData().forEach(item => {
        const sum = item.numbers.slice(0, 6).reduce((a, b) => a + parseInt(b), 0);
        sumFreq[sum] = (sumFreq[sum] || 0) + 1;
    });

    const labels = Object.keys(sumFreq).sort((a, b) => a - b);

    charts.qxcSum = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: labels.map(l => sumFreq[l]),
                backgroundColor: '#667eea80',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 跨度分布（前6位）
function renderQxcSpanChart() {
    const ctx = document.getElementById('qxcSpanChart').getContext('2d');
    const spanFreq = {};

    activeData().forEach(item => {
        const nums = item.numbers.slice(0, 6).map(n => parseInt(n));
        const span = Math.max(...nums) - Math.min(...nums);
        spanFreq[span] = (spanFreq[span] || 0) + 1;
    });

    const labels = Object.keys(spanFreq).sort((a, b) => a - b);

    charts.qxcSpan = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: labels.map(l => spanFreq[l]),
                backgroundColor: '#43e97b80',
                borderColor: '#43e97b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 特别号频率统计（0-14）
function renderQxcSpecialFreqChart() {
    const ctx = document.getElementById('qxcSpecialFreqChart').getContext('2d');
    const numbers = Array.from({ length: 15 }, (_, i) => i);
    const freq = {};
    numbers.forEach(n => { freq[n] = 0; });

    activeData().forEach(item => {
        freq[parseInt(item.numbers[6])]++;
    });

    charts.qxcSpecialFreq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: numbers.map(String),
            datasets: [{
                label: '出现期数',
                data: numbers.map(n => freq[n]),
                backgroundColor: '#f39c1280',
                borderColor: '#f39c12',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 7星彩遗漏值（前6位 0-9 / 特别号 0-14）
function renderQxcOmitValues() {
    const grid = document.getElementById('omitGrid');
    const data = activeData();
    const digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    const specials = Array.from({ length: 15 }, (_, i) => i);
    const positions = ['第1位', '第2位', '第3位', '第4位', '第5位', '第6位'];

    let html = '';
    for (let pos = 0; pos < 6; pos++) {
        const omitValues = calcOmitValues(data, digits, item => [parseInt(item.numbers[pos])]);
        html += `<div class="omit-position">
            <h4>${positions[pos]}</h4>
            <div class="omit-balls">${omitBallsHtml(omitValues, digits)}</div>
        </div>`;
    }

    const specialOmit = calcOmitValues(data, specials, item => [parseInt(item.numbers[6])]);
    html += `<div class="omit-position">
        <h4>特别号 (0-14)</h4>
        <div class="omit-balls">${omitBallsHtml(specialOmit, specials)}</div>
    </div>`;

    grid.innerHTML = html;
}

// ===== 双色球 =====

// 渲染双色球表格（6红 + 1蓝）
function renderSsqTable() {
    const tbody = document.getElementById('ssqTableBody');
    const pageData = currentPageData();

    tbody.innerHTML = pageData.map(item => {
        const front = item.front.map(n => parseInt(n));
        const sum = front.reduce((a, b) => a + b, 0);
        const span = Math.max(...front) - Math.min(...front);
        const frontBalls = item.front.map(n => `<span class="ssq-front-ball">${n}</span>`).join('');
        const backBall = `<span class="ssq-back-ball">${item.back[0]}</span>`;

        return `<tr>
            <td>${item.issue_no}</td>
            <td>${item.date}</td>
            <td colspan="6" class="ssq-front-cell"><div class="ssq-group">${frontBalls}</div></td>
            <td class="ssq-back-cell"><div class="ssq-group">+${backBall}</div></td>
            <td>${sum}</td>
            <td>${span}</td>
        </tr>`;
    }).join('');
}

// 双色球红球号码频率（01-33）
function renderSsqFrontFreqChart() {
    const ctx = document.getElementById('ssqFrontFreqChart').getContext('2d');
    const numbers = Array.from({ length: 33 }, (_, i) => i + 1);
    const freq = {};
    numbers.forEach(n => { freq[n] = 0; });

    activeData().forEach(item => {
        item.front.map(Number).forEach(n => { freq[n]++; });
    });

    charts.ssqFrontFreq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: numbers.map(n => (n < 10 ? '0' + n : String(n))),
            datasets: [{
                label: '出现期数',
                data: numbers.map(n => freq[n]),
                backgroundColor: '#ff6b6b80',
                borderColor: '#ff6b6b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 双色球红球和值分布
function renderSsqSumChart() {
    const ctx = document.getElementById('ssqSumChart').getContext('2d');
    const sumFreq = {};

    activeData().forEach(item => {
        const sum = item.front.reduce((a, b) => +a + +b, 0);
        sumFreq[sum] = (sumFreq[sum] || 0) + 1;
    });

    const labels = Object.keys(sumFreq).sort((a, b) => a - b);

    charts.ssqSum = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: labels.map(l => sumFreq[l]),
                backgroundColor: '#667eea80',
                borderColor: '#667eea',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 双色球红球跨度分布
function renderSsqSpanChart() {
    const ctx = document.getElementById('ssqSpanChart').getContext('2d');
    const spanFreq = {};

    activeData().forEach(item => {
        const nums = item.front.map(Number);
        const span = Math.max(...nums) - Math.min(...nums);
        spanFreq[span] = (spanFreq[span] || 0) + 1;
    });

    const labels = Object.keys(spanFreq).sort((a, b) => a - b);

    charts.ssqSpan = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '期数',
                data: labels.map(l => spanFreq[l]),
                backgroundColor: '#43e97b80',
                borderColor: '#43e97b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 双色球蓝球号码频率（01-16）
function renderSsqBackFreqChart() {
    const ctx = document.getElementById('ssqBackFreqChart').getContext('2d');
    const numbers = Array.from({ length: 16 }, (_, i) => i + 1);
    const freq = {};
    numbers.forEach(n => { freq[n] = 0; });

    activeData().forEach(item => {
        freq[parseInt(item.back[0])]++;
    });

    charts.ssqBackFreq = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: numbers.map(n => (n < 10 ? '0' + n : String(n))),
            datasets: [{
                label: '出现期数',
                data: numbers.map(n => freq[n]),
                backgroundColor: '#3498db80',
                borderColor: '#3498db',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// 双色球遗漏值（红球 01-33 / 蓝球 01-16）
function renderSsqOmitValues() {
    const grid = document.getElementById('omitGrid');
    const data = activeData();
    const pad2 = n => (n < 10 ? '0' + n : String(n));
    const range = (from, to) => Array.from({ length: to - from + 1 }, (_, i) => from + i);

    const frontNumbers = range(1, 33);
    const backNumbers = range(1, 16);

    const frontOmit = calcOmitValues(data, frontNumbers, item => item.front.map(Number));
    const backOmit = calcOmitValues(data, backNumbers, item => item.back.map(Number));

    grid.innerHTML = `<div class="omit-position">
            <h4>红球 (01-33)</h4>
            <div class="omit-balls">${omitBallsHtml(frontOmit, frontNumbers, pad2)}</div>
        </div>
        <div class="omit-position">
            <h4>蓝球 (01-16)</h4>
            <div class="omit-balls">${omitBallsHtml(backOmit, backNumbers, pad2)}</div>
        </div>`;
}
