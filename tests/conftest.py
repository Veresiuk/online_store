import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from online_store.models import Base


@pytest.fixture
def session() -> Session:
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)

    TestSession = sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
    )

    with TestSession() as session:
        yield session

    Base.metadata.drop_all(test_engine)