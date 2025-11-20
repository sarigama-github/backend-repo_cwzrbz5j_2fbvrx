from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "graph_path_finder")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        _db = _client[DATABASE_NAME]
    return _db

async def create_document(collection_name: str, data: Dict[str, Any]) -> str:
    db = await get_db()
    now = datetime.utcnow().isoformat()
    data_with_meta = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(data_with_meta)
    return str(result.inserted_id)

async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    db = await get_db()
    cursor = db[collection_name].find(filter_dict or {}).limit(limit)
    docs: List[Dict[str, Any]] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # serialize ObjectId
        docs.append(doc)
    return docs
