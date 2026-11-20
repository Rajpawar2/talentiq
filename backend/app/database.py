from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Configure connection arguments based on database engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency that provides an independent database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in the database and migrate schema."""
    from app.models import (
        user, resume, job_description, interview, evaluation
    )
    Base.metadata.create_all(bind=engine)
    _migrate_user_table()

def _migrate_user_table():
    """Safely migrate user table to remove obsolete OTP columns while preserving existing users."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    existing_cols = {col["name"] for col in inspector.get_columns("users")}
    obsolete_cols = [
        "verification_otp_hash",
        "verification_otp_expires_at",
        "verification_attempts",
        "last_otp_sent_at",
        "email_verified",
    ]
    with engine.begin() as conn:
        for col in obsolete_cols:
            if col in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE users DROP COLUMN {col}"))
                except Exception:
                    # Ignore if the underlying DB engine does not support DROP COLUMN
                    pass

