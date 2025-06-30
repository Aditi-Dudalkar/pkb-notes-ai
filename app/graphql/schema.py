import strawberry
from typing import List, Optional
from app.core.config import database
from app.core.models import Note


@strawberry.type
class NoteType:
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str

@strawberry.type
class Query:
    @strawberry.field
    async def all_notes(self) -> List[NoteType]:
        query = "SELECT * FROM notes ORDER BY created_at DESC"
        rows = await database.fetch_all(query=query)
        return [
            NoteType(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"]),
            )
            for row in rows
        ]

    @strawberry.field
    async def get_note(self, id: int) -> Optional[NoteType]:
        query = "SELECT * FROM notes WHERE id = :id"
        row = await database.fetch_one(query=query, values={"id": id})

        if row:
            return NoteType(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"]),
            )
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_note(self, title: str, content: str) -> NoteType:
        query = """
            INSERT INTO notes (title, content, created_at, updated_at)
            VALUES (:title, :content, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        values = {"title": title, "content": content}
        note_id = await database.execute(query=query, values=values)

        get_query = "SELECT * FROM notes WHERE id = :id"
        row = await database.fetch_one(get_query, {"id": note_id})

        return NoteType(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    @strawberry.mutation
    async def update_note(self, id: int, title: str, content: str) -> Optional[NoteType]:
        get_query = "SELECT * FROM notes WHERE id = :id"
        existing = await database.fetch_one(get_query, {"id": id})
        if not existing:
            return None

        update_query = """
            UPDATE notes
            SET title = :title, content = :content, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """
        await database.execute(update_query, {"id": id, "title": title, "content": content})

        updated = await database.fetch_one(get_query, {"id": id})
        return NoteType(
            id=updated["id"],
            title=updated["title"],
            content=updated["content"],
            created_at=str(updated["created_at"]),
            updated_at=str(updated["updated_at"]),
        )
        
    @strawberry.mutation
    async def delete_note(self, id: int) -> bool:
        get_query = "SELECT * FROM notes WHERE id = :id"
        existing = await database.fetch_one(get_query, {"id": id})
        if not existing:
            return False

        delete_query = "DELETE FROM notes WHERE id = :id"
        await database.execute(delete_query, {"id": id})
        return True

schema = strawberry.Schema(query=Query, mutation=Mutation)
