// 全局状态
let currentPage = 1;
let pageSize = 50;
let filteredData = [...LOTTERY_DATA].sort((a, b) => parseInt(b.issue_no) - parseInt(a.issue_no));
let charts = {};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initYearFilter();
    renderTable();
    renderCharts();
    renderOmitValues();
});

// 初始化年份筛选
function initYearFilter() {
    const years = [...new Set(LOTTERY_DATA.map(d => d.issue_no.substring(0, 2)))].sort();
    const select = document.getElementById('yearFilter');
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = '20' + year + '年';
        select.appendChild(option);
    });
}

// 渲染表格
function renderTable() {
    const tbody = document.getElementById('tableBody');
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageData = filteredData.slice(start, end);

    tbody.innerHTML = pageData.map(item => {
        const nums = item.numbers.map(n => parseInt(n));
        const sum = nums.reduce((a, b) => a + b, 0);
        const span = Math.max(...nums) - Math.min(...nums);
        // 前三位用 pl3-ball（排列3数据），后两位用 pl5-ball
        const pl3Balls = nums.slice(0, 3).map(n => `<span class="pl3-ball">${n}</span>`).join('');
        const pl5Balls = nums.slice(3).map(n => `<span class="pl5-ball">${n}</span>`).join('');
        
        return `<tr>
            <td>${item.issue_no}</td>
            <td>${item.date}</td>
            <td colspan="3" class="pl3-cell"><div class="pl3-group">${pl3Balls}</div></td>
            <td colspan="2" class="pl5-cell"><div class="pl5-group">${pl5Balls}</div></td>
            <td>${sum}</td>
            <td>${span}</td>
        </tr>`;
    }).join('');

    const totalPages = Math.ceil(filteredData.length / pageSize);
    document.getElementById('pageInfo').textContent = 
        `第 ${currentPage} 页 / 共 ${totalPages} 页 (共 ${filteredData.length} 条)`;
}

// 搜索
function searchData() {
    const query = document.getElementById('searchInput').value.trim();
    if (query) {
        filteredData = LOTTERY_DATA.filter(d => d.issue_no.includes(query));
    } else {
        filteredData = [...LOTTERY_DATA];
    }
    filteredData.sort((a, b) => parseInt(b.issue_no) - parseInt(a.issue_no));
    currentPage = 1;
    renderTable();
}

// 年份筛选
function filterByYear() {
    const year = document.getElementById('yearFilter').value;
    if (year) {
        filteredData = LOTTERY_DATA.filter(d => d.issue_no.startsWith(year));
    } else {
        filteredData = [...LOTTERY_DATA];
    }
    filteredData.sort((a, b) => parseInt(b.issue_no) - parseInt(a.issue_no));
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
    renderFreqChart();
    renderSumChart();
    renderSpanChart();
    renderHotColdChart();
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
        LOTTERY_DATA.forEach(item => {
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
    
    LOTTERY_DATA.forEach(item => {
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
    
    LOTTERY_DATA.forEach(item => {
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
    const recentData = LOTTERY_DATA.slice(-30);
    
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

// 渲染遗漏值
function renderOmitValues() {
    const grid = document.getElementById('omitGrid');
    const positions = ['万位', '千位', '百位', '十位', '个位'];
    
    let html = '';
    for (let pos = 0; pos < 5; pos++) {
        // 计算每个号码的遗漏值
        const lastAppear = Array(10).fill(-1);
        const omitValues = Array(10).fill(0);
        
        for (let i = 0; i < LOTTERY_DATA.length; i++) {
            const num = parseInt(LOTTERY_DATA[i].numbers[pos]);
            lastAppear[num] = i;
        }
        
        const total = LOTTERY_DATA.length;
        for (let num = 0; num < 10; num++) {
            if (lastAppear[num] >= 0) {
                omitValues[num] = total - 1 - lastAppear[num];
            } else {
                omitValues[num] = total;
            }
        }
        
        // 分类遗漏值
        const maxOmit = Math.max(...omitValues);
        const minOmit = Math.min(...omitValues);
        const threshold = (maxOmit - minOmit) / 3;
        
        let ballsHtml = '';
        for (let num = 0; num < 10; num++) {
            let className = 'cold';
            if (omitValues[num] > maxOmit - threshold) className = 'hot';
            else if (omitValues[num] > minOmit + threshold) className = 'warm';
            
            ballsHtml += `<div class="omit-ball ${className}" title="遗漏${omitValues[num]}期">${num}<br><small>${omitValues[num]}</small></div>`;
        }
        
        html += `<div class="omit-position">
            <h4>${positions[pos]}</h4>
            <div class="omit-balls">${ballsHtml}</div>
        </div>`;
    }
    
    grid.innerHTML = html;
}
