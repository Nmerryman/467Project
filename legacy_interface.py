from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqlalchemy import Select
from sqlalchemy import VARCHAR, FLOAT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


"""
use csci467; 
 create table parts ( 
    number int, 
    description varchar(50), 
    price float(8,2), 
    weight float(4,2), 
    pictureURL varchar(50)
 );
"""


class LegacyParts(Base):
    __tablename__ = "parts"

    number: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(VARCHAR(50))
    price: Mapped[float] = mapped_column(FLOAT(precision=8, decimal_return_scale=2))
    weight: Mapped[float] = mapped_column(FLOAT(precision=4, decimal_return_scale=2))
    pictureURL: Mapped[str] = mapped_column(VARCHAR(50))

    def __repr__(self):
        return f"Parts[{self.number}](${self.price}, {self.weight=}: {self.description=} -> {self.pictureURL})"


ENGINE = create_engine("mysql+pymysql://student:student@blitz.cs.niu.edu:3306/csci467", echo=False)


def ask_legacy(query: Select):
    """
    Run query against the legacy database.
    """
    with Session(ENGINE) as s:
        return s.execute(query).scalars().all()


def debug_sql_query(query: Select):
    return f"DEBUG: [\n{query.compile(compile_kwargs={'literal_binds': True})}\n]"


"""
TODO:
Add some extra helper funtions to interact with the legacy database. Ideally we could contain all custom sql for the
legacy db in this file. 
"""


if __name__ == '__main__':

    # Basic connection works
    with Session(ENGINE) as session:
        query = Select(LegacyParts)
        res = session.execute(query)
        count = 0
        for row in res.scalars().all():
            # print(row)
            count += 1
        print(type(res.scalars().all()))
        print(type(query))
        # print(type(res))
        # print(type(res.scalars().all()))
        print(f"First db found {count} parts.")

    for a in ask_legacy(Select(LegacyParts).filter(LegacyParts.price >= 100)):
        # print(a)
        pass

    temp = Select(LegacyParts).filter(LegacyParts.price >= 100)
    print(debug_sql_query(temp))
    # print(temp.compile(compile_kwargs={"literal_binds": True}))
    # print(temp.compile())





