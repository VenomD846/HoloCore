from __future__ import annotations

import json
import sys
from pathlib import Path

from .engine import HoloCoreEngine
from .commands import COMMANDS
from .home import HomeManager
from .lifecycle import sync_all
from .animus import Animus
from .animus_mining import AnimusMiner, MiningOptions


def _tool(name, description, properties=None, required=None): return {"name": name, "description": description, "inputSchema": {"type": "object", "properties": properties or {}, "required": required or []}}
TOOLS = [
    _tool("holocore_search", "Unified relevance-gated search", {"query": {"type": "string"}, "world": {"type": "string"}}, ["query"]),
    _tool("holocore_status", "World, Archive, Atlas and Animus status"),
    _tool("holocore_archive_search", "Search the curated wiki", {"query": {"type": "string"}}, ["query"]),
    _tool("holocore_archive_read", "Read a wiki entry", {"path": {"type": "string"}}, ["path"]),
    _tool("holocore_archive_create", "Create an AI-first wiki entry", {"path": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}}, ["path", "title", "content"]),
    _tool("holocore_atlas_refresh", "Refresh the native structural graph"),
    _tool("holocore_atlas_search", "Search structural signals", {"query": {"type": "string"}}, ["query"]),
    _tool("holocore_atlas_explain", "Explain a resolved structural signal", {"query": {"type": "string"}}, ["query"]),
    _tool("holocore_atlas_path", "Find a shortest Atlas path", {"source": {"type": "string"}, "target": {"type": "string"}, "max_depth": {"type": "integer"}}, ["source", "target"]),
    _tool("holocore_atlas_affected", "Find signals affected by a target", {"query": {"type": "string"}, "depth": {"type": "integer"}}, ["query"]),
    _tool("holocore_atlas_neighborhood", "Inspect a local relationship neighborhood", {"query": {"type": "string"}, "depth": {"type": "integer"}}, ["query"]),
    _tool("holocore_atlas_audit", "Audit Atlas quality and unresolved relationships"),
    _tool("holocore_atlas_constellations", "List deterministic Atlas constellations", {"min_size": {"type": "integer"}}),
    _tool("holocore_atlas_html", "Generate a self-contained Atlas HTML viewer"),
    _tool("holocore_atlas_export", "Export Atlas JSON, HTML, Markdown, and a manifest", {"output": {"type": "string"}, "formats": {"type": "array"}}, ["output"]),
    _tool("holocore_remember", "Store a scoped Memory Shard", {"content": {"type": "string"}, "sector": {"type": "string"}, "source": {"type": "string"}}, ["content"]),
    _tool("holocore_recall", "Recall scoped episodic memory", {"query": {"type": "string"}, "sector": {"type": "string"}}, ["query"]),
    _tool("holocore_ingest_chat", "Store raw chat and distill summary/facts", {"messages": {"type": "array"}, "sector": {"type": "string"}, "instructions": {"type": "string"}}, ["messages"]),
    _tool("holocore_home", "Show the selected shared HoloCore Home and Obsidian vault"),
    _tool("holocore_worlds", "List every project registered with the shared HoloCore Home"),
    _tool("holocore_global_graph", "Build one Atlas-only graph across registered Worlds", {"output": {"type": "string"}}),
    _tool("holocore_setup", "Register this World and connect supported AI clients. Ask the user to choose the shared HoloCore Home location first.", {"home": {"type": "string", "description": "User-chosen shared HoloCore Home directory"}}, ["home"]),
    _tool("holocore_sync_all", "Reconcile every registered World after a HoloCore upgrade"),
    _tool("holocore_ingest", "Ingest a local file, folder, or HTTP(S) URL into immutable raw storage, scoped memory, a durable Archive Entry, and the current Atlas", {"source": {"type": "string"}, "title": {"type": "string"}}, ["source"]),
    _tool("holocore_inbox_sync", "Ingest new files from this World's visible source Inbox"),
    _tool("holocore_animus_mine", "Mine one explicitly scoped World using files, conversations, or Git history", {"mode": {"type": "string"}, "path": {"type": "string"}, "sector": {"type": "string"}}, ["mode"]),
    _tool("holocore_animus_checkpoint", "Read the last scoped Animus mining checkpoint", {"mode": {"type": "string"}, "source": {"type": "string"}, "sector": {"type": "string"}}, ["mode", "source"]),
    _tool("holocore_animus_diary", "Record an episodic diary entry in the active World", {"content": {"type": "string"}, "title": {"type": "string"}, "sector": {"type": "string"}}, ["content"]),
    _tool("holocore_animus_timeline", "Read the active World's diary timeline", {"sector": {"type": "string"}, "limit": {"type": "integer"}}),
    _tool("holocore_animus_consolidate", "Merge duplicate diary entries within one scope", {"sector": {"type": "string"}}),
    _tool("holocore_animus_export", "Export scoped Animus diary records", {"sector": {"type": "string"}, "limit": {"type": "integer"}}),
]
PROMPTS = [
    {
        "name": command.name,
        "description": command.description,
        "arguments": [{"name": "arguments", "description": "Optional command details", "required": False}],
    }
    for command in COMMANDS
]


def get_prompt(name: str, arguments: dict) -> dict:
    command = next((item for item in COMMANDS if item.name == name), None)
    if command is None:
        raise ValueError(f"Unknown HoloCore prompt: {name}")
    supplied = str(arguments.get("arguments", "")).strip()
    invocation = command.invocation.replace("$ARGUMENTS", supplied).strip()
    if name == "setup":
        text = (
            "Before running setup, ask the user where the one shared HoloCore Home should live. "
            "Explain that its Archive folder is the Obsidian vault shared by every project. "
            "After the user chooses a path, run: holocore setup --home <chosen-path>"
        )
    else:
        text = f"Run this from the current World and return the focused result: {invocation}"
    return {
        "description": command.description,
        "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
    }


def call(engine: HoloCoreEngine, name: str, args: dict):
    if name == "holocore_search": return [r.__dict__ for r in engine.search(args["query"], args.get("world"))]
    if name == "holocore_status": return engine.status()
    if name == "holocore_archive_search": return engine.router.archive.search(args["query"])
    if name == "holocore_archive_read": return engine.router.archive.read(args["path"])
    if name == "holocore_archive_create": return engine.router.archive.create(args["path"], f"# {args['title']}\n\n## For future Claude\n{args['content']}")
    if name == "holocore_atlas_refresh": return engine.refresh()
    if name == "holocore_atlas_search": return engine.router.atlas.search(args["query"])
    if name == "holocore_atlas_explain": return engine.router.atlas.explain(args["query"])
    if name == "holocore_atlas_path": return engine.router.atlas.shortest_path(args["source"], args["target"], max_depth=args.get("max_depth"))
    if name == "holocore_atlas_affected": return engine.router.atlas.affected(args["query"], depth=args.get("depth", 2))
    if name == "holocore_atlas_neighborhood": return engine.router.atlas.neighborhood(args["query"], depth=args.get("depth", 1))
    if name == "holocore_atlas_audit": return engine.router.atlas.audit()
    if name == "holocore_atlas_constellations": return engine.router.atlas.constellations(min_size=args.get("min_size", 2))
    if name == "holocore_atlas_html":
        return engine.ensure_atlas()
    if name == "holocore_atlas_export":
        from .atlas_exports import export_atlas
        return export_atlas(engine.router.atlas, args["output"], args.get("formats"))
    if name == "holocore_remember": return engine.remember(args["content"], args.get("sector", "general"), args.get("source", ""))
    if name == "holocore_recall":
        engine.router.ensure_memory_scope()
        return [r.__dict__ for r in engine.router.animus.search(args["query"], world=engine.router.world_id, sector=args.get("sector"))]
    if name == "holocore_ingest_chat": return engine.ingest_chat(args["messages"], sector=args.get("sector", "conversations"), source="mcp", custom_instructions=args.get("instructions", ""))
    if name == "holocore_home":
        manager = HomeManager(); return {"home": str(manager.home), "archive": str(manager.archive), "worlds_file": str(manager.worlds_path)}
    if name == "holocore_worlds": return HomeManager().list_worlds()
    if name == "holocore_global_graph":
        from .global_graph import build_global_graph
        manager = HomeManager(); output = args.get("output") or str(manager.home / "global-graph" / "graph.json")
        return build_global_graph(manager.home, output=output)
    if name == "holocore_setup": return engine.setup(home=Path(args["home"]).expanduser())
    if name == "holocore_sync_all": return sync_all()
    if name == "holocore_ingest": return engine.ingest_source(args["source"], title=args.get("title"))
    if name == "holocore_inbox_sync": return engine.sync_inbox()
    if name.startswith("holocore_animus_"):
        root = engine.root; config = engine.router.config; animus = Animus(config.animus_path); world = config.world_id or root.name
        animus.create_world(world, root.name, {"root": str(root)})
        sector = args.get("sector")
        if sector: animus.create_sector(world, sector)
        if name == "holocore_animus_mine":
            return AnimusMiner(animus).mine(MiningOptions(mode=args["mode"], world=world, sector=sector or "project", root=Path(args.get("path") or root).resolve()))
        if name == "holocore_animus_checkpoint": return animus.get_checkpoint(world=world, sector=sector, mode=args["mode"], source_ref=args["source"])
        if name == "holocore_animus_diary": return animus.record_diary(args["content"], world=world, sector=sector or "project", title=args.get("title", ""), source_ref="mcp")
        if name == "holocore_animus_timeline": return animus.timeline(world=world, sector=sector, limit=int(args.get("limit", 100)))
        if name == "holocore_animus_consolidate": return animus.consolidate(world=world, sector=sector)
        if name == "holocore_animus_export": return animus.timeline(world=world, sector=sector, limit=int(args.get("limit", 1000)))
    raise ValueError(f"Unknown HoloCore tool: {name}")


def main() -> int:
    engine = HoloCoreEngine(Path.cwd())
    for line in sys.stdin:
        request = {}
        try:
            request = json.loads(line); method = request.get("method"); params = request.get("params", {})
            if method == "initialize": result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}, "prompts": {}}, "serverInfo": {"name": "holocore", "version": "0.5.0"}}
            elif method == "tools/list": result = {"tools": TOOLS}
            elif method == "tools/call": result = {"content": [{"type": "text", "text": json.dumps(call(engine, params["name"], params.get("arguments", {})), ensure_ascii=False, default=str)}]}
            elif method == "prompts/list": result = {"prompts": PROMPTS}
            elif method == "prompts/get": result = get_prompt(params["name"], params.get("arguments", {}))
            else: result = {}
            response = {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
        except Exception as exc: response = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32000, "message": str(exc)}}
        print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__": raise SystemExit(main())
