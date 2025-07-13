from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.core.config import database
from app.core.models import Note

router = APIRouter()

class NoteIn(BaseModel):
    title: str
    content: str

class NoteOut(NoteIn):
    id: int
    created_at: str
    updated_at: str

@router.get("/notes", response_model=List[NoteOut])
async def get_all_notes(
    keyword: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    filters = []
    values = {}
    if keyword:
        filters.append("(title LIKE :kw OR content LIKE :kw)")
        values["kw"] = f"%{keyword}%"
    if from_date:
        filters.append("created_at >= :from_date")
        values["from_date"] = from_date
    if to_date:
        filters.append("created_at <= :to_date")
        values["to_date"] = to_date
    filter_clause = "WHERE " + " AND ".join(filters) if filters else ""
    query = f"SELECT * FROM notes {filter_clause} ORDER BY created_at DESC"
    rows = await database.fetch_all(query=query, values=values)
    return rows

@router.get("/notes/{id}", response_model=NoteOut)
async def get_note(id: int):
    query = "SELECT * FROM notes WHERE id = :id"
    row = await database.fetch_one(query=query, values={"id": id})
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return row

@router.post("/notes", response_model=NoteOut)
async def create_note(note: NoteIn):
    query = """
        INSERT INTO notes (title, content, created_at, updated_at)
        VALUES (:title, :content, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """
    values = {"title": note.title, "content": note.content}
    note_id = await database.execute(query=query, values=values)
    fetch_query = "SELECT * FROM notes WHERE id = :id"
    row = await database.fetch_one(fetch_query, {"id": note_id})
    return row

@router.put("/notes/{id}", response_model=NoteOut)
async def update_note(id: int, note: NoteIn):
    query = "SELECT * FROM notes WHERE id = :id"
    existing = await database.fetch_one(query=query, values={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    update_query = """
        UPDATE notes
        SET title = :title, content = :content, updated_at = CURRENT_TIMESTAMP
        WHERE id = :id
    """
    await database.execute(update_query, {"id": id, "title": note.title, "content": note.content})
    updated = await database.fetch_one(query, {"id": id})
    return updated

@router.delete("/notes/{id}", response_model=dict)
async def delete_note(id: int):
    query = "SELECT * FROM notes WHERE id = :id"
    existing = await database.fetch_one(query=query, values={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
    delete_query = "DELETE FROM notes WHERE id = :id"
    await database.execute(delete_query, {"id": id})
    return {"success": True}
