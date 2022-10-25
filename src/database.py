from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import settings

# TODO добавить путь в переменные окружения
engine = create_engine(
    'sqlite:////home/worker/PycharmProjects/connectnow/sqlite3.db',
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
