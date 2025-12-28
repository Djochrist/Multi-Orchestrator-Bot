"""
API FastAPI pour Multi-Orchestrator-Bot
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from .storage import strategies_storage, trades_storage
from .models import Strategy, Trade

# Modèles Pydantic pour l'API
class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    type: str = Field(..., pattern=r'^(rsi|macd|ml|manual)$')
    config: dict = Field(default_factory=dict)

class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r'^(active|inactive)$')
    config: Optional[dict] = None

class TradeCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    side: str = Field(..., pattern=r'^(buy|sell)$')
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)

class MarketDataResponse(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: str

# Création du router FastAPI
router = APIRouter()

# Routes pour les stratégies
@router.get("/strategies", response_model=List[dict])
def get_strategies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern=r'^(active|inactive)$')
):
    """Récupère toutes les stratégies"""
    strategies = strategies_storage.get_all()
    if status:
        strategies = [s for s in strategies if s.status == status]
    return [s.to_dict() for s in strategies[skip:skip + limit]]

@router.get("/strategies/{strategy_id}", response_model=dict)
def get_strategy(strategy_id: int):
    """Récupère une stratégie par ID"""
    strategy = strategies_storage.get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie non trouvée")
    return strategy.to_dict()

@router.post("/strategies", response_model=dict, status_code=201)
def create_strategy(strategy_data: StrategyCreate):
    """Crée une nouvelle stratégie"""
    strategy = Strategy(**strategy_data.dict())
    created = strategies_storage.create(strategy)
    return created.to_dict()

@router.put("/strategies/{strategy_id}", response_model=dict)
def update_strategy(strategy_id: int, strategy_data: StrategyUpdate):
    """Met à jour une stratégie"""
    existing = strategies_storage.get(strategy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Stratégie non trouvée")

    update_data = strategy_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)

    updated = strategies_storage.update(strategy_id, existing)
    return updated.to_dict()

@router.patch("/strategies/{strategy_id}/toggle", response_model=dict)
def toggle_strategy(strategy_id: int):
    """Active/désactive une stratégie"""
    strategy = strategies_storage.get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie non trouvée")

    strategy.status = 'inactive' if strategy.status == 'active' else 'active'
    updated = strategies_storage.update(strategy_id, strategy)
    return updated.to_dict()

@router.delete("/strategies/{strategy_id}", status_code=204)
def delete_strategy(strategy_id: int):
    """Supprime une stratégie"""
    strategy = strategies_storage.get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Stratégie non trouvée")

    strategies_storage.delete(strategy_id)

# Routes pour les trades
@router.get("/trades", response_model=List[dict])
def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern=r'^(open|closed|cancelled)$'),
    symbol: Optional[str] = None
):
    """Récupère tous les trades"""
    trades = trades_storage.get_all()
    if status:
        trades = [t for t in trades if t.status == status]
    if symbol:
        trades = [t for t in trades if t.symbol == symbol]
    # Trie par date de création décroissante
    trades.sort(key=lambda x: x.created_at, reverse=True)
    return [t.to_dict() for t in trades[skip:skip + limit]]

@router.post("/trades", response_model=dict, status_code=201)
def create_trade(trade_data: TradeCreate):
    """Crée un nouveau trade"""
    # Utilise le prix fourni ou une valeur par défaut
    effective_price = trade_data.price or 100.0

    trade = Trade(
        symbol=trade_data.symbol,
        side=trade_data.side,
        quantity=trade_data.quantity,
        entry_price=effective_price,
        status='open'
    )

    created = trades_storage.create(trade)
    return created.to_dict()

# Routes pour les données de marché (mockées)
@router.get("/market/prices", response_model=List[MarketDataResponse])
def get_market_prices():
    """Récupère les prix de marché (données mockées)"""
    mock_data = [
        MarketDataResponse(symbol="BTC", price=95000.0, volume=1500000.0, timestamp=datetime.now(timezone.utc).isoformat()),
        MarketDataResponse(symbol="ETH", price=3500.0, volume=800000.0, timestamp=datetime.now(timezone.utc).isoformat()),
        MarketDataResponse(symbol="SOL", price=180.0, volume=500000.0, timestamp=datetime.now(timezone.utc).isoformat()),
        MarketDataResponse(symbol="AAPL", price=230.0, volume=1000000.0, timestamp=datetime.now(timezone.utc).isoformat()),
        MarketDataResponse(symbol="TSLA", price=350.0, volume=2000000.0, timestamp=datetime.now(timezone.utc).isoformat()),
    ]
    return mock_data

# Route pour le dashboard
@router.get("/dashboard/summary")
def get_dashboard_summary():
    """Récupère le résumé du dashboard"""
    trades = trades_storage.get_all()
    closed_trades = [t for t in trades if t.is_closed]

    total_pnl = sum(t.pnl or 0 for t in closed_trades)
    open_positions = len([t for t in trades if t.is_open])
    active_strategies = len(strategies_storage.find_by(status="active"))

    return {
        "total_pnl": total_pnl,
        "open_positions": open_positions,
        "active_strategies": active_strategies,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Route de santé
@router.get("/health")
def health_check():
    """Vérification de santé de l'application"""
    return {"status": "healthy", "version": "1.0.0"}
