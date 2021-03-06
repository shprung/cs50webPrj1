import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)
for isbn,title,author,year in reader:
    if year=='year':
        """ skip headline """
    else :
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:i, :t, :a, :y)",
                {"i": isbn, "t": title, "a": author, "y": year})
        print(f"Added the book {title} from {year}")
db.commit()


