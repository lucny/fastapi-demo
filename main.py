import orjson
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class MovieRecord(BaseModel):
    title: str
    year: int
    runtime: int
    rating: float
    description: str
    director: str
    actors: list[str]
    url: str
    genres: set[str]

    @staticmethod
    def from_dict(data: dict):
        genres = set(data.pop('genres', []))
        record = MovieRecord(genres=genres, **data)
        return record


class Problem(BaseModel):
    detail: str


class Database:
    def __init__(self):
        self._data: list = []

    def load_from_filename(self, filename: str):
        with open(filename, "rb") as f:
            data = orjson.loads(f.read())
            for record in data:
                obj = MovieRecord.from_dict(record)
                self._data.append(obj)

    def delete(self, id_movie: int):
        if 0 < id_movie >= len(self._data):
            return
        self._data.pop(id_movie)

    def add(self, movie: MovieRecord):
        self._data.append(movie)

    def get(self, id_movie: int):
        if 0 < id_movie >= len(self._data):
            return
        return self._data[id_movie]

    def get_all(self) -> list[MovieRecord]:
        return self._data

    def update(self, id_movie: int, movie: MovieRecord):
        if 0 < id_movie >= len(self._data):
            return
        self._data[id_movie] = movie

    def count(self) -> int:
        return len(self._data)


db = Database()
db.load_from_filename('movies.json')

app = FastAPI(title="Filmoteka API", version="0.1", docs_url="/docs")

app.is_shutdown = False


@app.get("/movies", response_model=list[MovieRecord], description="Vrátí seznam filmů")
async def get_movies():
    return db.get_all()


@app.get("/movies/{id_movie}", response_model=MovieRecord)
async def get_movie(id_movie: int):
    return db.get(id_movie)


@app.post("/movies", response_model=MovieRecord, description="Přidáme film do DB")
async def post_movies(movie: MovieRecord):
    db.add(movie)
    return movie


@app.delete("/movies/{id_movie}", description="Sprovodíme film ze světa", responses={
    404: {'model': Problem}
})
async def delete_movie(id_movie: int):
    movie = db.get(id_movie)
    if movie is None:
        raise HTTPException(404, "Film neexistuje")
    db.delete(id_movie)
    return {'status': 'smazano'}


@app.patch("/movies/{id_movie}", description="Aktualizujeme film do DB", responses={
    404: {'model': Problem}
})
async def update_movie(id_movie: int, updated_movie: MovieRecord):
    movie = db.get(id_movie)
    if movie is None:
        raise HTTPException(404, "Film neexistuje")
    db.update(id_movie, updated_movie)
    return {'old': movie, 'new': updated_movie}