from __future__ import annotations

import json
import sys
from pathlib import Path

from .engine import HoloCoreEngine


def _tool(name, description, properties=None, required=None): return {"name": name, "description": description, "inputSchema": {"type": "object", "properties": properties or {}, "required": required or []}}
TOOLS = [
    _tool("holocore_search", "Unified relevance-gated search", {"query": {"type": "string"}, "world": {"type": "string"}}, ["query"]),
    _tool("holocore_status", "World, Archive, Atlas and Animus status"),
    _tool("holocore_archive_search", "Search the curated wiki", {"query": {"type": "string"}}, ["query"]),
    _tool("holocore_archive_read", "Read a wiki entry", {"path": {"type": "string"}}, ["path"]),
    _tool("holocore_archive_create", "Create an AI-first wiki entry", {"path": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}}, ["path", "title", "content"]),
    _tool("holocore_atlas_refresh", "Refresh the native structural graph"),
    _tool("holocore_atlas_search", "Search structural signals", {"query": {"type": "string"}}, ["query"]),
    _tool("holocore_atlas_html", "Generate a self-contained Atlas HTML viewer"),
    _tool("holocore_remember", "Store a scoped Memory Shard", {"content": {"type": "string"}, "sector": {"type": "string"}, "source": {"type": "string"}}, ["content"]),
    _tool("holocore_recall", "Recall scoped episodic memory", {"query": {"type": "string"}, "sector": {"type": "string"}}, ["query"]),
    _tool("holocore_ingest_chat", "Store raw chat and distill summary/facts", {"messages": {"type": "array"}, "sector": {"type": "string"}, "instructions": {"type": "string"}}, ["messages"]),
]


def call(engine: HoloCoreEngine, name: str, args: dict):
    if name == "holocore_search": return [r.__dict__ for r in engine.search(args["query"], args.get("world"))]
    if name == "holocore_status": return engine.status()
    if name == "holocore_archive_search": return engine.router.archive.search(args["query"])
    if name == "holocore_archive_read": return engine.router.archive.read(args["path"])
    if name == "holocore_archive_create": return engine.router.archive.create(args["path"], f"# {args['title']}\n\n## For future Claude\n{args['content']}")
    if name == "holocore_atlas_refresh": return engine.refresh()
    if name == "holocore_atlas_search": return engine.router.atlas.search(args["query"])
    if name == "holocore_atlas_html":
        from .atlas_html import generate_atlas_html
        return {"html": str(generate_atlas_html(engine.router.atlas.output))}
    if name == "holocore_remember": return engine.remember(args["content"], args.get("sector", "general"), args.get("source", ""))
    if name == "holocore_recall": return [r.__dict__ for r in engine.router.animus.search(args["query"], world=engine.root.name, sector=args.get("sector"))]
    if name == "holocore_ingest_chat": return engine.ingest_chat(args["messages"], sector=args.get("sector", "conversations"), source="mcp", custom_instructions=args.get("instructions", ""))
    raise ValueError(f"Unknown HoloCore tool: {name}")


def main() -> int:
    engine = HoloCoreEngine(Path.cwd())
    for line in sys.stdin:
        request = {}
        try:
            request = json.loads(line); method = request.get("method"); params = request.get("params", {})
            if method == "initialize": result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "holocore", "version": "0.2.0"}}
            elif method == "tools/list": result = {"tools": TOOLS}
            elif method == "tools/call": result = {"content": [{"type": "text", "text": json.dumps(call(engine, params["name"], params.get("arguments", {})), ensure_ascii=False, default=str)}]}
            else: result = {}
            response = {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
        except Exception as exc: response = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32000, "message": str(exc)}}
        print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__": raise SystemExit(main())
