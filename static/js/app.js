// Application Multi-Orchestrator-Bot
class TradingApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.strategies = [];
        this.trades = [];
        this.marketData = [];
        this.dashboardData = {};

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.checkAPIHealth();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = e.target.dataset.page;
                this.switchPage(page);
            });
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshCurrentPage();
        });

        // Strategy modal
        document.getElementById('add-strategy-btn').addEventListener('click', () => {
            this.openStrategyModal();
        });

        // Trade modal
        document.getElementById('add-trade-btn').addEventListener('click', () => {
            this.openTradeModal();
        });

        // Market refresh
        document.getElementById('refresh-market-btn').addEventListener('click', () => {
            this.loadMarketData();
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });

        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        });

        // Forms
        document.getElementById('strategy-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveStrategy();
        });

        document.getElementById('trade-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveTrade();
        });
    }

    switchPage(page) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // Update pages
        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
        });
        document.getElementById(`${page}-page`).classList.add('active');

        this.currentPage = page;

        // Load page data
        switch (page) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'strategies':
                this.loadStrategies();
                break;
            case 'trades':
                this.loadTrades();
                break;
            case 'market':
                this.loadMarketData();
                break;
        }
    }

    refreshCurrentPage() {
        this.switchPage(this.currentPage);
    }

    async apiRequest(endpoint, options = {}) {
        const url = `/api${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            this.showError(`Erreur API: ${error.message}`);
            throw error;
        }
    }

    async checkAPIHealth() {
        try {
            const data = await this.apiRequest('/health');
            document.getElementById('api-status').textContent = '✓ API OK';
            document.getElementById('api-status').className = 'stat-value status-healthy';
        } catch (error) {
            document.getElementById('api-status').textContent = '✗ API HS';
            document.getElementById('api-status').className = 'stat-value';
            document.getElementById('api-status').style.color = '#dc2626';
        }
    }

    async loadDashboard() {
        try {
            const data = await this.apiRequest('/dashboard/summary');
            this.dashboardData = data;

            document.getElementById('total-pnl').textContent = `$${data.total_pnl.toFixed(2)}`;
            document.getElementById('open-positions').textContent = data.open_positions;
            document.getElementById('active-strategies').textContent = data.active_strategies;
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    async loadStrategies() {
        try {
            this.strategies = await this.apiRequest('/strategies');
            this.renderStrategies();
        } catch (error) {
            console.error('Failed to load strategies:', error);
        }
    }

    async loadTrades() {
        try {
            this.trades = await this.apiRequest('/trades');
            this.renderTrades();
        } catch (error) {
            console.error('Failed to load trades:', error);
        }
    }

    async loadMarketData() {
        try {
            this.marketData = await this.apiRequest('/market/prices');
            this.renderMarketData();
        } catch (error) {
            console.error('Failed to load market data:', error);
        }
    }

    renderStrategies() {
        const container = document.getElementById('strategies-list');
        container.innerHTML = '';

        if (this.strategies.length === 0) {
            container.innerHTML = '<p class="empty-state">Aucune stratégie trouvée. Créez-en une nouvelle.</p>';
            return;
        }

        this.strategies.forEach(strategy => {
            const item = document.createElement('div');
            item.className = 'data-item';

            const statusClass = strategy.status === 'active' ? 'status-active' : 'status-inactive';

            item.innerHTML = `
                <div class="data-item-header">
                    <div class="data-item-title">${strategy.name}</div>
                    <div class="data-item-status ${statusClass}">${strategy.status}</div>
                </div>
                <div class="data-item-content">
                    <div class="data-field">
                        <div class="data-field-label">Type</div>
                        <div class="data-field-value">${strategy.type.toUpperCase()}</div>
                    </div>
                    <div class="data-field">
                        <div class="data-field-label">PnL Total</div>
                        <div class="data-field-value">$${strategy.performance.total_pnl?.toFixed(2) || '0.00'}</div>
                    </div>
                    <div class="data-field">
                        <div class="data-field-label">Taux de Réussite</div>
                        <div class="data-field-value">${(strategy.performance.win_rate * 100)?.toFixed(1) || '0.0'}%</div>
                    </div>
                </div>
                <div class="data-item-actions">
                    <button class="btn btn-secondary" onclick="app.toggleStrategy(${strategy.id})">
                        ${strategy.status === 'active' ? 'Désactiver' : 'Activer'}
                    </button>
                    <button class="btn btn-danger" onclick="app.deleteStrategy(${strategy.id})">
                        Supprimer
                    </button>
                </div>
            `;

            container.appendChild(item);
        });
    }

    renderTrades() {
        const container = document.getElementById('trades-list');
        container.innerHTML = '';

        if (this.trades.length === 0) {
            container.innerHTML = '<p class="empty-state">Aucun trade trouvé. Créez-en un nouveau.</p>';
            return;
        }

        this.trades.forEach(trade => {
            const item = document.createElement('div');
            item.className = 'data-item';

            const statusClass = trade.status === 'closed' ? 'status-closed' : 'status-open';

            item.innerHTML = `
                <div class="data-item-header">
                    <div class="data-item-title">${trade.symbol} - ${trade.side.toUpperCase()}</div>
                    <div class="data-item-status ${statusClass}">${trade.status}</div>
                </div>
                <div class="data-item-content">
                    <div class="data-field">
                        <div class="data-field-label">Quantité</div>
                        <div class="data-field-value">${trade.quantity}</div>
                    </div>
                    <div class="data-field">
                        <div class="data-field-label">Prix d'Entrée</div>
                        <div class="data-field-value">$${trade.entry_price.toFixed(2)}</div>
                    </div>
                    <div class="data-field">
                        <div class="data-field-label">PnL</div>
                        <div class="data-field-value">$${trade.pnl?.toFixed(2) || '0.00'}</div>
                    </div>
                    <div class="data-field">
                        <div class="data-field-label">Date</div>
                        <div class="data-field-value">${new Date(trade.created_at).toLocaleDateString()}</div>
                    </div>
                </div>
            `;

            container.appendChild(item);
        });
    }

    renderMarketData() {
        const container = document.getElementById('market-data');
        container.innerHTML = '';

        this.marketData.forEach(item => {
            const element = document.createElement('div');
            element.className = 'market-item';

            element.innerHTML = `
                <div class="market-symbol">${item.symbol}</div>
                <div class="market-price">$${item.price.toFixed(2)}</div>
                <div class="market-volume">Vol: ${(item.volume / 1000000).toFixed(1)}M</div>
            `;

            container.appendChild(element);
        });
    }

    openStrategyModal(strategy = null) {
        const modal = document.getElementById('strategy-modal');
        const form = document.getElementById('strategy-form');
        const title = document.getElementById('strategy-modal-title');

        if (strategy) {
            title.textContent = 'Modifier Stratégie';
            document.getElementById('strategy-name').value = strategy.name;
            document.getElementById('strategy-description').value = strategy.description;
            document.getElementById('strategy-type').value = strategy.type;
        } else {
            title.textContent = 'Nouvelle Stratégie';
            form.reset();
        }

        modal.classList.add('active');
    }

    openTradeModal() {
        const modal = document.getElementById('trade-modal');
        const form = document.getElementById('trade-form');
        form.reset();
        modal.classList.add('active');
    }

    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    async saveStrategy() {
        const formData = new FormData(document.getElementById('strategy-form'));
        const data = {
            name: document.getElementById('strategy-name').value,
            description: document.getElementById('strategy-description').value,
            type: document.getElementById('strategy-type').value,
        };

        try {
            await this.apiRequest('/strategies', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            this.closeModal();
            this.loadStrategies();
            this.showSuccess('Stratégie créée avec succès');
        } catch (error) {
            this.showError('Erreur lors de la création de la stratégie');
        }
    }

    async saveTrade() {
        const data = {
            symbol: document.getElementById('trade-symbol').value,
            side: document.getElementById('trade-side').value,
            quantity: parseFloat(document.getElementById('trade-quantity').value),
            price: document.getElementById('trade-price').value ?
                   parseFloat(document.getElementById('trade-price').value) : undefined,
        };

        try {
            await this.apiRequest('/trades', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            this.closeModal();
            this.loadTrades();
            this.loadDashboard();
            this.showSuccess('Trade créé avec succès');
        } catch (error) {
            this.showError('Erreur lors de la création du trade');
        }
    }

    async toggleStrategy(strategyId) {
        try {
            await this.apiRequest(`/strategies/${strategyId}/toggle`, {
                method: 'PATCH'
            });

            this.loadStrategies();
            this.loadDashboard();
            this.showSuccess('Statut de la stratégie modifié');
        } catch (error) {
            this.showError('Erreur lors de la modification du statut');
        }
    }

    async deleteStrategy(strategyId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cette stratégie ?')) {
            return;
        }

        try {
            await this.apiRequest(`/strategies/${strategyId}`, {
                method: 'DELETE'
            });

            this.loadStrategies();
            this.loadDashboard();
            this.showSuccess('Stratégie supprimée');
        } catch (error) {
            this.showError('Erreur lors de la suppression');
        }
    }

    showError(message) {
        // Simple alert for now, could be improved with toast notifications
        alert(`Erreur: ${message}`);
    }

    showSuccess(message) {
        // Simple alert for now, could be improved with toast notifications
        alert(`Succès: ${message}`);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TradingApp();
});
