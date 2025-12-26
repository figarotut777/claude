// Wildberries Analytics Dashboard JavaScript

// Конфигурация
const API_BASE_URL = '';
let currentPeriod = 'today';

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initPeriodSelector();
    loadDashboard();

    // Автообновление каждые 5 минут
    setInterval(loadDashboard, 5 * 60 * 1000);
});

// Инициализация селектора периода
function initPeriodSelector() {
    const periodButtons = document.querySelectorAll('.period-btn');

    periodButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Снятие активного класса со всех кнопок
            periodButtons.forEach(b => b.classList.remove('active'));

            // Установка активного класса
            this.classList.add('active');

            // Сохранение периода
            currentPeriod = this.dataset.period;

            // Показ/скрытие кастомного периода
            const customPeriod = document.getElementById('customPeriod');
            if (currentPeriod === 'custom') {
                customPeriod.style.display = 'flex';
            } else {
                customPeriod.style.display = 'none';
                loadDashboard();
            }
        });
    });
}

// Применение кастомного периода
function applyCustomPeriod() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!startDate || !endDate) {
        alert('Пожалуйста, выберите начальную и конечную дату');
        return;
    }

    loadDashboard(startDate, endDate);
}

// Загрузка данных дашборда
async function loadDashboard(customStart = null, customEnd = null) {
    try {
        showLoading();

        // Формирование URL
        let url = `${API_BASE_URL}/api/dashboard?period=${currentPeriod}`;

        if (currentPeriod === 'custom' && customStart && customEnd) {
            url += `&start=${customStart}T00:00:00Z&end=${customEnd}T23:59:59Z`;
        }

        // Запрос данных
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Обновление UI
        updateMetrics(data.metrics);
        updateTopProducts(data.top_products);
        updateAllProducts(data.products_summary);
        updateSyncStatus(data.sync_status);

    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showError('Не удалось загрузить данные. Проверьте подключение к серверу.');
    }
}

// Обновление метрик
function updateMetrics(metrics) {
    if (!metrics) return;

    const sales = metrics.sales || {};
    const profit = metrics.profit || {};
    const trends = metrics.trends || {};

    // Продажи (штуки)
    document.getElementById('salesQty').textContent = formatNumber(sales.quantity || 0);
    updateTrendIndicator('salesQtyChange', trends.quantity_change_percent);

    // Выручка
    document.getElementById('salesRevenue').textContent = formatCurrency(sales.revenue || 0);
    updateTrendIndicator('salesRevenueChange', trends.revenue_change_percent);

    // Выручка после комиссии
    document.getElementById('revenueAfterCommission').textContent =
        formatCurrency(sales.revenue_after_commission || 0);

    // Чистая прибыль
    document.getElementById('netProfit').textContent = formatCurrency(profit.net_profit || 0);

    // ROI
    document.getElementById('roi').textContent = formatPercent(profit.roi || 0);

    // Средний чек
    document.getElementById('avgOrderValue').textContent =
        formatCurrency(sales.avg_order_value || 0);
}

// Обновление индикатора тренда
function updateTrendIndicator(elementId, changePercent) {
    const element = document.getElementById(elementId);

    if (changePercent === undefined || changePercent === null) {
        element.textContent = '-';
        return;
    }

    const isPositive = changePercent >= 0;
    const arrow = isPositive ? '↑' : '↓';
    const className = isPositive ? 'positive' : 'negative';

    element.textContent = `${arrow} ${Math.abs(changePercent).toFixed(1)}%`;
    element.className = `metric-change ${className}`;
}

// Обновление топ товаров
function updateTopProducts(products) {
    const tbody = document.querySelector('#topProductsTable tbody');

    if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Нет данных</td></tr>';
        return;
    }

    tbody.innerHTML = products.slice(0, 5).map((product, index) => `
        <tr>
            <td><strong>${index + 1}</strong></td>
            <td>${escapeHtml(product.article || '-')}</td>
            <td>${escapeHtml(product.name || '-')}</td>
            <td>${formatNumber(product.quantity || 0)}</td>
            <td><strong>${formatCurrency(product.revenue || 0)}</strong></td>
        </tr>
    `).join('');
}

// Обновление всех товаров
function updateAllProducts(products) {
    const tbody = document.querySelector('#allProductsTable tbody');

    if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading">Нет данных</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.nm_id || '-'}</td>
            <td>${escapeHtml(product.article || '-')}</td>
            <td>${escapeHtml(product.name || '-')}</td>
            <td>${escapeHtml(product.brand || '-')}</td>
            <td>${formatNumber(product.sales_qty_30d || 0)}</td>
            <td><strong>${formatCurrency(product.revenue_30d || 0)}</strong></td>
            <td>${formatNumber(product.stock_qty || 0)}</td>
            <td>${formatCurrency(product.cost_price || 0)}</td>
            <td>${formatPercent(product.wb_commission || 0)}</td>
        </tr>
    `).join('');
}

// Обновление статуса синхронизации
function updateSyncStatus(status) {
    if (!status) return;

    const lastUpdateElement = document.getElementById('lastUpdate');

    if (status.last_update) {
        const lastUpdate = new Date(status.last_update);
        lastUpdateElement.textContent = `Последнее обновление: ${formatDateTime(lastUpdate)}`;
    } else {
        lastUpdateElement.textContent = 'Обновление данных не выполнялось';
    }
}

// Показ индикатора загрузки
function showLoading() {
    const tables = document.querySelectorAll('tbody');
    tables.forEach(tbody => {
        tbody.innerHTML = '<tr><td colspan="10" class="loading">Загрузка...</td></tr>';
    });
}

// Показ ошибки
function showError(message) {
    alert(message);
}

// Утилиты форматирования

function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatPercent(value) {
    return `${value.toFixed(1)}%`;
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
