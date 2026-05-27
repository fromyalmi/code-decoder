import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def rollback_db():
    # GREEN 단계에서 db/ 모듈 생성 후 실제 트랜잭션 롤백 구현
    yield
