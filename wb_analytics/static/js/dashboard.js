// WB Analytics - JavaScript

let currentPeriod = 'month';
let allProducts = [];

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
            url += `&custom_start=${customStart}&custom_end=${customEnd}`;
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
        tbody.innerHTML = '<tr><td colspan="14" class="loading">Нет данных за выбранный период</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => {
        const photo = getWBPhotoURL(product.nm_id);
        const profit = product.profit_net || 0;
        const profitClass = profit >= 0 ? 'profit-positive' : 'profit-negative';
        const roi = product.roi !== null ? formatPercent(product.roi) : '<span style="color: #888;">N/A</span>';

        return `
            <tr>
                <td class="col-photo">
                    <img src="${photo}"
                         alt="${product.article || ''}"
                         class="product-photo"
                         onerror="this.style.display='none'">
                </td>
                <td class="col-article">${product.article || '-'}</td>
                <td class="col-name">
                    <div class="product-name">${product.name || 'Без названия'}</div>
                </td>
                <td class="col-number">${formatCurrency(product.revenue_gross)}</td>
                <td class="col-number">${formatCurrency(product.commission)}</td>
                <td class="col-number">${formatCurrency(product.logistics)}</td>
                <td class="col-number">${formatCurrency(product.storage)}</td>
                <td class="col-number">${formatCurrency(product.penalties)}</td>
                <td class="col-number">${formatCurrency(product.ads)}</td>
                <td class="col-number">${formatCurrency(product.returns)}</td>
                <td class="col-number">${formatCurrency(product.other)}</td>
                <td class="col-number">${formatCurrency(product.cogs)}</td>
                <td class="col-number ${profitClass}">${formatCurrency(profit)}</td>
                <td class="col-number">${roi}</td>
            </tr>
        `;
    }).join('');
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

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    setupPeriodFilters();
    setupSearch();
    loadData(currentPeriod);
});
