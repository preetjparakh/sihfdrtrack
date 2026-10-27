from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models import models
from backend.app.models.models import Institution
from backend.seed_db import seed_database


def bootstrap_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        has_seed_data = db.query(Institution.id).first() is not None
    if not has_seed_data:
        seed_database()


if __name__ == "__main__":
    bootstrap_database()
