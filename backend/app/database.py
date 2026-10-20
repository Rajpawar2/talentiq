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
    """Ensure email verification columns exist and existing users remain verified."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    existing_cols = {col["name"] for col in inspector.get_columns("users")}
    with engine.begin() as conn:
        if "email_verified" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 1"))
        if "verification_otp_hash" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN verification_otp_hash VARCHAR(255)"))
        if "verification_otp_expires_at" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN verification_otp_expires_at DATETIME"))
        if "verification_attempts" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN verification_attempts INTEGER DEFAULT 0"))
        if "last_otp_sent_at" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_otp_sent_at DATETIME"))
        # Ensure any pre-existing users are marked as verified so they are not locked out
        conn.execute(text("UPDATE users SET email_verified = 1 WHERE email_verified IS NULL"))

