# tests/conftest.py
import sys
from pathlib import Path

# Добавляем корень проекта в PATH, чтобы можно было импортировать app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Загружаем .env ДО импорта любых модулей приложения
from dotenv import load_dotenv
import os

# Укажите путь к .env файлу явно, если он не в корне
dotenv_path = Path(__file__).resolve().parents[1] / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f".env файл не найден по пути: {dotenv_path}")

# Теперь можно безопасно импортировать приложение
from app.api_main import app  # замените на ваш FastAPI app
from app.services.report_service import ReportServices
from app.repo.transaction_repo import TransactionRepository
from app.models import TransactionModel

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_transaction_repo(mock_session):
    repo = TransactionRepository(mock_session)
    repo.get_trans_user_ids = AsyncMock(return_value=[])
    repo.get_aggregated_report = AsyncMock()
    return repo


@pytest.fixture
def mock_report_service(mock_transaction_repo):
    service = ReportServices(mock_session)
    service.report_repo = mock_transaction_repo
    return service


@pytest.fixture
def client():
    return TestClient(app)
