"""
Pytest configuration for KrishiVision test suite.
E-09: Isolates test database execution from the persistent backend/krishivision.db.
Creates an isolated temporary SQLite database for test execution and cleans it up on teardown.
"""

import os
import uuid
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
import sys
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app.db.database as db_module
from app.db.database import Base, get_db
from app.main import app, seed_database


@pytest.fixture(scope="session", autouse=True)
def isolated_test_database():
    """
    Session-wide fixture that creates a temporary isolated SQLite database
    for all tests, completely isolating backend/krishivision.db from test mutations.
    """
    test_db_file = Path(__file__).resolve().parent / f".test_krishivision_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_file}"

    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    orig_engine = db_module.engine
    orig_session_local = db_module.SessionLocal

    db_module.engine = test_engine
    db_module.SessionLocal = TestingSessionLocal

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Seed the demo user into the isolated test database
    seed_database()

    yield test_db_file

    # Teardown
    app.dependency_overrides.clear()
    test_engine.dispose()
    db_module.engine = orig_engine
    db_module.SessionLocal = orig_session_local

    for suffix in ("", "-wal", "-shm", "-journal"):
        test_file = Path(f"{test_db_file}{suffix}")
        if test_file.exists():
            test_file.unlink()


@pytest.fixture
def client():
    """TestClient fixture using the isolated test database."""
    with TestClient(app) as test_client:
        yield test_client
