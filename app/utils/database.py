from contextlib import contextmanager
from typing import Optional
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import Settings
from pydantic import PostgresDsn


def get_sqlalchemy_conn():
    connection_string: Optional[PostgresDsn] = Settings().DATABASE_URI
    return create_engine(connection_string, pool_size=20)


engine = get_sqlalchemy_conn()
_session_instance = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


@contextmanager
def session_scope() -> Session:
    """Provide a transactional scope around a series of operations."""

    session = _session_instance()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


Base = declarative_base()
Base.metadata.bind = engine
