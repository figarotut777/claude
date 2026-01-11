// WB Analytics - JavaScript

let currentPeriod = 'month';
let allProducts = [];
let currentSort = { column: 'profit_net', direction: 'desc' };

// Форматирование чисел
function formatNumber(num) {
    if (!num && num !== 0) return '-';
    return new Intl.NumberFormat('ru-RU').format(Math.round(num));
}

function formatCurrency(num) {
    if (!num && num !== 0) return '-';
    return formatNumber(num) + ' ₽';
}

function formatPercent(num) {
    if (!num && num !== 0) return '-';
    return num.toFixed(1) + '%';
}

// Получение URL фото товара из WB
function getWBPhotoURL(nmId) {
    if (!nmId) return '';

    const nmIdStr = String(nmId);
    const vol = Math.floor(nmId / 100000);
    const part = Math.floor(nmId / 1000);

    // Определение корзины (basket номер от 01 до 16)
    const basket = String((nmId % 16) + 1).padStart(2, '0');

    return `https://basket-${basket}.wbbasket.ru/vol${vol}/part${part}/${nmId}/images/c246x328/1.jpg`;
}

// Загрузка данных
async function loadData(period = 'month', customStart = null, customEnd = null) {
    try {
        let url = `/api/dashboard?period=${period}`;

        if (period === 'custom' && customStart && customEnd) {
            url += `&start=${customStart}&end=${customEnd}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.products_summary) {
            allProducts = data.products_summary;
            renderProducts(allProducts);
        }

        // Рендер Top & Bottom SKU
        if (data.top_blocks) {
            renderTopBlocks(data.top_blocks);
        }

        // Обновление последней синхронизации
        if (data.sync_status && data.sync_status.last_incremental_sync) {
            const syncDate = new Date(data.sync_status.last_incremental_sync);
            document.getElementById('lastSync').textContent =
                `Обновлено: ${syncDate.toLocaleString('ru-RU')}`;
        }

    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        document.getElementById('productsTable').innerHTML = `
            <tr><td colspan="14" class="loading" style="color: #ef4444;">
                Ошибка загрузки данных. Проверьте подключение к серверу.
            </td></tr>
        `;
    }
}

// Рендер таблицы товаров
function renderProducts(products) {
    const tbody = document.getElementById('productsTable');

    if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="16" class="loading">Нет данных за выбранный период</td></tr>';
        document.getElementById('productsFooter').style.display = 'none';
        return;
    }

    // Расчет итогов
    let totals = {
        sales: 0,
        returnQty: 0,
        revenue: 0,
        commission: 0,
        logistics: 0,
        storage: 0,
        penalties: 0,
        ads: 0,
        returns: 0,
        other: 0,
        cogs: 0,
        tax: 0,
        profit: 0
    };

    tbody.innerHTML = products.map(product => {
        const profit = product.profit_net || 0;
        const profitClass = profit >= 0 ? 'profit-positive' : 'profit-negative';
        const roi = product.roi !== null ? formatPercent(product.roi) : '<span style="color: #888;">N/A</span>';
        const sales = product.sales_qty || 0;
        const returnQty = product.return_qty || 0;
        const returnPercent = product.return_percent || 0;

        // Суммирование
        totals.sales += sales;
        totals.returnQty += returnQty;
        totals.revenue += product.revenue_gross || 0;
        totals.commission += product.commission || 0;
        totals.logistics += product.logistics || 0;
        totals.storage += product.storage || 0;
        totals.penalties += product.penalties || 0;
        totals.ads += product.ads || 0;
        totals.returns += product.returns || 0;
        totals.other += product.other || 0;
        totals.cogs += product.cogs || 0;
        totals.tax += product.tax || 0;
        totals.profit += profit;

        return `
            <tr>
                <td class="col-article">${product.article || '-'}</td>
                <td class="col-number">${formatNumber(sales)}</td>
                <td class="col-number">${formatNumber(returnQty)}</td>
                <td class="col-number">${formatPercent(returnPercent)}</td>
                <td class="col-number">${formatCurrency(product.revenue_gross)}</td>
                <td class="col-number">${formatCurrency(product.commission)}</td>
                <td class="col-number">${formatCurrency(product.logistics)}</td>
                <td class="col-number">${formatCurrency(product.storage)}</td>
                <td class="col-number">${formatCurrency(product.penalties)}</td>
                <td class="col-number">${formatCurrency(product.ads)}</td>
                <td class="col-number">${formatCurrency(product.returns)}</td>
                <td class="col-number">${formatCurrency(product.other)}</td>
                <td class="col-number">${formatCurrency(product.cogs)}</td>
                <td class="col-number">${formatCurrency(product.tax)}</td>
                <td class="col-number ${profitClass}">${formatCurrency(profit)}</td>
                <td class="col-number">${roi}</td>
            </tr>
        `;
    }).join('');

    // Обновление строки итогов
    const totalProfitClass = totals.profit >= 0 ? 'profit-positive' : 'profit-negative';
    document.getElementById('totalSales').textContent = formatNumber(totals.sales);
    document.getElementById('totalReturnQty').textContent = formatNumber(totals.returnQty);
    document.getElementById('totalRevenue').textContent = formatCurrency(totals.revenue);
    document.getElementById('totalCommission').textContent = formatCurrency(totals.commission);
    document.getElementById('totalLogistics').textContent = formatCurrency(totals.logistics);
    document.getElementById('totalStorage').textContent = formatCurrency(totals.storage);
    document.getElementById('totalPenalties').textContent = formatCurrency(totals.penalties);
    document.getElementById('totalAds').textContent = formatCurrency(totals.ads);
    document.getElementById('totalReturns').textContent = formatCurrency(totals.returns);
    document.getElementById('totalOther').textContent = formatCurrency(totals.other);
    document.getElementById('totalCogs').textContent = formatCurrency(totals.cogs);
    document.getElementById('totalTax').textContent = formatCurrency(totals.tax);

    const totalProfitCell = document.getElementById('totalProfit');
    totalProfitCell.textContent = formatCurrency(totals.profit);
    totalProfitCell.className = `col-number profit-col ${totalProfitClass}`;

    document.getElementById('productsFooter').style.display = 'table-footer-group';
}

// Поиск по таблице
function setupSearch() {
    const searchInput = document.getElementById('searchInput');

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();

        if (!query) {
            renderProducts(allProducts);
            return;
        }

        const filtered = allProducts.filter(product => {
            const article = (product.article || '').toLowerCase();
            const name = (product.name || '').toLowerCase();
            return article.includes(query) || name.includes(query);
        });

        renderProducts(filtered);
    });
}

// Обработка фильтров периодов
function setupPeriodFilters() {
    const tabs = document.querySelectorAll('.period-tab');
    const customDateRange = document.getElementById('customDateRange');
    const applyCustomBtn = document.getElementById('applyCustom');
    const btnCustomPeriod = document.getElementById('btnCustomPeriod');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const period = tab.dataset.period;

            // Удаление active со всех табов
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            if (period === 'custom') {
                customDateRange.style.display = 'flex';
            } else {
                customDateRange.style.display = 'none';
                currentPeriod = period;
                loadData(period);
            }
        });
    });

    // Применение custom периода
    applyCustomBtn.addEventListener('click', () => {
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;

        if (!dateFrom || !dateTo) {
            alert('Выберите обе даты');
            return;
        }

        currentPeriod = 'custom';
        loadData('custom', dateFrom, dateTo);
    });
}

// Рендер Top & Bottom SKU
function renderTopBlocks(topBlocks) {
    if (!topBlocks) return;

    renderTopList('topProfit', topBlocks.top_profit, 'profit');
    renderTopList('topRevenue', topBlocks.top_revenue, 'revenue');
    renderTopList('worstProfit', topBlocks.worst_profit, 'profit');
    renderTopList('fastestChange', topBlocks.fastest_change, 'change');
}

function renderTopList(elementId, products, valueType) {
    const container = document.getElementById(elementId);

    if (!container) return;

    if (!products || products.length === 0) {
        container.innerHTML = '<div class="loading-small">Нет данных</div>';
        return;
    }

    container.innerHTML = products.map((product, index) => {
        let valueDisplay = '';
        let valueColor = '#9ca3af';

        if (valueType === 'profit') {
            const profit = product.profit_net || 0;
            valueColor = profit >= 0 ? '#10b981' : '#ef4444';
            valueDisplay = formatCurrency(profit);
        } else if (valueType === 'revenue') {
            valueDisplay = formatCurrency(product.revenue_gross || 0);
            valueColor = '#10b981';
        } else if (valueType === 'change') {
            const change = product.profit_change_percent || 0;
            valueColor = change >= 0 ? '#10b981' : '#ef4444';
            valueDisplay = (change >= 0 ? '+' : '') + formatPercent(Math.abs(change));
        }

        const articleName = product.article || product.name || '-';
        const subtitle = [product.brand, product.subject].filter(Boolean).join(' | ') || '-';

        return `
            <div class="top-item">
                <span class="top-rank">${index + 1}</span>
                <div class="top-info">
                    <strong>${articleName}</strong>
                    <small>${subtitle}</small>
                </div>
                <div class="top-value">
                    <span style="color: ${valueColor};">${valueDisplay}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Сортировка товаров
function sortProducts(column) {
    // Меняем направление сортировки если кликнули на ту же колонку
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'desc';
    }

    // Сортируем
    allProducts.sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];

        // Обработка null/undefined
        if (aVal === null || aVal === undefined) aVal = currentSort.direction === 'asc' ? Infinity : -Infinity;
        if (bVal === null || bVal === undefined) bVal = currentSort.direction === 'asc' ? Infinity : -Infinity;

        // Для строк (артикул)
        if (typeof aVal === 'string') {
            return currentSort.direction === 'asc'
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal);
        }

        // Для чисел
        return currentSort.direction === 'asc' ? aVal - bVal : bVal - aVal;
    });

    renderProducts(allProducts);
    updateSortIndicators();
}

// Обновление индикаторов сортировки в заголовках
function updateSortIndicators() {
    // Удаляем все старые индикаторы
    document.querySelectorAll('.products-table th').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
    });

    // Добавляем новый индикатор
    const columnMap = {
        'article': 0,
        'sales_qty': 1,
        'return_qty': 2,
        'return_percent': 3,
        'revenue_gross': 4,
        'commission': 5,
        'logistics': 6,
        'storage': 7,
        'penalties': 8,
        'ads': 9,
        'returns': 10,
        'other': 11,
        'cogs': 12,
        'tax': 13,
        'profit_net': 14,
        'roi': 15
    };

    const thIndex = columnMap[currentSort.column];
    if (thIndex !== undefined) {
        const th = document.querySelectorAll('.products-table thead th')[thIndex];
        if (th) {
            th.classList.add(currentSort.direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    }
}

// Настройка кликов по заголовкам для сортировки
function setupTableSorting() {
    const headers = document.querySelectorAll('.products-table thead th');
    const columnNames = ['article', 'sales_qty', 'return_qty', 'return_percent', 'revenue_gross', 'commission', 'logistics',
                        'storage', 'penalties', 'ads', 'returns', 'other', 'cogs', 'tax', 'profit_net', 'roi'];

    headers.forEach((header, index) => {
        if (columnNames[index]) {
            header.style.cursor = 'pointer';
            header.title = 'Кликните для сортировки';
            header.addEventListener('click', () => {
                sortProducts(columnNames[index]);
            });
        }
    });
}

// Обработка изменения налога
async function setupTaxSelector() {
    const taxSelect = document.getElementById('taxRate');

    // Загрузка сохранённого налога из settings
    try {
        const response = await fetch('/api/settings');
        if (response.ok) {
            const settings = await response.json();
            if (settings.tax_rate !== undefined) {
                taxSelect.value = settings.tax_rate;
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки настроек налога:', error);
    }

    // Обработка изменения налога
    taxSelect.addEventListener('change', async (e) => {
        const taxRate = parseFloat(e.target.value);

        // Сохранение в БД
        try {
            const response = await fetch('/api/settings', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tax_rate: taxRate })
            });

            if (response.ok) {
                // Перезагрузка данных с новым налогом
                loadData(currentPeriod);
            }
        } catch (error) {
            console.error('Ошибка сохранения налога:', error);
        }
    });
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    setupPeriodFilters();
    setupSearch();
    setupTaxSelector();
    setupTableSorting();
    loadData(currentPeriod);
});
