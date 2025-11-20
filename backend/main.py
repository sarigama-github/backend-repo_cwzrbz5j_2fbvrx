from __future__ import annotations
from typing import Dict, List, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schemas import Graph, KUPathQuery, PathResult
from database import get_documents, create_document

app = FastAPI(title="Graph Path Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Graph Path Finder backend is running"}

@app.get("/test")
async def test():
    try:
        # probe database by listing collections
        cols = await get_documents("__probe__", {}, 1)  # may be empty
        status = "ok"
    except Exception as e:
        status = f"error: {e}"  # surface status for frontend
        cols = []
    return {
        "backend": "ok",
        "database": "mongodb",
        "database_url": "env",
        "database_name": "graph_path_finder",
        "connection_status": status,
        "collections": [],
    }

# In-memory Dijkstra utility (for demo). Real persistence would save graphs via Mongo.
# This keeps business logic in the backend while frontend remains UI-only.

def build_adj_list(nodes: List[str], edges: List[Tuple[str, str, float]]):
    adj: Dict[str, List[Tuple[str, float]]] = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj

@app.post("/dijkstra", response_model=PathResult)
async def run_dijkstra(graph: Graph, query: KUPathQuery):
    nodes = [n.id for n in graph.nodes]
    if query.start not in nodes or query.end not in nodes:
        raise HTTPException(status_code=400, detail="Start or end not in graph")
    edges = [(e.source, e.target, e.weight) for e in graph.edges]
    adj = build_adj_list(nodes, edges)

    import heapq
    INF = float('inf')
    dist: Dict[str, float] = {n: INF for n in nodes}
    prev: Dict[str, str | None] = {n: None for n in nodes}
    dist[query.start] = 0.0
    pq: List[Tuple[float, str]] = [(0.0, query.start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        if u == query.end:
            break
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if dist[query.end] == INF:
        raise HTTPException(status_code=404, detail="No path found")

    # reconstruct path
    path: List[str] = []
    cur = query.end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    return PathResult(path=path, distance=dist[query.end])
