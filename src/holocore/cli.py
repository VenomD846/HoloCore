from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import HoloCoreEngine
from .atlas_html import generate_atlas_html


def main() -> int:
    parser = argparse.ArgumentParser(prog="holocore", description="Unified local knowledge engine")
    parser.add_argument("--root", default="."); parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("--no-git", action="store_true")
    sub.add_parser("status"); sub.add_parser("doctor")
    search = sub.add_parser("search"); search.add_argument("query"); search.add_argument("--world")
    sub.add_parser("atlas-refresh")
    sub.add_parser("atlas-html"); sub.add_parser("atlas-view")
    atlas_search = sub.add_parser("atlas-search"); atlas_search.add_argument("query")
    mine = sub.add_parser("mine"); mine.add_argument("path", nargs="?", default="."); mine.add_argument("--sector", default="project")
    remember = sub.add_parser("remember"); remember.add_argument("content"); remember.add_argument("--sector", default="general"); remember.add_argument("--source", default="")
    recall = sub.add_parser("recall"); recall.add_argument("query"); recall.add_argument("--sector")
    ingest = sub.add_parser("ingest-chat"); ingest.add_argument("file"); ingest.add_argument("--sector", default="conversations"); ingest.add_argument("--instructions", default="")
    archive_init = sub.add_parser("archive-init")
    archive_search = sub.add_parser("archive-search"); archive_search.add_argument("query")
    archive_create = sub.add_parser("archive-create"); archive_create.add_argument("path"); archive_create.add_argument("content")
    args = parser.parse_args(); engine = HoloCoreEngine(Path(args.root))
    if args.command == "init": value = engine.initialize(git=not args.no_git)
    elif args.command in {"status", "doctor"}: value = engine.status()
    elif args.command == "search": value = [r.__dict__ for r in engine.search(args.query, args.world)]
    elif args.command == "atlas-refresh": value = engine.refresh()
    elif args.command in {"atlas-html", "atlas-view"}: value = {"html": str(generate_atlas_html(engine.router.atlas.output))}
    elif args.command == "atlas-search": value = engine.router.atlas.search(args.query)
    elif args.command == "mine": value = engine.mine(Path(args.path), args.sector)
    elif args.command == "remember": value = engine.remember(args.content, args.sector, args.source)
    elif args.command == "recall": value = [r.__dict__ for r in engine.router.animus.search(args.query, world=engine.root.name, sector=args.sector)]
    elif args.command == "ingest-chat":
        payload = json.loads(Path(args.file).read_text(encoding="utf-8")); messages = payload.get("messages", payload) if isinstance(payload, dict) else payload
        value = engine.ingest_chat(messages, sector=args.sector, source=str(Path(args.file).resolve()), custom_instructions=args.instructions)
    elif args.command == "archive-init": value = engine.router.archive.init()
    elif args.command == "archive-search": value = engine.router.archive.search(args.query)
    elif args.command == "archive-create": value = engine.router.archive.create(args.path, args.content)
    else: raise AssertionError(args.command)
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str) if args.json or not isinstance(value, str) else value)
    return 0


if __name__ == "__main__": raise SystemExit(main())
