import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app

_LLM_STUB = {
    "forest": "두 수를 더해 출력하는 프로그램입니다.",
    "tree": "x=1 → y=2 → print(x+y)",
    "line_explanations": [
        {"line_no": 1, "short": "정수 1을 x에 할당"},
        {"line_no": 2, "short": "정수 2를 y에 할당"},
        {"line_no": 3, "short": "x와 y의 합 출력"},
    ],
    "deep_leaves": [{"line_no": i, "deep": f"깊은 설명 {i}"} for i in range(1, 6)],
    "tags": ["python", "arithmetic"],
    "key_concepts": [{"name": "변수 할당", "definition": "값을 이름에 바인딩"}],
}


@pytest.fixture(autouse=True)
def _default_llm_mock(monkeypatch):
    monkeypatch.setattr("app.llm.client.call_analysis", lambda msgs, **kw: _LLM_STUB)


_SIGNUP_URL = "/api/v1/auth/signup"
_LOGIN_URL = "/api/v1/auth/login"


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app, base_url="https://testserver") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def rollback_db():
    yield
