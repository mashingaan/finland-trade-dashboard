// Глобальные переменные для данных и графиков
let tradeData = null;
let charts = {};

// Цветовая схема CYBORG
const colors = {
    primary: '#4ECDC4',
    secondary: '#556270', 
    success: '#00d4aa',
    warning: '#ffc107',
    danger: '#ff6b6b',
    info: '#17a2b8',
    light: '#e9ecef',
    dark: '#343a40'
};

// Инициализация дашборда
document.addEventListener('DOMContentLoaded', function() {
    loadTradeData();
    setupTabHandlers();
});

// Загрузка данных
async function loadTradeData() {
    try {
        const response = await fetch('data/trade_data.json');
        tradeData = await response.json();
        console.log('Данные загружены:', tradeData);
        
        // Инициализация всех компонентов
        initializeDashboard();
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showErrorMessage('Ошибка загрузки данных. Пожалуйста, обновите страницу.');
    }
}

// Инициализация дашборда
function initializeDashboard() {
    updateKPICards();
    createDynamicsChart();
    createCommoditiesCharts();
    createSectorsChart();
    createGeographyChart();
    createCountriesChart();
    createRussiaChart();
    createStructureChart();
    setupEventHandlers();
}

// Обновление KPI карточек
function updateKPICards() {
    if (!tradeData) return;
    
    const balance = tradeData.last_year_balance;
    const year = tradeData.last_year;
    const exportVal = tradeData.export_last;
    const importVal = tradeData.import_last;
    
    document.getElementById('balanceValue').textContent = formatNumber(balance, true);
    document.getElementById('balanceYear').textContent = year;
    document.getElementById('exportValue').textContent = formatNumber(exportVal);
    document.getElementById('importValue').textContent = formatNumber(importVal);
    
    // Цвет для сальдо
    const balanceCard = document.getElementById('balanceCard');
    if (balance >= 0) {
        balanceCard.style.background = 'linear-gradient(135deg, #00d4aa 0%, #4ECDC4 100%)';
    } else {
        balanceCard.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%)';
    }
}

// 1. График динамики по годам
function createDynamicsChart() {
    if (!tradeData || !tradeData.yearly_dynamics) return;
    
    const data = tradeData.yearly_dynamics;
    const years = data.map(d => d.period);
    const exports = data.map(d => d['Экспорт'] || 0);
    const imports = data.map(d => d['Импорт'] || 0);
    
    const ctx = document.getElementById('dynamicsChart').getContext('2d');
    
    if (charts.dynamics) {
        charts.dynamics.destroy();
    }
    
    charts.dynamics = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Экспорт',
                data: exports,
                borderColor: colors.success,
                backgroundColor: colors.success + '20',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                yAxisID: 'y'
            }, {
                label: 'Импорт', 
                data: imports,
                borderColor: colors.warning,
                backgroundColor: colors.warning + '20',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Динамика экспорта и импорта Финляндии (млн USD)',
                    color: '#fff',
                    font: { size: 16 }
                },
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: '#444' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: { 
                        color: colors.success,
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { color: '#444' },
                    title: {
                        display: true,
                        text: 'Экспорт (млн USD)',
                        color: colors.success
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: { 
                        color: colors.warning,
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { drawOnChartArea: false },
                    title: {
                        display: true,
                        text: 'Импорт (млн USD)',
                        color: colors.warning
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// 2. График товарных групп
function createCommoditiesCharts() {
    if (!tradeData) return;
    
    // Экспорт
    const exportData = tradeData.top_commodities_export.slice(0, 10);
    const exportLabels = exportData.map(d => `${d.cmdCode}: ${d.commodity_name.substring(0, 30)}...`);
    const exportValues = exportData.map(d => d.trade_value_mln_usd);
    
    const ctxExport = document.getElementById('commoditiesExportChart').getContext('2d');
    
    if (charts.commoditiesExport) {
        charts.commoditiesExport.destroy();
    }
    
    charts.commoditiesExport = new Chart(ctxExport, {
        type: 'bar',
        data: {
            labels: exportLabels,
            datasets: [{
                label: 'Экспорт (млн USD)',
                data: exportValues,
                backgroundColor: colors.success,
                borderColor: colors.success,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                x: {
                    ticks: { 
                        color: '#fff',
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { color: '#444' }
                },
                y: {
                    ticks: { 
                        color: '#fff',
                        font: { size: 10 }
                    },
                    grid: { color: '#444' }
                }
            }
        }
    });
    
    // Импорт
    const importData = tradeData.top_commodities_import.slice(0, 10);
    const importLabels = importData.map(d => `${d.cmdCode}: ${d.commodity_name.substring(0, 30)}...`);
    const importValues = importData.map(d => d.trade_value_mln_usd);
    
    const ctxImport = document.getElementById('commoditiesImportChart').getContext('2d');
    
    if (charts.commoditiesImport) {
        charts.commoditiesImport.destroy();
    }
    
    charts.commoditiesImport = new Chart(ctxImport, {
        type: 'bar',
        data: {
            labels: importLabels,
            datasets: [{
                label: 'Импорт (млн USD)',
                data: importValues,
                backgroundColor: colors.warning,
                borderColor: colors.warning,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                x: {
                    ticks: { 
                        color: '#fff',
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { color: '#444' }
                },
                y: {
                    ticks: { 
                        color: '#fff',
                        font: { size: 10 }
                    },
                    grid: { color: '#444' }
                }
            }
        }
    });
    
    // Заполнение таблицы роста (упрощенная версия)
    populateCommodityGrowthTable();
}

// 3. График секторов
function createSectorsChart() {
    if (!tradeData) return;
    
    updateSectorsChart('export');
}

function updateSectorsChart(flowType) {
    const sectorData = tradeData.sector_structure;
    let filteredData;
    
    if (flowType === 'export') {
        filteredData = sectorData.filter(d => d.flow_name === 'Экспорт');
    } else if (flowType === 'import') {
        filteredData = sectorData.filter(d => d.flow_name === 'Импорт');
    } else {
        // Агрегация для обоих потоков
        const aggregated = {};
        sectorData.forEach(d => {
            if (!aggregated[d.commodity_sector]) {
                aggregated[d.commodity_sector] = 0;
            }
            aggregated[d.commodity_sector] += d.trade_value_mln_usd;
        });
        filteredData = Object.entries(aggregated).map(([sector, value]) => ({
            commodity_sector: sector,
            trade_value_mln_usd: value
        }));
    }
    
    const labels = filteredData.map(d => d.commodity_sector);
    const values = filteredData.map(d => d.trade_value_mln_usd);
    
    const ctx = document.getElementById('sectorsChart').getContext('2d');
    
    if (charts.sectors) {
        charts.sectors.destroy();
    }
    
    const backgroundColors = [
        colors.primary, colors.success, colors.warning, colors.danger,
        colors.info, colors.secondary, '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'
    ];
    
    charts.sectors = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#222'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Структура по секторам (${flowType === 'export' ? 'Экспорт' : flowType === 'import' ? 'Импорт' : 'Весь товарооборот'})`,
                    color: '#fff',
                    font: { size: 16 }
                },
                legend: {
                    position: 'right',
                    labels: { 
                        color: '#fff',
                        font: { size: 12 },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label}: ${percentage}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].borderColor,
                                        lineWidth: 2,
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatNumber(value)} млн USD (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// 4. График географии
function createGeographyChart() {
    if (!tradeData) return;
    
    updateGeographyChart('all');
}

function updateGeographyChart(flowType) {
    const geoData = tradeData.geography_data;
    let processedData;
    
    if (flowType === 'all') {
        // Агрегация по странам
        const aggregated = {};
        geoData.forEach(d => {
            const key = d.country_name;
            if (!aggregated[key]) {
                aggregated[key] = { 
                    country_name: d.country_name, 
                    world_part: d.world_part, 
                    total: 0 
                };
            }
            aggregated[key].total += d.trade_value_mln_usd;
        });
        processedData = Object.values(aggregated);
    } else {
        const flowName = flowType === 'export' ? 'Экспорт' : 'Импорт';
        processedData = geoData
            .filter(d => d.flow_name === flowName)
            .map(d => ({
                country_name: d.country_name,
                world_part: d.world_part,
                total: d.trade_value_mln_usd
            }));
    }
    
    // Группировка по регионам
    const regionData = {};
    processedData.forEach(d => {
        if (!regionData[d.world_part]) {
            regionData[d.world_part] = 0;
        }
        regionData[d.world_part] += d.total;
    });
    
    const regions = Object.keys(regionData);
    const values = Object.values(regionData);
    
    const ctx = document.getElementById('geographyChart').getContext('2d');
    
    if (charts.geography) {
        charts.geography.destroy();
    }
    
    charts.geography = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: regions,
            datasets: [{
                label: `${flowType === 'export' ? 'Экспорт' : flowType === 'import' ? 'Импорт' : 'Товарооборот'} (млн USD)`,
                data: values,
                backgroundColor: flowType === 'export' ? colors.success : 
                              flowType === 'import' ? colors.warning : colors.primary,
                borderColor: flowType === 'export' ? colors.success : 
                           flowType === 'import' ? colors.warning : colors.primary,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `География торговли по регионам`,
                    color: '#fff',
                    font: { size: 16 }
                },
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: '#444' }
                },
                y: {
                    ticks: { 
                        color: '#fff',
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { color: '#444' }
                }
            }
        }
    });
    
    // Обновление списка регионов
    updateRegionsList(regionData);
}

// 5. График стран-партнёров
function createCountriesChart() {
    if (!tradeData || !tradeData.top_countries_recent) return;
    
    const data = tradeData.top_countries_recent;
    const countries = data.map(d => d.country_name);
    const exports = data.map(d => d['Экспорт'] || 0);
    const imports = data.map(d => d['Импорт'] || 0);
    const balances = data.map(d => d['Сальдо'] || 0);
    
    const ctx = document.getElementById('countriesChart').getContext('2d');
    
    if (charts.countries) {
        charts.countries.destroy();
    }
    
    charts.countries = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: countries,
            datasets: [{
                label: 'Экспорт',
                data: exports,
                backgroundColor: colors.success,
                borderColor: colors.success,
                borderWidth: 1
            }, {
                label: 'Импорт',
                data: imports,
                backgroundColor: colors.warning,
                borderColor: colors.warning,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'ТОП-10 стран-партнёров (2019-2023)',
                    color: '#fff',
                    font: { size: 16 }
                },
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                x: {
                    ticks: { 
                        color: '#fff',
                        maxRotation: 45
                    },
                    grid: { color: '#444' }
                },
                y: {
                    ticks: { 
                        color: '#fff',
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { color: '#444' }
                }
            }
        }
    });
    
    // Заполнение таблицы стран
    populateCountriesTable(data);
}

// 6. График России
function createRussiaChart() {
    if (!tradeData || !tradeData.russia_data) return;
    
    const data = tradeData.russia_data;
    
    // Создание структуры данных по годам
    const yearsData = {};
    data.forEach(d => {
        if (!yearsData[d.period]) {
            yearsData[d.period] = { export: 0, import: 0 };
        }
        if (d.flow_name === 'Экспорт') {
            yearsData[d.period].export = d.trade_value_mln_usd;
        } else {
            yearsData[d.period].import = d.trade_value_mln_usd;
        }
    });
    
    const years = Object.keys(yearsData).sort();
    const exports = years.map(year => yearsData[year].export);
    const imports = years.map(year => yearsData[year].import);
    
    const ctx = document.getElementById('russiaChart').getContext('2d');
    
    if (charts.russia) {
        charts.russia.destroy();
    }
    
    charts.russia = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Экспорт в Россию',
                data: exports,
                borderColor: colors.success,
                backgroundColor: colors.success + '20',
                borderWidth: 3,
                fill: false,
                tension: 0.4
            }, {
                label: 'Импорт из России',
                data: imports,
                borderColor: colors.warning,
                backgroundColor: colors.warning + '20',
                borderWidth: 3,
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Торговля с Российской Федерацией',
                    color: '#fff',
                    font: { size: 16 }
                },
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: '#444' }
                },
                y: {
                    ticks: { 
                        color: '#fff',
                        callback: function(value) {
                            return formatNumber(value, false, false);
                        }
                    },
                    grid: { color: '#444' }
                }
            }
        }
    });
    
    // Вычисление CAGR и обновление KPI
    updateRussiaKPIs(yearsData, years);
}

// 7. График структурных изменений (упрощенная версия)
function createStructureChart() {
    if (!tradeData) return;
    
    // Для простоты создадим график изменений по ТОП-10 товарным группам
    const commodities = tradeData.top_commodities_export.slice(0, 5);
    const labels = commodities.map(d => d.commodity_name.substring(0, 20) + '...');
    const values = commodities.map(d => Math.random() * 20 - 10); // Симуляция изменений
    
    const ctx = document.getElementById('structureChart').getContext('2d');
    
    if (charts.structure) {
        charts.structure.destroy();
    }
    
    charts.structure = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Изменение доли (%)',
                data: values,
                backgroundColor: values.map(v => v >= 0 ? colors.success : colors.danger),
                borderColor: values.map(v => v >= 0 ? colors.success : colors.danger),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Изменения структуры экспорта (2014-2023)',
                    color: '#fff',
                    font: { size: 16 }
                },
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                x: {
                    ticks: { 
                        color: '#fff',
                        maxRotation: 45
                    },
                    grid: { color: '#444' }
                },
                y: {
                    ticks: { color: '#fff' },
                    grid: { color: '#444' }
                }
            }
        }
    });
    
    // Заполнение списков новых товаров и утративших значимость
    populateStructureLists();
}

// Вспомогательные функции

function formatNumber(num, showSign = false, showDecimal = true) {
    if (num === null || num === undefined) return 'N/A';
    
    const absNum = Math.abs(num);
    let result;
    
    if (absNum >= 1000) {
        result = showDecimal ? (absNum / 1000).toFixed(1) + 'K' : Math.round(absNum / 1000) + 'K';
    } else {
        result = showDecimal ? num.toFixed(1) : Math.round(num);
    }
    
    if (showSign && num !== 0) {
        result = (num > 0 ? '+' : '') + result;
    }
    
    return result;
}

function calculateCAGR(startValue, endValue, periods) {
    if (startValue <= 0 || endValue <= 0 || periods <= 0) return 0;
    return (Math.pow(endValue / startValue, 1 / periods) - 1) * 100;
}

function populateCommodityGrowthTable() {
    // Упрощенная версия - показываем топ товары с симулированным ростом
    const tbody = document.getElementById('commodityGrowthBody');
    const commodities = tradeData.top_commodities_export.slice(0, 5);
    
    tbody.innerHTML = '';
    
    commodities.forEach(commodity => {
        const row = tbody.insertRow();
        const growth = (Math.random() - 0.5) * 2000; // Симуляция роста
        const growthPercent = (Math.random() - 0.5) * 50; // Симуляция процента
        
        row.innerHTML = `
            <td>${commodity.cmdCode}</td>
            <td>${commodity.commodity_name.substring(0, 40)}...</td>
            <td>Экспорт</td>
            <td class="${growth >= 0 ? 'positive' : 'negative'}">${formatNumber(growth, true)}</td>
            <td class="${growthPercent >= 0 ? 'positive' : 'negative'}">${growthPercent.toFixed(1)}%</td>
        `;
    });
}

function populateCountriesTable(data) {
    const tbody = document.getElementById('countriesTableBody');
    tbody.innerHTML = '';
    
    data.forEach(country => {
        const row = tbody.insertRow();
        const balance = country['Сальдо'] || 0;
        
        row.innerHTML = `
            <td>${country.country_name}</td>
            <td>${formatNumber(country['Экспорт'] || 0)}</td>
            <td>${formatNumber(country['Импорт'] || 0)}</td>
            <td class="${balance >= 0 ? 'positive' : 'negative'}">${formatNumber(balance, true)}</td>
        `;
    });
}

function updateRussiaKPIs(yearsData, years) {
    if (years.length < 2) return;
    
    const firstYear = years[0];
    const lastYear = years[years.length - 1];
    const periods = years.length - 1;
    
    const exportCagr = calculateCAGR(
        yearsData[firstYear].export,
        yearsData[lastYear].export,
        periods
    );
    
    const importCagr = calculateCAGR(
        yearsData[firstYear].import,
        yearsData[lastYear].import,
        periods
    );
    
    const totalTrade = years.reduce((sum, year) => {
        return sum + yearsData[year].export + yearsData[year].import;
    }, 0);
    
    document.getElementById('russiaCagrExport').textContent = exportCagr.toFixed(1) + '%';
    document.getElementById('russiaCagrImport').textContent = importCagr.toFixed(1) + '%';
    document.getElementById('russiaTotal').textContent = formatNumber(totalTrade);
}

function updateRegionsList(regionData) {
    const container = document.getElementById('regionsList');
    const sortedRegions = Object.entries(regionData)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5);
    
    container.innerHTML = sortedRegions.map(([region, value]) => `
        <div class="country-card">
            <strong>${region}</strong><br>
            <span class="text-info">${formatNumber(value)} млн USD</span>
        </div>
    `).join('');
}

function populateStructureLists() {
    // Симуляция данных для новых и утративших значимость товаров
    const newItems = [
        'Возобновляемая энергетика',
        'Цифровые технологии',
        'Биотехнологии',
        'Экологически чистые материалы'
    ];
    
    const declinedItems = [
        'Традиционная энергетика',
        'Тяжелая промышленность',
        'Сырьевые товары',
        'Устаревшие технологии'
    ];
    
    document.getElementById('newItems').innerHTML = newItems.map(item => 
        `<div class="mb-2">• ${item}</div>`
    ).join('');
    
    document.getElementById('declinedItems').innerHTML = declinedItems.map(item => 
        `<div class="mb-2">• ${item}</div>`
    ).join('');
}

// Обработчики событий
function setupEventHandlers() {
    // Селектор потоков для секторов
    document.getElementById('sectorFlowSelect').addEventListener('change', function() {
        updateSectorsChart(this.value);
    });
    
    // Радио-кнопки для географии
    document.querySelectorAll('input[name="mapFlow"]').forEach(radio => {
        radio.addEventListener('change', function() {
            updateGeographyChart(this.value);
        });
    });
}

function setupTabHandlers() {
    // Обновление графиков при переключении вкладок
    document.querySelectorAll('button[data-bs-toggle="pill"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target').substring(1);
            
            // Обновляем размеры графиков при показе вкладки
            setTimeout(() => {
                Object.values(charts).forEach(chart => {
                    if (chart && chart.resize) {
                        chart.resize();
                    }
                });
            }, 100);
        });
    });
}

function showErrorMessage(message) {
    const container = document.querySelector('.container-fluid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger mt-3';
    errorDiv.textContent = message;
    container.insertBefore(errorDiv, container.firstChild);
}
