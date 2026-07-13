"""Dependency-free, self-contained HTML rendering for a HoloCore Atlas graph."""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def _validated_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes", [])
    links = graph.get("links", graph.get("edges", []))
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise ValueError("Atlas graph must contain node and link arrays")
    return {**graph, "nodes": nodes, "links": links}


def _script_json(value: Any) -> str:
    # JSON in an application/json script element still needs protection from a
    # literal closing script tag. Escaping HTML-significant characters also
    # keeps arbitrary source labels inert.
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_atlas_html(graph: Mapping[str, Any], *, title: str = "HoloCore Atlas") -> str:
    """Return a standalone HTML document with the complete graph embedded."""
    payload = _script_json(_validated_graph(graph))
    safe_title = (
        title.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif;background:#090d18;color:#e7ecf5}*{box-sizing:border-box}body{margin:0;height:100vh;display:grid;grid-template-rows:auto 1fr}.bar{padding:14px 18px;background:#101728;border-bottom:1px solid #26324b;display:flex;gap:10px;align-items:center;flex-wrap:wrap}.bar strong{margin-right:auto}input,select,button{background:#0b1221;color:#e7ecf5;border:1px solid #33415f;border-radius:7px;padding:8px 10px}input{min-width:240px}.layout{min-height:0;display:grid;grid-template-columns:1fr 300px}#graph{width:100%;height:100%;background:radial-gradient(circle at center,#15203a,#090d18)}aside{overflow:auto;padding:16px;border-left:1px solid #26324b;background:#0d1423}.muted{color:#93a0b8;font-size:13px}.field{margin:8px 0;overflow-wrap:anywhere}svg text{fill:#e7ecf5;font-size:11px;pointer-events:none}.node{cursor:pointer;stroke:#09101d;stroke-width:2}.edge{stroke:#52617d;stroke-opacity:.55;stroke-width:1.2}.edge-label{fill:#8997b0;font-size:9px}.empty{display:grid;place-items:center;color:#93a0b8}
@media(max-width:760px){.layout{grid-template-columns:1fr;grid-template-rows:65vh auto}aside{border-left:0;border-top:1px solid #26324b}}
</style></head><body>
<header class="bar"><strong>__TITLE__</strong><input id="search" type="search" placeholder="Search label, id, or source file" aria-label="Search nodes"><select id="kind" aria-label="Filter node kind"><option value="">All node kinds</option></select><select id="relation" aria-label="Filter relation"><option value="">All relations</option></select><button id="reset" type="button">Reset</button><span id="stats" class="muted"></span></header>
<main class="layout"><div id="graph"></div><aside><h2>Node details</h2><div id="details" class="muted">Select a node to inspect it.</div></aside></main>
<script id="atlas-data" type="application/json">__ATLAS_DATA__</script>
<script>
(()=>{'use strict';const data=JSON.parse(document.getElementById('atlas-data').textContent),allNodes=data.nodes||[],allLinks=data.links||data.edges||[];
const byId=new Map(allNodes.map(n=>[String(n.id),n])),search=document.getElementById('search'),kind=document.getElementById('kind'),relation=document.getElementById('relation'),host=document.getElementById('graph'),details=document.getElementById('details'),stats=document.getElementById('stats');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const endpoint=v=>String(v&&typeof v==='object'?v.id:v);const nodeKind=n=>String(n.kind||n.type||n.file_type||'unknown');
function options(el,values){[...new Set(values.filter(Boolean))].sort().forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;el.appendChild(o)})}options(kind,allNodes.map(nodeKind));options(relation,allLinks.map(e=>String(e.relation||e.type||'')));
function color(s){let h=0;for(const c of s)h=(h*31+c.charCodeAt(0))>>>0;return `hsl(${h%360} 62% 58%)`}
function show(n){const fields=Object.entries(n).filter(([,v])=>v!==null&&v!==''&&typeof v!=='object').map(([k,v])=>`<div class="field"><b>${esc(k)}</b><br>${esc(v)}</div>`).join('');details.innerHTML=fields||'<span class="muted">No details.</span>'}
function draw(){const q=search.value.trim().toLowerCase(),k=kind.value,r=relation.value;let nodes=allNodes.filter(n=>(!k||nodeKind(n)===k)&&(!q||[n.id,n.label,n.source_file,n.module].some(v=>String(v||'').toLowerCase().includes(q))));let ids=new Set(nodes.map(n=>String(n.id)));let links=allLinks.filter(e=>ids.has(endpoint(e.source??e.from))&&ids.has(endpoint(e.target??e.to))&&(!r||String(e.relation||e.type||'')===r));if(r){const connected=new Set(links.flatMap(e=>[endpoint(e.source??e.from),endpoint(e.target??e.to)]));nodes=nodes.filter(n=>connected.has(String(n.id)));ids=connected}stats.textContent=`${nodes.length} / ${allNodes.length} nodes · ${links.length} / ${allLinks.length} links`;host.replaceChildren();if(!nodes.length){host.className='empty';host.textContent='No matching nodes';return}host.className='';const w=Math.max(host.clientWidth,480),h=Math.max(host.clientHeight,360),cx=w/2,cy=h/2,rad=Math.max(80,Math.min(w,h)*.38),pos=new Map();nodes.forEach((n,i)=>{const a=(Math.PI*2*i/nodes.length)-Math.PI/2;pos.set(String(n.id),{x:cx+Math.cos(a)*rad,y:cy+Math.sin(a)*rad})});const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('width','100%');svg.setAttribute('height','100%');links.forEach(e=>{const a=pos.get(endpoint(e.source??e.from)),b=pos.get(endpoint(e.target??e.to));if(!a||!b)return;const line=document.createElementNS(ns,'line');line.setAttribute('class','edge');line.setAttribute('x1',a.x);line.setAttribute('y1',a.y);line.setAttribute('x2',b.x);line.setAttribute('y2',b.y);svg.appendChild(line)});nodes.forEach(n=>{const p=pos.get(String(n.id)),g=document.createElementNS(ns,'g'),c=document.createElementNS(ns,'circle'),t=document.createElementNS(ns,'text');c.setAttribute('class','node');c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r','7');c.setAttribute('fill',color(nodeKind(n)));c.addEventListener('click',()=>show(n));t.setAttribute('x',p.x+10);t.setAttribute('y',p.y+4);t.textContent=String(n.label||n.id);g.append(c,t);svg.appendChild(g)});host.appendChild(svg)}
[search,kind,relation].forEach(el=>el.addEventListener(el===search?'input':'change',draw));document.getElementById('reset').addEventListener('click',()=>{search.value=kind.value=relation.value='';draw()});addEventListener('resize',draw);draw()})();
</script></body></html>'''
    return template.replace("__TITLE__", safe_title).replace("__ATLAS_DATA__", payload)


def generate_atlas_html(
    atlas: str | Path | Mapping[str, Any], output: str | Path | None = None, *, title: str = "HoloCore Atlas"
) -> Path:
    """Read ``atlas.json`` (or accept its mapping), write HTML, and return its path."""
    if isinstance(atlas, Mapping):
        graph = atlas
        if output is None:
            raise ValueError("output is required when atlas is an in-memory mapping")
        destination = Path(output)
    else:
        source = Path(atlas)
        try:
            graph = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read Atlas graph {source}: {exc}") from exc
        destination = Path(output) if output is not None else source.with_suffix(".html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_atlas_html(graph, title=title), encoding="utf-8", newline="\n")
    return destination


write_atlas_html = generate_atlas_html
build_atlas_html = generate_atlas_html

__all__ = ["render_atlas_html", "generate_atlas_html", "write_atlas_html", "build_atlas_html"]
