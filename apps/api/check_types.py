from sqlmodel import Session, select
from apps.api.db import engine
from apps.api.models import Prompt

with Session(engine) as session:
    statement = select(Prompt)
    results = session.exec(statement).all()
    types = set(p.type for p in results)
    print(f"Distinct types: {types}")
    for t in types:
        count = len([p for p in results if p.type == t])
        print(f"Type {t}: {count} items")
