from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import settings

# TODO добавить путь в переменные окружения
engine = create_engine(
    settings.database_url,
    connect_args={'check_same_thread': False}
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False
)


def get_database() -> Session:
    session = Session()

    try:
        yield session
    finally:
        session.close()
