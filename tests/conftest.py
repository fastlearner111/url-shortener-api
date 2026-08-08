#import pytest
#from fastapi.testclient import TestClient
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy.pool import StaticPool
#
#from app.main import app
#from app.core.database import Base, get_db
#from app.core.security import get_current_user
#from app.models.models import User
#
## Use an in-memory SQLite database for fast, isolated tests
#SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
#
#engine = create_engine(
#    SQLALCHEMY_DATABASE_URL,
#    connect_args={"check_same_thread": False},
#    poolclass=StaticPool,
#)
#TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#@pytest.fixture(autouse=True)
#def test_db():
#    # Create tables before each test and drop them after for a clean state
#    Base.metadata.create_all(bind=engine)
#    yield
#    Base.metadata.drop_all(bind=engine)
#
#@pytest.fixture
#def db_session():
#    db = TestingSessionLocal()
#    try:
#        yield db
#    finally:
#        db.close()
#
#@pytest.fixture
#def client(db_session):
#    # Override FastAPI's get_db dependency to use our test session
#    def override_get_db():
#        try:
#            yield db_session
#        finally:
#            pass
#
#    app.dependency_overrides[get_db] = override_get_db
#    with TestClient(app) as c:
#        yield c
#    app.dependency_overrides.clear()
#
## Helper fixture: Use this ONLY in tests that explicitly require a logged-in user
#@pytest.fixture
#def authenticated_client(client):
#    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com")
#    yield client
#    if get_current_user in app.dependency_overrides:
#        del app.dependency_overrides[get_current_user]

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_current_user
from app.models.models import User

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    # Automatically mock a logged-in user so test endpoints don't return 401
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com")

    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()