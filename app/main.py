"""Rail yard slot planner: synthetic logistics scheduling demonstration."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

DB = os.getenv('DATABASE_PATH', str(Path(__file__).resolve().parent.parent / 'yard.db'))
app = FastAPI(title='Rail Yard Slot Planner', version='1.0.0')

@contextmanager
def connect():
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys=ON')
        yield conn

def init_db():
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS slots (id INTEGER PRIMARY KEY, track TEXT NOT NULL, start_min INTEGER NOT NULL, end_min INTEGER NOT NULL, train TEXT NOT NULL, UNIQUE(track,start_min,train))')

class Slot(BaseModel):
    track: str = Field(pattern=r'^[A-Z][0-9]{1,2}$')
    start_min: int = Field(ge=0, lt=1440)
    end_min: int = Field(gt=0, le=1440)
    train: str = Field(min_length=2, max_length=40, pattern=r'^[a-zA-Z0-9 -]+$')

@app.on_event('startup')
def startup():
    init_db()

@app.get('/api/slots')
def list_slots():
    init_db()
    with connect() as db:
        rows = db.execute('SELECT id,track,start_min,end_min,train FROM slots ORDER BY start_min,track').fetchall()
    return [dict(zip(('id','track','start_min','end_min','train'), row)) for row in rows]

@app.post('/api/slots', status_code=201)
def create_slot(slot: Slot):
    init_db()
    if slot.end_min <= slot.start_min:
        raise HTTPException(422, 'End must be after start; slots cannot cross midnight')
    with connect() as db:
        overlap = db.execute('SELECT id FROM slots WHERE track=? AND start_min < ? AND end_min > ?', (slot.track, slot.end_min, slot.start_min)).fetchone()
        if overlap:
            raise HTTPException(409, 'Track already occupied during this interval')
        cur = db.execute('INSERT INTO slots(track,start_min,end_min,train) VALUES (?,?,?,?)', (slot.track,slot.start_min,slot.end_min,slot.train))
        return {'id':cur.lastrowid, **slot.model_dump()}

@app.delete('/api/slots/{slot_id}', status_code=204)
def delete_slot(slot_id: int):
    with connect() as db:
        cur = db.execute('DELETE FROM slots WHERE id=?',(slot_id,))
        if not cur.rowcount:
            raise HTTPException(404, 'Slot not found')

@app.get('/', response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / 'index.html').read_text()
