import pytest
import mongomock

@pytest.fixture(scope="function")
def mock_mongo_db():
    client = mongomock.MongoClient()
    db = client["test_db"]
    yield db 