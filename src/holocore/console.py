"""Local browser Console for inspecting and editing HoloCore knowledge."""
from __future__ import annotations

import html
import json
import threading
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .animus import Animus
from .archive import Archive
from .commands import COMMANDS
from .config import Config
from .layout import world_paths


def _record(value):
    return asdict(value) if hasattr(value, "__dataclass_fields__") else value


def build_console_payload(root: Path) -> dict:
    root = root.resolve()
    config = Config.load(root=root)
    paths = world_paths(root, config)
    world = config.world_id or root.name
    animus = Animus(config.animus_path)
    try:
        status = animus.status(world=world)
        chats = [_record(item) for item in animus.timeline(world=world, limit=200)]
        shards = [_record(item) for item in animus.shards(world=world)[:200]]
        decks = [_record(item) for item in animus.decks(world=world)]
        chronicle = [_record(item) for item in animus.signal_chronicle(world=world, limit=200)]
    except (KeyError, OSError, ValueError) as exc:
        status = {"ready": False, "error": str(exc), "database": str(config.animus_path)}
        chats, shards, decks, chronicle = [], [], [], []
    archive = Archive(config.vault)
    wiki = []
    for note in archive._notes()[0]:  # bounded by Archive's safety limits
        rel = note.relative_to(archive.vault).as_posix()
        try:
            item = archive.read(rel)
            wiki.append({"path": rel, "title": note.stem, "content": item["content"], "modified": note.stat().st_mtime})
        except (OSError, ValueError):
            continue
    atlas = {"path": paths["atlas_json"], "html": paths["atlas_html"], "exists": Path(paths["atlas_json"]).exists()}
    return {
        "world": world, "root": str(root), "paths": paths, "status": status,
        "chats": chats, "shards": shards, "decks": decks, "chronicle": chronicle,
        "wiki": wiki, "atlas": atlas,
        "commands": [asdict(command) for command in COMMANDS],
    }


def render_console_html(payload: dict) -> str:
    state = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    return """<!doctype html><html><head><meta charset="utf-8"><title>HoloCore Console</title>
<style>body{margin:0;background:#0b1020;color:#dce7ff;font:14px system-ui}header{padding:20px 28px;background:#121a31;display:flex;justify-content:space-between}h1{margin:0;color:#8ee7ff}nav{padding:12px 28px;background:#0f172b;display:flex;gap:8px;flex-wrap:wrap}button{background:#1b2b4d;color:#dce7ff;border:1px solid #35527f;border-radius:6px;padding:8px 12px;cursor:pointer}button.active{background:#2389a8}main{padding:20px 28px;max-width:1400px;margin:auto}.panel{display:none}.panel.active{display:block}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card{background:#121a31;border:1px solid #263b61;border-radius:8px;padding:14px;margin:8px 0}.muted{color:#91a4c7}pre,textarea{width:100%;box-sizing:border-box;background:#080d19;color:#dce7ff;border:1px solid #30486f;border-radius:6px;padding:10px}textarea{min-height:280px}input{background:#080d19;color:#dce7ff;border:1px solid #30486f;padding:8px;border-radius:5px}.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}a{color:#8ee7ff}</style></head><body>
<header><div><h1>HoloCore Console</h1><div class="muted" id="world"></div></div><div class="muted">Home-backed · local only</div></header><nav id="nav"></nav><main id="app"></main><script id="state" type="application/json">"""+state+"""</script>
<script>const S=JSON.parse(document.getElementById('state').textContent);const tabs=['Overview','Chats','Shards','Wiki','Signals','Commands'];let current='Overview';
function esc(x){return String(x??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}function card(title,body){return `<div class="card"><h3>${esc(title)}</h3>${body}</div>`}
function render(){document.getElementById('world').textContent=S.world+' · '+S.root;document.getElementById('nav').innerHTML=tabs.map(t=>`<button class="${t==current?'active':''}" onclick="current='${t}';render()">${t}</button>`).join('');let a='';
if(current==='Overview'){a='<div class="grid">'+card('Animus',`<b>${S.status.memory_shards??0}</b> shards · <b>${S.chats.length}</b> chats`)+card('Atlas',`${S.atlas.exists?'Ready':'Missing'}<br><span class="muted">${esc(S.atlas.path)}</span>`)+card('Locations',Object.entries(S.paths).map(([k,v])=>`<div><b>${esc(k)}</b>: ${esc(v)}</div>`).join(''))+'</div>'}
if(current==='Chats')a=S.chats.length?S.chats.map(x=>card(x.title||x.kind,`<div class="muted">${esc(x.occurred_at)} · ${esc(x.source_ref||'')}</div><pre>${esc(x.content)}</pre>`)).join(''):'<p class="muted">No captured chats in this World.</p>';
if(current==='Shards')a=S.shards.length?S.shards.map(x=>card(x.sector_id||'general',`<div class="muted">${esc(x.created_at)} · ${esc((x.sources||[]).map(y=>y.source_ref).join(', '))}</div><pre>${esc(x.content)}</pre>`)).join(''):'<p class="muted">No Memory Shards in this World.</p>';
if(current==='Wiki')a='<div class="row"><select id="wikiSelect" onchange="loadWiki()">'+S.wiki.map(x=>`<option value="${esc(x.path)}">${esc(x.path)}</option>`).join('')+'</select><button onclick="newWiki()">New note</button><button onclick="saveWiki()">Save</button></div><textarea id="wikiText"></textarea><p class="muted">Edits are validated as AI-first Archive notes and stay inside this World\'s wiki.</p>'; 
if(current==='Signals')a=(S.decks.length?S.decks.map(x=>card('Deck: '+x.name,esc(x.description||''))).join(''):'')+(S.chronicle.length?S.chronicle.map(x=>card(x.relation,`<b>${esc(x.value)}</b><div class="muted">${esc(x.occurred_at)} · ${esc(x.source_ref)}</div>`)).join(''):'<p class="muted">No Signal Chronicle events.</p>');
if(current==='Commands')a='<div class="grid">'+S.commands.map(x=>card(x.name,`${esc(x.description)}<pre>${esc(x.invocation)}</pre>`)).join('')+'</div>';document.getElementById('app').innerHTML=a;if(current==='Wiki'&&S.wiki.length)loadWiki()}
function loadWiki(){let p=document.getElementById('wikiSelect').value;fetch('/api/wiki?path='+encodeURIComponent(p)).then(r=>r.json()).then(x=>document.getElementById('wikiText').value=x.content||'')};function newWiki(){document.getElementById('wikiSelect').innerHTML='<option value="wiki/new-note.md">wiki/new-note.md</option>';document.getElementById('wikiText').value='Write the note here.'};function saveWiki(){let p=document.getElementById('wikiSelect').value;fetch('/api/wiki',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:p,content:document.getElementById('wikiText').value})}).then(r=>r.json()).then(x=>{alert(x.error||'Saved');if(!x.error)location.reload()})};render();</script></body></html>"""


class _Handler(BaseHTTPRequestHandler):
    service = None
    def _send(self, value, status=200, content_type="application/json"):
        data = value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", content_type+"; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/console"}: return self._send(render_console_html(self.service.payload), content_type="text/html")
        if parsed.path == "/api/state": return self._send(self.service.payload)
        if parsed.path == "/api/wiki":
            path = parse_qs(parsed.query).get("path", [""])[0]
            try: return self._send(self.service.archive.read(path))
            except Exception as exc: return self._send({"error": str(exc)}, 400)
        return self._send({"error":"not found"}, 404)
    def do_POST(self):
        if self.path != "/api/wiki": return self._send({"error":"not found"},404)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            path, content = str(body["path"]), str(body["content"])
            try: result = self.service.archive.update(path, body=content)
            except FileNotFoundError: result = self.service.archive.create(path, content)
            self.service.payload = build_console_payload(self.service.root)
            return self._send(result)
        except Exception as exc: return self._send({"error": str(exc)}, 400)
    def log_message(self, *_): pass


class ConsoleService:
    def __init__(self, root: Path):
        self.root = root.resolve(); self.payload = build_console_payload(self.root); self.archive = Archive(Config.load(root=self.root).vault)


def serve_console(root: Path, host: str = "127.0.0.1", port: int = 0, open_browser: bool = True) -> int:
    service = ConsoleService(root); _Handler.service = service
    # Keep one discoverable snapshot in Home; the live server remains the
    # editable surface and is still opened by the CLI.
    home = Path(service.payload["paths"]["home"])
    export_path = home / "Console" / "console.html"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(render_console_html(service.payload), encoding="utf-8")
    server = ThreadingHTTPServer((host, port), _Handler); url = f"http://{host}:{server.server_port}/"
    print(json.dumps({"url": url, "html": str(export_path), "world": service.payload["world"], "close": "Ctrl+C"}, indent=2))
    if open_browser: threading.Timer(0.2, lambda: webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0


def export_console(root: Path) -> Path:
    service = ConsoleService(root)
    path = Path(service.payload["paths"]["home"]) / "Console" / "console.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_console_html(service.payload), encoding="utf-8")
    return path


__all__ = ["build_console_payload", "export_console", "render_console_html", "serve_console"]
