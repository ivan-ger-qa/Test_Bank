from collections.abc import Iterator

import pytest
from sqlalchemy.orm.session import Session

from src.main.db.engine import SessionLocal, engine


# Сессия БД с откатом
@pytest.fixture
def db_session() -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
