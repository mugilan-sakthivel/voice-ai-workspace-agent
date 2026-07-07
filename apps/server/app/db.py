from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Iterator, Optional

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from app.core.config import Settings


class Base(DeclarativeBase):
    pass


class ThreadRecord(Base):
    __tablename__ = "threads"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(128), index=True, nullable=False)
    title = Column(String(255), default="New thread", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    messages = relationship("MessageRecord", back_populates="thread", cascade="all, delete-orphan")


class MessageRecord(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True)
    thread_id = Column(ForeignKey("threads.id"), index=True, nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    thread = relationship("ThreadRecord", back_populates="messages")


class ApprovalRecordDB(Base):
    __tablename__ = "approvals"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(128), index=True, nullable=False)
    thread_id = Column(String(64), index=True, nullable=False)
    tool_name = Column(String(255), nullable=False)
    action_summary = Column(Text, nullable=False)
    arguments = Column(JSON, default=dict, nullable=False)
    status = Column(String(32), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class ConnectedAccountRecord(Base):
    __tablename__ = "connected_accounts"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(128), index=True, nullable=False)
    suite = Column(String(64), nullable=False)
    app = Column(String(128), nullable=False)
    status = Column(String(32), default="pending", nullable=False)
    connected_account_id = Column(String(255), nullable=True)
    auth_config_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class Database:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.available = False
        self._engine = None
        self._sessionmaker: Optional[sessionmaker[Session]] = None

        if not settings.database_url:
            return

        try:
            self._engine = create_engine(
                _normalize_database_url(settings.database_url),
                future=True,
                pool_pre_ping=True,
            )
            self._sessionmaker = sessionmaker(bind=self._engine, autoflush=False, autocommit=False)
            self.available = True
        except Exception:
            self.available = False

    def create_all(self) -> bool:
        if not self.available or self._engine is None:
            return False
        try:
            Base.metadata.create_all(self._engine)
            return True
        except (SQLAlchemyError, Exception):
            self.available = False
            self._sessionmaker = None
            self._engine = None
            return False

    @contextmanager
    def session(self) -> Iterator[Optional[Session]]:
        if not self.available or self._sessionmaker is None:
            yield None
            return

        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def touch_thread(thread: ThreadRecord) -> None:
    thread.updated_at = datetime.now(UTC)


def get_thread_by_id(session: Session, thread_id: str) -> Optional[ThreadRecord]:
    return session.get(ThreadRecord, thread_id)


def get_messages_for_thread(session: Session, thread_id: str) -> list[MessageRecord]:
    stmt = select(MessageRecord).where(MessageRecord.thread_id == thread_id).order_by(MessageRecord.created_at.asc())
    return list(session.scalars(stmt).all())


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://") and "://" in database_url and "+" not in database_url.split("://", 1)[0]:
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url
