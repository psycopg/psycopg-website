import datetime as dt
from typing import Annotated
from uuid import UUID, uuid4

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Request
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field

# Application models


class Person(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    date_of_birth: dt.date | None = None


# Application creation


def lifespan(app: FastAPI):
    with ConnectionPool("") as pool:
        app.state.pool = pool
        yield


app = FastAPI(title="My People", lifespan=lifespan)


# Dependency injection definition


def get_connection(request: Request):
    with request.app.state.pool.connection() as conn:
        yield conn


Conn = Annotated[psycopg.Connection, Depends(get_connection)]


# View functions


@app.get("/person")
def list_people(conn: Conn) -> list[Person]:
    return fetch_people(conn)


@app.get("/person/{id}")
def get_person(id: UUID, conn: Conn) -> Person:
    if people := fetch_people(conn, id=id):
        return people[0]
    else:
        raise HTTPException(status_code=404)


# Application helpers


def fetch_people(conn: psycopg.Connection, id: UUID | None = None) -> list[Person]:
    query = "SELECT id, name, date_of_birth FROM person"
    if id:
        query += " WHERE id = %(id)s"

    with conn.cursor(row_factory=class_row(Person)) as cur:
        cur.execute(query, {"id": id})
        return cur.fetchall()
