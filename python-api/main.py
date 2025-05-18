from fastapi import FastAPI, Query
import csv
from typing import Optional

app = FastAPI()

def read_books_from_csv(filename):
    books = {}
    with open(filename, "r", encoding="UTF-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            book_id = row.get("book_id")
            book_info = {}
            if book_id:
                for key, value in row.items():
                    if key != "book_id":
                        book_info[key] = value
            books[book_id] = book_info
        return books

@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/api/v1/books")
async def get_books(
    book_id: Optional[str] = Query(None, description="Filter by Book ID"),
    author: Optional[str] = Query(None, description="Filter by Author"),
    genre: Optional[str] = Query(None, description="Filter by Genre"),
    publication_year: Optional[str] = Query(None, description="Filter by Publication Year")
):
    all_books = read_books_from_csv("books.csv")
    filtered_books = {}
    for b_id, book_data in all_books.items():
        match = True
        if book_id and b_id != book_id:
            match = False
        if author and book_data.get("author", "").lower() != author.lower():
            match = False
        if genre and book_data.get("genre", "").lower() != genre.lower():
            match = False
        if publication_year and book_data.get("publication_year") != publication_year:
            match = False
        if match:
            filtered_books[b_id] = book_data
    return filtered_books

if __name__ == "__main__":
    print(get_books(book_id="B001"))
