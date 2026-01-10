// Управление себестоимостью товаров

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

// Загрузка товаров с себестоимостью
async function loadProducts() {
    try {
        const response = await fetch('/api/cost-prices');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.products) {
            allProducts = data.products;
            renderProducts(allProducts);
        }

    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        document.getElementById('costPricesTable').innerHTML = `
            <tr><td colspan="5" class="loading" style="color: #ef4444;">
                Ошибка загрузки данных. Проверьте подключение к серверу.
            </td></tr>
        `;
    }
}

// Рендер таблицы товаров
function renderProducts(products) {
    const tbody = document.getElementById('costPricesTable');

    if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Нет товаров</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => {
        const currentCost = product.cost_price || 0;

        return `
            <tr data-nm-id="${product.nm_id}">
                <td class="col-article">${product.article || '-'}</td>
                <td>${product.name || 'Без названия'}</td>
                <td class="col-number">${formatCurrency(currentCost)}</td>
                <td class="col-number">
                    <input type="number"
                           class="cost-input"
                           id="cost-${product.nm_id}"
                           value="${currentCost}"
                           min="0"
                           step="0.01"
                           placeholder="0">
                </td>
                <td>
                    <button class="btn-save" onclick="saveCostPrice(${product.nm_id})">
                        Сохранить
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Сохранение себестоимости
async function saveCostPrice(nmId) {
    const input = document.getElementById(`cost-${nmId}`);
    const costPrice = parseFloat(input.value) || 0;

    if (costPrice < 0) {
        alert('Себестоимость не может быть отрицательной');
        return;
    }

    try {
        const response = await fetch('/api/cost-prices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nm_id: nmId,
                cost_price: costPrice
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            // Показать успех
            const row = document.querySelector(`tr[data-nm-id="${nmId}"]`);
            const currentCostCell = row.querySelector('.col-number');
            currentCostCell.textContent = formatCurrency(costPrice);

            // Анимация успеха
            const btn = row.querySelector('.btn-save');
            btn.textContent = '✓ Сохранено';
            btn.style.background = '#10b981';

            setTimeout(() => {
                btn.textContent = 'Сохранить';
                btn.style.background = '';
            }, 2000);
        }

    } catch (error) {
        console.error('Ошибка сохранения:', error);
        alert('Ошибка при сохранении себестоимости');
    }
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

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    setupSearch();
    loadProducts();
});
