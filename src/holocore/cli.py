from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .config import Config
from .engine import HoloCoreEngine
from .home import HomeManager
from .layout import format_paths, world_paths
from .lifecycle import installation_check, sync_all, uninstall_tool, update_install
from .animus import Animus
from .animus_mining import AnimusMiner, MiningOptions
from .animus_retrieval import AnimusRetriever
from .archive_source import sync_archive_source
from . import __version__


PLATFORMS = ("claude", "codex", "gemini", "cursor", "opencode", "generic")


def _platform_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--platform", action="append", choices=PLATFORMS, help="Configure only this AI client (repeatable). Default: all clients.")


def _selected_home(explicit: str | None) -> Path:
    manager = HomeManager(explicit)
    if explicit or manager.pointer_path.exists():
        return manager.home
    default = manager.default_home
    if sys.stdin.isatty():
        answer = input(f"Where should HoloCore store the shared second brain? [{default}] ").strip()
        return Path(answer).expanduser().resolve() if answer else default
    return default


def _format_setup(value: dict) -> str:
    paths = value["paths"]
    atlas = value["atlas"]
    return f"""HoloCore is ready.

World
  {value['world']}

Your data
  HoloCore Home             {paths['home']}
  Shared Obsidian vault     {paths['archive']}
  This World's Archive     {paths['world_archive']}
  Atlas graph               {paths['atlas_json']} ({atlas['nodes']} signals)
  Atlas visual              {paths['atlas_html']}
  Memory Shards             {paths['memory_shards']}
  Raw chat audit            {paths['raw_chats']}
  Source Inbox              {paths['ingest_inbox']}
  Immutable raw sources     {paths['raw_sources']}

AI access
  Claude Code: restart in this World, run /mcp once, then /holocore-search (capture installed)
  Codex: restart/reopen this World, review /hooks once, then invoke $holocore-search (capture installed)
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
  Claude Code: {'connected' if claude['connected'] else claude['detail']} · capture {'on' if claude['capture'] else 'off'} · {claude['slash_commands']} slash commands · {claude['skills']} skills
  Codex:       {'connected' if codex['connected'] else codex['detail']} · capture {'on' if codex['capture'] else 'off'} · {codex['skills']} skills

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
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--root", default=".", help="World/project directory (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Print stable machine-readable JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup", help="One-command World setup and AI connection")
    setup.add_argument("path", nargs="?")
    setup.add_argument("--git", action="store_true", help="Initialize Git if needed (off by default)")
    setup.add_argument("--home", help="Shared HoloCore Home directory; first setup prompts when omitted")
    _platform_options(setup)
    init = sub.add_parser("init", help="Initialize storage and integrations without building Atlas")
    init.add_argument("path", nargs="?")
    init.add_argument("--no-git", action="store_true")
    init.add_argument("--home", help="Shared HoloCore Home directory")
    _platform_options(init)
    connect = sub.add_parser("connect", help="Install or repair AI client connections")
    connect.add_argument("path", nargs="?")
    connect.add_argument("--home", help="Shared HoloCore Home directory")
    _platform_options(connect)
    sub.add_parser("paths", help="Show every HoloCore data and integration location")
    sub.add_parser("open-archive", help="Open the visible Archive folder")
    sub.add_parser("status")
    sub.add_parser("doctor")
    home_command = sub.add_parser("home", help="Show or select the shared HoloCore Home")
    home_command.add_argument("path", nargs="?")
    home_command.add_argument("--path", dest="home_path", help="Shared HoloCore Home directory (alternative to the positional path)")
    sub.add_parser("worlds", help="List projects linked to the shared brain")
    global_graph = sub.add_parser("global-graph", help="Build an Atlas-only graph across registered Worlds")
    global_graph.add_argument("--output")
    sub.add_parser("sync-all", help="Reconcile every registered World")
    update = sub.add_parser("update", help="Update HoloCore and reconcile every World")
    update.add_argument("--no-sync", action="store_true", help="Only update the CLI; skip the potentially lengthy World/Atlas reconciliation")
    sub.add_parser("install-check", help="Show installed version and safe upgrade/uninstall commands")
    sub.add_parser("uninstall", help="Uninstall the HoloCore CLI while preserving project and Home data")
    search = sub.add_parser("search"); search.add_argument("query"); search.add_argument("--world")
    sub.add_parser("atlas-refresh")
    sub.add_parser("atlas-html"); sub.add_parser("atlas-view")
    atlas_search = sub.add_parser("atlas-search"); atlas_search.add_argument("query")
    atlas_explain = sub.add_parser("atlas-explain"); atlas_explain.add_argument("query")
    atlas_path = sub.add_parser("atlas-path"); atlas_path.add_argument("source"); atlas_path.add_argument("target"); atlas_path.add_argument("--max-depth", type=int)
    atlas_affected = sub.add_parser("atlas-affected"); atlas_affected.add_argument("query"); atlas_affected.add_argument("--depth", type=int, default=2)
    atlas_neighborhood = sub.add_parser("atlas-neighborhood"); atlas_neighborhood.add_argument("query"); atlas_neighborhood.add_argument("--depth", type=int, default=1)
    atlas_export = sub.add_parser("atlas-export"); atlas_export.add_argument("output"); atlas_export.add_argument("--format", action="append", dest="formats")
    sub.add_parser("atlas-audit")
    atlas_constellations = sub.add_parser("atlas-constellations"); atlas_constellations.add_argument("--min-size", type=int, default=2)
    mine = sub.add_parser("mine"); mine.add_argument("path", nargs="?", default="."); mine.add_argument("--sector", default="project"); mine.add_argument("--mode", choices=("files", "conversations", "git"), default="files"); mine.add_argument("--ignore", action="append", default=[])
    sync = sub.add_parser("animus-sync"); sync.add_argument("--sector", default="project"); sync.add_argument("--mode", choices=("files", "conversations", "git"), default="files")
    checkpoint = sub.add_parser("animus-checkpoint"); checkpoint.add_argument("--sector", default="project"); checkpoint.add_argument("--mode", choices=("files", "conversations", "git"), default="files"); checkpoint.add_argument("--source", default="")
    diary = sub.add_parser("diary"); diary.add_argument("content"); diary.add_argument("--title", default=""); diary.add_argument("--sector", default="project"); diary.add_argument("--kind", default="episode"); diary.add_argument("--source", default="cli")
    timeline = sub.add_parser("timeline"); timeline.add_argument("--sector", default=None); timeline.add_argument("--limit", type=int, default=100)
    consolidate = sub.add_parser("consolidate"); consolidate.add_argument("--sector", default=None)
    export = sub.add_parser("animus-export"); export.add_argument("--sector", default=None); export.add_argument("--limit", type=int, default=1000)
    remember = sub.add_parser("remember"); remember.add_argument("content"); remember.add_argument("--sector", default="general"); remember.add_argument("--source", default="")
    recall = sub.add_parser("recall"); recall.add_argument("query"); recall.add_argument("--sector")
    ingest = sub.add_parser("ingest-chat"); ingest.add_argument("file"); ingest.add_argument("--sector", default="conversations"); ingest.add_argument("--instructions", default="")
    source_ingest = sub.add_parser("ingest", help="Ingest a file, folder, or URL")
    source_ingest.add_argument("source")
    source_ingest.add_argument("--title")
    sub.add_parser("inbox-sync", help="Ingest new files from the visible World Inbox")
    sub.add_parser("archive-init")
    archive_search = sub.add_parser("archive-search"); archive_search.add_argument("query")
    archive_create = sub.add_parser("archive-create"); archive_create.add_argument("path"); archive_create.add_argument("content")
    archive_source = sub.add_parser("archive-source-sync", help="One-way sync curated Markdown into the Shared Archive")
    archive_source.add_argument("--source", required=True, help="Existing curated Markdown directory")
    args = parser.parse_args()
    root = Path(getattr(args, "path", None) or args.root).resolve() if args.command in {"setup", "init", "connect"} else Path(args.root).resolve()

    if args.command == "paths":
        value = world_paths(root, Config.load(root=root))
        output = json.dumps(value, indent=2) if args.json else format_paths(value)
        print(output)
        return 0
    if args.command == "home":
        manager = HomeManager()
        selected_path = args.home_path or args.path
        value = manager.select_home(selected_path) if selected_path else {
            "home": str(manager.home), "archive": str(manager.archive), "worlds_file": str(manager.worlds_path), "selected": manager.pointer_path.exists()
        }
        print(json.dumps(value, indent=2, default=str) if args.json else f"HoloCore Home: {value['home']}\nShared Archive: {Path(value['home']) / 'Archive'}\nWorld registry: {Path(value['home']) / 'worlds.json'}")
        return 0
    if args.command == "worlds":
        value = HomeManager().list_worlds()
        if args.json:
            print(json.dumps(value, indent=2, default=str))
        else:
            lines = [f"Registered Worlds ({value['count']}):"] + [f"  {item['name']}  {item['root']}" for item in value["worlds"]]
            print("\n".join(lines))
        return 0
    if args.command == "global-graph":
        from .global_graph import build_global_graph
        manager = HomeManager()
        output = Path(args.output).expanduser() if args.output else manager.home / "global-graph" / "graph.json"
        value = build_global_graph(manager.home, output=output)
        print(json.dumps(value, indent=2, default=str) if args.json else f"Global Atlas written to {value['path']}")
        return 0
    if args.command == "sync-all":
        value = sync_all()
        print(json.dumps(value, indent=2, default=str) if args.json else f"Reconciled {value['updated']} of {value['count']} Worlds ({value['failed']} failed).")
        return 0
    if args.command == "update":
        value = update_install(reconcile=not args.no_sync)
        reconciliation = value["reconciliation"]
        if args.json:
            print(json.dumps(value, indent=2, default=str))
        elif reconciliation is None:
            print("HoloCore updated. World reconciliation skipped. Run `holocore sync-all` when ready.")
        else:
            print(f"HoloCore updated. Reconciled {reconciliation['updated']} of {reconciliation['count']} Worlds.")
        return 0
    if args.command == "install-check":
        value = installation_check()
        print(json.dumps(value, indent=2) if args.json else f"Installed HoloCore: {value['installed_version']}\nUpdate: {value['upgrade_command']}\nUninstall: {value['uninstall_command']}\nProject and Home data are preserved.")
        return 0
    if args.command == "uninstall":
        value = uninstall_tool()
        print(json.dumps(value, indent=2) if args.json else "HoloCore CLI uninstalled. Project and Home data were preserved.")
        return 0
    if args.command == "open-archive":
        config = Config.load(root=root)
        archive = (config.home / "Archive") if config.home else config.vault
        if not archive.is_dir():
            parser.error(f"Archive does not exist yet: {archive}. Run `holocore setup` first.")
        _open_folder(archive)
        value = {"opened": str(archive)}
        print(json.dumps(value, indent=2) if args.json else f"Opened Archive: {archive}")
        return 0

    engine = HoloCoreEngine(root)
    if args.command == "setup": value = engine.setup(git=args.git, platforms=args.platform, home=_selected_home(args.home))
    elif args.command == "init": value = engine.initialize(git=not args.no_git, platforms=args.platform, home=_selected_home(args.home))
    elif args.command == "connect": value = engine.connect(platforms=args.platform, home=_selected_home(args.home))
    elif args.command in {"status", "doctor"}: value = engine.status()
    elif args.command == "search": value = [r.__dict__ for r in engine.search(args.query, args.world)]
    elif args.command == "atlas-refresh": value = engine.refresh()
    elif args.command in {"atlas-html", "atlas-view"}:
        atlas = engine.ensure_atlas()
        html = Path(atlas["html"])
        if args.command == "atlas-view":
            import webbrowser
            webbrowser.open(html.resolve().as_uri())
        value = {**atlas, "html": str(html), "opened": args.command == "atlas-view"}
    elif args.command == "atlas-search": value = engine.router.atlas.search(args.query)
    elif args.command == "atlas-explain": value = engine.router.atlas.explain(args.query)
    elif args.command == "atlas-path": value = engine.router.atlas.shortest_path(args.source, args.target, max_depth=args.max_depth)
    elif args.command == "atlas-affected": value = engine.router.atlas.affected(args.query, depth=args.depth)
    elif args.command == "atlas-neighborhood": value = engine.router.atlas.neighborhood(args.query, depth=args.depth)
    elif args.command == "atlas-audit": value = engine.router.atlas.audit()
    elif args.command == "atlas-constellations": value = engine.router.atlas.constellations(min_size=args.min_size)
    elif args.command == "atlas-export":
        from .atlas_exports import export_atlas
        value = export_atlas(engine.router.atlas, args.output, args.formats)
    elif args.command in {"mine", "animus-sync", "animus-checkpoint", "diary", "timeline", "consolidate", "animus-export"}:
        config = Config.load(root=root); animus = Animus(config.animus_path); world = config.world_id or root.name
        animus.create_world(world, root.name, {"root": str(root)})
        if getattr(args, "sector", None): animus.create_sector(world, args.sector)
        if args.command in {"mine", "animus-sync"}:
            path = Path(args.path if args.command == "mine" else root).resolve()
            value = AnimusMiner(animus).mine(MiningOptions(mode=args.mode, world=world, sector=args.sector, root=path, ignore=tuple(args.ignore) or MiningOptions().ignore))
        elif args.command == "animus-checkpoint":
            source = args.source or str(root.resolve()); value = animus.get_checkpoint(world=world, sector=args.sector, mode=args.mode, source_ref=source)
        elif args.command == "diary": value = animus.record_diary(args.content, world=world, sector=args.sector, title=args.title, kind=args.kind, source_ref=args.source)
        elif args.command == "timeline": value = animus.timeline(world=world, sector=args.sector, limit=args.limit)
        elif args.command == "consolidate": value = animus.consolidate(world=world, sector=args.sector)
        else: value = [{"id": row.id, "world_id": row.world_id, "sector_id": row.sector_id, "occurred_at": row.occurred_at, "title": row.title, "content": row.content, "kind": row.kind, "metadata": dict(row.metadata), "provenance": [p.__dict__ for p in row.provenance]} for row in animus.timeline(world=world, sector=args.sector, limit=args.limit)]
    elif args.command == "remember": value = engine.remember(args.content, args.sector, args.source)
    elif args.command == "recall":
        engine.router.ensure_memory_scope()
        value = [r.__dict__ for r in engine.router.animus.search(args.query, world=engine.router.world_id, sector=args.sector)]
    elif args.command == "ingest-chat":
        payload = json.loads(Path(args.file).read_text(encoding="utf-8")); messages = payload.get("messages", payload) if isinstance(payload, dict) else payload
        value = engine.ingest_chat(messages, sector=args.sector, source=str(Path(args.file).resolve()), custom_instructions=args.instructions)
    elif args.command == "ingest": value = engine.ingest_source(args.source, title=args.title)
    elif args.command == "inbox-sync": value = engine.sync_inbox()
    elif args.command == "archive-init": value = engine.router.archive.init_vault()
    elif args.command == "archive-search": value = engine.router.archive.search(args.query)
    elif args.command == "archive-create": value = engine.router.archive.create(args.path, args.content)
    elif args.command == "archive-source-sync": value = sync_archive_source(args.source, HomeManager().home)
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
