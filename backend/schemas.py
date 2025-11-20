from __future__ import annotations
from typing import List, Tuple
from pydantic import BaseModel, Field

class Node(BaseModel):
    id: str
    x: float
    y: float

class Edge(BaseModel):
    source: str
    target: str
    weight: float = Field(ge=0)

class Graph(BaseModel):
    name: str = "default"
    nodes: List[Node]
    edges: List[Edge]

class KUPathQuery(BaseModel):
    start: str
    end: str

class PathResult(BaseModel):
    path: List[str]
    distance: float
