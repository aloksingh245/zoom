from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Separated into base.py to avoid circular imports.
    """
    pass
