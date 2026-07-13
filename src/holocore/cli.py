from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .atlas_html import generate_atlas_html
from .config import Config
from .engine import HoloCoreEngine
from .layout import format_paths, world_paths


PLATFORMS = ("claude", "codex", "gemini", "cursor", "opencode", "generic")


def _platform_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--platform", action="append", choices=PLATFORMS, help="Configure only this AI client (repeatable). Default: all clients.")


def _format_setup(value: dict) -> str:
    paths = value["paths"]
    atlas = value["atlas"]
    return f"""HoloCore is ready.

World
  {value['world']}

Your data
  Archive / Obsidian vault   {paths['archive']}
  Archive Entries           {paths['archive_entries']}
  Atlas graph               {paths['atlas_json']} ({atlas['nodes']} signals)
  Atlas visual              {paths['atlas_html']}
  Memory Shards             {paths['memory_shards']}
  Raw chat audit            {paths['raw_chats']}

AI access
  Claude Code: restart in this World, run /mcp once, then /holocore-search
  Codex: restart/reopen this World, then invoke $holocore-search
  Other MCP clients: use the generated project-local MCP configuration

Obsidian is optional. To use it, open this folder as a vault:
  {paths['archive']}

Full local guide:
  {paths['start_here']}"""


def _format_connect(value: dict) -> str:
    changed = len(value.get("created", [])) + len(value.get("updated", []))
    warnings = value.get("warnings", [])
    suffix = "\n\nWarnings:\n  " + "\n  ".join(warnings) if warnings else ""
    return f"""HoloCore AI connections are installed ({changed} files created or repaired).

Claude Code
  Config: {value['paths']['claude_mcp']}
  Restart Claude, run /mcp to approve/check the server, then /holocore-search.

Codex
  Config: {value['paths']['codex_mcp']}
  Skills: {value['paths']['codex_skills']}
  Restart/reopen the World, then invoke $holocore-search.{suffix}"""


def _format_status(value: dict) -> str:
    ready = value["readiness"]["ready"]
    claude = value["integrations"]["claude"]
    codex = value["integrations"]["codex"]
    return f"""HoloCore {'is ready' if ready else 'needs attention'}.

World:   {value['world']}
Archive: {value['paths']['archive']}
Atlas:   {value['paths']['atlas_json']} ({'fresh' if value['atlas'].get('fresh') else 'missing or stale'})
Animus:  {value['paths']['memory_shards']}

AI connections
  Claude Code: {'connected' if claude['connected'] else claude['detail']} · {claude['slash_commands']} slash commands · {claude['skills']} skills
  Codex:       {'connected' if codex['connected'] else codex['detail']} · {codex['skills']} skills

Run `holocore paths` for every location or `holocore connect` to repair AI connections."""


def _open_folder(path: Path) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def main() -> int:
    parser = argparse.ArgumentParser(prog="holocore", description="Unified local knowledge engine")
    parser.add_argument("--root", default=".", help="World/project directory (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Print stable machine-readable JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup", help="One-command World setup and AI connection")
    setup.add_argument("path", nargs="?")
    setup.add_argument("--git", action="store_true", help="Initialize Git if needed (off by default)")
    _platform_options(setup)
    init = sub.add_parser("init", help="Initialize storage and integrations without building Atlas")
    init.add_argument("path", nargs="?")
    init.add_argument("--no-git", action="store_true")
    _platform_options(init)
    connect = sub.add_parser("connect", help="Install or repair AI client connections")
    connect.add_argument("path", nargs="?")
    _platform_options(connect)
    sub.add_parser("paths", help="Show every HoloCore data and integration location")
    sub.add_parser("open-archive", help="Open the visible Archive folder")
    sub.add_parser("status")
    sub.add_parser("doctor")
    search = sub.add_parser("search"); search.add_argument("query"); search.add_argument("--world")
    sub.add_parser("atlas-refresh")
    sub.add_parser("atlas-html"); sub.add_parser("atlas-view")
    atlas_search = sub.add_parser("atlas-search"); atlas_search.add_argument("query")
    mine = sub.add_parser("mine"); mine.add_argument("path", nargs="?", default="."); mine.add_argument("--sector", default="project")
    remember = sub.add_parser("remember"); remember.add_argument("content"); remember.add_argument("--sector", default="general"); remember.add_argument("--source", default="")
    recall = sub.add_parser("recall"); recall.add_argument("query"); recall.add_argument("--sector")
    ingest = sub.add_parser("ingest-chat"); ingest.add_argument("file"); ingest.add_argument("--sector", default="conversations"); ingest.add_argument("--instructions", default="")
    sub.add_parser("archive-init")
    archive_search = sub.add_parser("archive-search"); archive_search.add_argument("query")
    archive_create = sub.add_parser("archive-create"); archive_create.add_argument("path"); archive_create.add_argument("content")
    args = parser.parse_args()
    root = Path(getattr(args, "path", None) or args.root).resolve() if args.command in {"setup", "init", "connect"} else Path(args.root).resolve()

    if args.command == "paths":
        value = world_paths(root, Config.load(root=root))
        output = json.dumps(value, indent=2) if args.json else format_paths(value)
        print(output)
        return 0
    if args.command == "open-archive":
        archive = Config.load(root=root).vault
        if not archive.is_dir():
            parser.error(f"Archive does not exist yet: {archive}. Run `holocore setup` first.")
        _open_folder(archive)
        value = {"opened": str(archive)}
        print(json.dumps(value, indent=2) if args.json else f"Opened Archive: {archive}")
        return 0

    engine = HoloCoreEngine(root)
    if args.command == "setup": value = engine.setup(git=args.git, platforms=args.platform)
    elif args.command == "init": value = engine.initialize(git=not args.no_git, platforms=args.platform)
    elif args.command == "connect": value = engine.connect(platforms=args.platform)
    elif args.command in {"status", "doctor"}: value = engine.status()
    elif args.command == "search": value = [r.__dict__ for r in engine.search(args.query, args.world)]
    elif args.command == "atlas-refresh": value = engine.refresh()
    elif args.command in {"atlas-html", "atlas-view"}:
        html = generate_atlas_html(engine.router.atlas.output)
        if args.command == "atlas-view":
            import webbrowser
            webbrowser.open(html.resolve().as_uri())
        value = {"html": str(html), "opened": args.command == "atlas-view"}
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

    if args.json:
        output = json.dumps(value, indent=2, ensure_ascii=False, default=str)
    elif args.command == "setup": output = _format_setup(value)
    elif args.command in {"init", "connect"}: output = _format_connect(value)
    elif args.command in {"status", "doctor"}: output = _format_status(value)
    else: output = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, default=str)
    print(output)
    return 0


if __name__ == "__main__": raise SystemExit(main())
