// Wildberries Analytics Dashboard JavaScript

// Конфигурация
const API_BASE_URL = '';
let currentPeriod = 'month'; // Изменено с 'today' на 'month' для отображения всех данных

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initSidebarNavigation();
    initPeriodSelector();
    loadDashboard();

    // Автообновление каждые 5 минут
    setInterval(loadDashboard, 5 * 60 * 1000);
});

// Инициализация навигации в боковом меню
function initSidebarNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();

            // Снятие активного класса со всех пунктов меню
            navItems.forEach(nav => nav.classList.remove('active'));

            // Установка активного класса на выбранный пункт
            this.classList.add('active');

            // Получение секции для показа
            const sectionId = this.dataset.section;
            showSection(sectionId);
        });
    });
}

// Показ выбранной секции
function showSection(sectionId) {
    // Скрытие всех секций
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));

    // Показ выбранной секции
    const targetSection = document.getElementById(`section-${sectionId}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Загрузка данных для секции
    if (sectionId === 'dashboard') {
        loadDashboard();
    } else if (sectionId === 'finances') {
        loadFinances();
    } else if (sectionId === 'products') {
        loadProducts();
    } else if (sectionId === 'expenses') {
        loadExpenses();
    }
}

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
            url += `&custom_start=${customStart}T00:00:00Z&custom_end=${customEnd}T23:59:59Z`;
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
    const expenses = metrics.expenses || {};
    const trends = metrics.trends || {};

    // Баланс WB (к выплате)
    document.getElementById('wbBalance').textContent = formatCurrency(sales.to_pay_from_wb || 0);

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

    // Расходы WB
    document.getElementById('expenseCommission').textContent =
        formatCurrency(expenses.commission || 0);
    document.getElementById('expenseLogistics').textContent =
        formatCurrency(expenses.logistics || 0);
    document.getElementById('expenseStorage').textContent =
        formatCurrency(expenses.storage || 0);
    document.getElementById('expensePenalties').textContent =
        formatCurrency(expenses.penalties || 0);

    // К выплате от WB
    document.getElementById('toPayFromWB').textContent =
        formatCurrency(sales.to_pay_from_wb || 0);
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
        tbody.innerHTML = '<tr><td colspan="10" class="loading">Нет данных</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => {
        const imageUrl = product.image_url || `https://via.placeholder.com/100x100?text=No+Image`;
        return `
        <tr>
            <td><img src="${imageUrl}" alt="${escapeHtml(product.name || '')}" class="product-thumbnail" onerror="this.src='https://via.placeholder.com/100x100?text=No+Image'"></td>
            <td>${escapeHtml(product.name || '-')}</td>
            <td>${escapeHtml(product.article || '-')}</td>
            <td>${escapeHtml(product.brand || '-')}</td>
            <td>${product.nm_id || '-'}</td>
            <td>${formatNumber(product.sales_qty_30d || 0)}</td>
            <td><strong>${formatCurrency(product.revenue_30d || 0)}</strong></td>
            <td>${formatNumber(product.stock_qty || 0)}</td>
            <td>${formatCurrency(product.cost_price || 0)}</td>
            <td>${formatPercent(product.wb_commission || 0)}</td>
        </tr>
        `;
    }).join('');
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

// Загрузка раздела "Финансы" (P&L)
async function loadFinances() {
    try {
        showLoading();

        let url = `${API_BASE_URL}/api/dashboard?period=${currentPeriod}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const metrics = data.metrics;

        // Обновление P&L таблицы
        updatePLTable(metrics);

        // Обновление прибыльности по товарам
        updateProductProfitTable(data.products_summary, metrics);

        // Обновление времени
        document.getElementById('lastUpdateFinances').textContent =
            `Обновлено: ${formatDateTime(new Date())}`;

    } catch (error) {
        console.error('Ошибка загрузки финансов:', error);
        showError('Не удалось загрузить финансовые данные');
    }
}

// Обновление P&L таблицы
function updatePLTable(metrics) {
    const tbody = document.getElementById('plTable');

    if (!metrics) {
        tbody.innerHTML = '<tr><td colspan="3" class="loading">Нет данных</td></tr>';
        return;
    }

    const sales = metrics.sales || {};
    const expenses = metrics.expenses || {};
    const profit = metrics.profit || {};

    const revenue = sales.revenue || 0;
    const commission = expenses.commission || 0;
    const logistics = expenses.logistics || 0;
    const storage = expenses.storage || 0;
    const penalties = expenses.penalties || 0;
    const totalWBExpenses = expenses.total_wb_expenses || 0;
    const costOfGoods = expenses.cost_of_goods || 0;
    const netProfit = profit.net_profit || 0;

    tbody.innerHTML = `
        <tr style="background: #f9fafb; font-weight: 600;">
            <td>💰 Выручка</td>
            <td style="text-align: right;">${formatCurrency(revenue)}</td>
            <td style="text-align: right;">100.0%</td>
        </tr>
        <tr>
            <td style="padding-left: 30px;">Минус: Комиссия WB</td>
            <td style="text-align: right; color: var(--danger-color);">-${formatCurrency(commission)}</td>
            <td style="text-align: right;">${formatPercent((commission / revenue * 100) || 0)}</td>
        </tr>
        <tr>
            <td style="padding-left: 30px;">Минус: Логистика</td>
            <td style="text-align: right; color: var(--danger-color);">-${formatCurrency(logistics)}</td>
            <td style="text-align: right;">${formatPercent((logistics / revenue * 100) || 0)}</td>
        </tr>
        <tr>
            <td style="padding-left: 30px;">Минус: Хранение</td>
            <td style="text-align: right; color: var(--danger-color);">-${formatCurrency(storage)}</td>
            <td style="text-align: right;">${formatPercent((storage / revenue * 100) || 0)}</td>
        </tr>
        <tr>
            <td style="padding-left: 30px;">Минус: Штрафы</td>
            <td style="text-align: right; color: var(--danger-color);">-${formatCurrency(penalties)}</td>
            <td style="text-align: right;">${formatPercent((penalties / revenue * 100) || 0)}</td>
        </tr>
        <tr style="background: #fff7ed; font-weight: 600;">
            <td>📊 Итого расходов WB</td>
            <td style="text-align: right; color: var(--warning-color);">-${formatCurrency(totalWBExpenses)}</td>
            <td style="text-align: right;">${formatPercent((totalWBExpenses / revenue * 100) || 0)}</td>
        </tr>
        <tr>
            <td>💳 К выплате от WB</td>
            <td style="text-align: right; color: var(--success-color);">${formatCurrency(sales.to_pay_from_wb || 0)}</td>
            <td style="text-align: right;">${formatPercent(((sales.to_pay_from_wb || 0) / revenue * 100) || 0)}</td>
        </tr>
        <tr>
            <td style="padding-left: 30px;">Минус: Себестоимость</td>
            <td style="text-align: right; color: var(--danger-color);">-${formatCurrency(costOfGoods)}</td>
            <td style="text-align: right;">${formatPercent((costOfGoods / revenue * 100) || 0)}</td>
        </tr>
        <tr style="background: ${netProfit >= 0 ? '#d1fae5' : '#fee2e2'}; font-weight: 700; font-size: 16px;">
            <td>✨ Чистая прибыль</td>
            <td style="text-align: right; color: ${netProfit >= 0 ? 'var(--success-color)' : 'var(--danger-color)'};">${formatCurrency(netProfit)}</td>
            <td style="text-align: right;">${formatPercent(profit.margin_percent || 0)}</td>
        </tr>
    `;
}

// Обновление таблицы прибыльности по товарам
function updateProductProfitTable(products, metrics) {
    const tbody = document.getElementById('productProfitTable');

    if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Нет данных</td></tr>';
        return;
    }

    // Заглушка - нужно будет получить детализацию с бэкенда
    tbody.innerHTML = '<tr><td colspan="7" class="loading">Детализация по товарам в разработке</td></tr>';
}

// Загрузка раздела "Товары"
async function loadProducts() {
    try {
        showLoading();

        let url = `${API_BASE_URL}/api/dashboard?period=month`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Обновление таблицы товаров в секции "Товары"
        const tbody = document.querySelector('#allProductsTableProducts');

        if (!data.products_summary || data.products_summary.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="loading">Нет данных</td></tr>';
        } else {
            tbody.innerHTML = data.products_summary.map(product => {
                const imageUrl = product.image_url || `https://via.placeholder.com/100x100?text=No+Image`;
                return `
                <tr>
                    <td><img src="${imageUrl}" alt="${escapeHtml(product.name || '')}" class="product-thumbnail" onerror="this.src='https://via.placeholder.com/100x100?text=No+Image'"></td>
                    <td>${escapeHtml(product.name || '-')}</td>
                    <td>${escapeHtml(product.article || '-')}</td>
                    <td>${escapeHtml(product.brand || '-')}</td>
                    <td>${product.nm_id || '-'}</td>
                    <td>${formatNumber(product.sales_qty_30d || 0)}</td>
                    <td><strong>${formatCurrency(product.revenue_30d || 0)}</strong></td>
                    <td>${formatNumber(product.stock_qty || 0)}</td>
                    <td>${formatCurrency(product.cost_price || 0)}</td>
                    <td>${formatPercent(product.wb_commission || 0)}</td>
                </tr>
                `;
            }).join('');
        }

        // Обновление времени
        document.getElementById('lastUpdateProducts').textContent =
            `Обновлено: ${formatDateTime(new Date())}`;

    } catch (error) {
        console.error('Ошибка загрузки товаров:', error);
        showError('Не удалось загрузить данные товаров');
    }
}

// Загрузка раздела "Расходы"
async function loadExpenses() {
    try {
        showLoading();

        let url = `${API_BASE_URL}/api/dashboard?period=${currentPeriod}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const metrics = data.metrics;
        const expenses = metrics.expenses || {};

        // Обновление карточек расходов
        document.getElementById('expenseCommissionDetails').textContent =
            formatCurrency(expenses.commission || 0);
        document.getElementById('expenseLogisticsDetails').textContent =
            formatCurrency(expenses.logistics || 0);
        document.getElementById('expenseStorageDetails').textContent =
            formatCurrency(expenses.storage || 0);
        document.getElementById('expensePenaltiesDetails').textContent =
            formatCurrency(expenses.penalties || 0);
        document.getElementById('totalWBExpenses').textContent =
            formatCurrency(expenses.total_wb_expenses || 0);
        document.getElementById('costOfGoods').textContent =
            formatCurrency(expenses.cost_of_goods || 0);

        // Обновление таблицы расходов по товарам
        const tbody = document.getElementById('productExpensesTable');
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Детализация расходов по товарам в разработке</td></tr>';

        // Обновление времени
        document.getElementById('lastUpdateExpenses').textContent =
            `Обновлено: ${formatDateTime(new Date())}`;

    } catch (error) {
        console.error('Ошибка загрузки расходов:', error);
        showError('Не удалось загрузить данные расходов');
    }
}
