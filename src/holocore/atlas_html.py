"""Dependency-free, self-contained HTML rendering for a HoloCore Atlas graph."""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


ATLAS_VIEWER_VERSION = "3"


def _validated_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes", [])
    links = graph.get("links", graph.get("edges", []))
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise ValueError("Atlas graph must contain node and link arrays")
    return {**graph, "nodes": nodes, "links": links}


def _script_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_atlas_html(graph: Mapping[str, Any], *, title: str = "HoloCore Atlas") -> str:
    """Return an accessible standalone force-directed Atlas viewer."""
    payload = _script_json(_validated_graph(graph))
    safe_title = (
        title.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )
    template = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="holocore-atlas-viewer" content="3">
<title>__TITLE__</title><style>
:root{color-scheme:dark;font-family:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;background:#0f172a;color:#f8fafc;--panel:#111c30;--line:#334155;--muted:#a8b4c5;--focus:#38bdf8;--accent:#22c55e}*{box-sizing:border-box}body{margin:0;height:100vh;overflow:hidden;display:grid;grid-template-rows:auto 1fr;background:#0f172a}.bar{z-index:2;min-height:64px;padding:10px 14px;background:#111c30;border-bottom:1px solid #334155;display:flex;gap:8px;align-items:center;flex-wrap:wrap;box-shadow:0 4px 18px #02061766}.brand{display:flex;align-items:center;gap:10px;margin-right:auto}.brand-mark{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:#0ea5e9;color:#03121f;font:700 17px "JetBrains Mono",monospace}.brand strong{font-size:16px;letter-spacing:.01em}.control{height:40px;background:#0b1324;color:#e2e8f0;border:1px solid #475569;border-radius:8px;padding:0 11px;font:inherit}.control:hover{border-color:#64748b}.control:focus-visible,button:focus-visible{outline:3px solid #38bdf8;outline-offset:2px}input.control{width:min(290px,42vw)}button.control{cursor:pointer;min-width:40px;font-weight:600}.icon-button{font-size:18px;padding:0 12px}.layout{min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 320px}#graph{position:relative;min-width:0;min-height:0;background:radial-gradient(circle at 48% 45%,#172554 0,#111c30 30%,#0b1324 68%,#07101e 100%);overflow:hidden;touch-action:none}.canvas-help{position:absolute;left:14px;bottom:12px;z-index:1;padding:7px 10px;border:1px solid #334155;border-radius:8px;background:#0f172add;color:#b8c4d4;font-size:12px;pointer-events:none}.loading{position:absolute;inset:0;display:grid;place-items:center;color:#cbd5e1;font-size:14px;background:#0b1324}.loading[hidden]{display:none}aside{overflow:auto;padding:18px;border-left:1px solid #334155;background:#111c30}aside h2{font-size:16px;margin:0 0 14px}.muted{color:#a8b4c5;font-size:13px;line-height:1.45}.field{margin:0 0 13px;overflow-wrap:anywhere}.field b{display:block;margin-bottom:3px;color:#e2e8f0;font-size:12px;text-transform:uppercase;letter-spacing:.05em}.legend{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px}.chip{display:inline-flex;align-items:center;gap:6px;padding:4px 7px;border:1px solid #334155;border-radius:999px;color:#cbd5e1;font-size:11px}.dot{width:8px;height:8px;border-radius:50%}svg{display:block;width:100%;height:100%;cursor:grab}svg.panning{cursor:grabbing}.edge{stroke:#64748b;stroke-opacity:.28;stroke-width:1}.edge.active{stroke:#7dd3fc;stroke-opacity:.8;stroke-width:1.7}.node{cursor:pointer;stroke:#0f172a;stroke-width:2;transition:stroke-width .15s,filter .15s}.node:hover,.node.selected{stroke:#f8fafc;stroke-width:3;filter:drop-shadow(0 0 5px #38bdf8)}.label{fill:#cbd5e1;font-size:11px;font-weight:500;paint-order:stroke;stroke:#0b1324;stroke-width:4px;stroke-linejoin:round;pointer-events:none;opacity:0}.label.major,.label.match,.node-group:hover .label,.node-group.selected .label{opacity:1}.label.suppressed{opacity:0}.node-group:hover .label.suppressed,.node-group.selected .label.suppressed{opacity:1}.empty{position:absolute;inset:0;display:grid;place-items:center;color:#b8c4d4}.toggle{display:flex;align-items:center;gap:6px;color:#cbd5e1;font-size:12px;padding:0 4px}.toggle input{accent-color:#22c55e}.stats{min-width:160px;text-align:right}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:900px){body{overflow:auto;height:auto;min-height:100vh}.layout{grid-template-columns:1fr;grid-template-rows:70vh auto}.stats{width:100%;text-align:left}.bar{position:sticky;top:0}.layout aside{border-left:0;border-top:1px solid #334155;min-height:260px}input.control{width:min(100%,320px)}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style></head><body>
<header class="bar"><div class="brand"><span class="brand-mark" aria-hidden="true">H</span><strong>__TITLE__</strong></div><label class="sr-only" for="search">Search Signals</label><input id="search" class="control" type="search" placeholder="Search concepts, decisions, or sources" autocomplete="off"><select id="mode" class="control" aria-label="Atlas view"><option value="knowledge">Knowledge</option><option value="structure">Code structure</option><option value="all">Everything</option></select><select id="kind" class="control" aria-label="Filter Signal type"><option value="">All Signal types</option></select><select id="relation" class="control" aria-label="Filter relationship"><option value="">All relationships</option></select><button id="zoomOut" class="control icon-button" type="button" aria-label="Zoom out">−</button><button id="fit" class="control" type="button">Fit</button><button id="zoomIn" class="control icon-button" type="button" aria-label="Zoom in">+</button><button id="reset" class="control" type="button">Reset</button><label class="toggle"><input id="labels" type="checkbox"> More labels</label><span id="stats" class="muted stats" aria-live="polite"></span></header>
<main class="layout"><div id="graph"><div id="loading" class="loading">Arranging the Atlas…</div><div class="canvas-help">Drag nodes · drag background to pan · scroll to zoom</div></div><aside><h2>Signal details</h2><div id="details" class="muted">Select a Signal to inspect its source, type, and relationships.</div><div id="legend" class="legend" aria-label="Signal type legend"></div></aside></main>
<script id="atlas-data" type="application/json">__ATLAS_DATA__</script>
<script>
(()=>{'use strict';
const data=JSON.parse(document.getElementById('atlas-data').textContent),allNodes=data.nodes||[],allLinks=data.links||data.edges||[];
const byId=new Map(allNodes.map(n=>[String(n.id),n])),search=document.getElementById('search'),mode=document.getElementById('mode'),kind=document.getElementById('kind'),relation=document.getElementById('relation'),host=document.getElementById('graph'),details=document.getElementById('details'),stats=document.getElementById('stats'),loading=document.getElementById('loading'),moreLabels=document.getElementById('labels');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const endpoint=v=>String(v&&typeof v==='object'?v.id:v),nodeKind=n=>String(n.kind||n.type||n.file_type||'unknown');
const isKnowledge=n=>Boolean(n.semantic)||String(n.source_file||'').startsWith('.knowledge/');
if(!allNodes.some(isKnowledge))mode.value='all';
const palette=['#38bdf8','#22c55e','#f59e0b','#a78bfa','#f472b6','#2dd4bf','#fb7185','#94a3b8'];
const hash=s=>{let h=2166136261;for(const c of String(s)){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0};
const color=s=>palette[hash(s)%palette.length];
function options(el,values){[...new Set(values.filter(Boolean))].sort().forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;el.appendChild(o)})}
options(kind,allNodes.map(nodeKind));options(relation,allLinks.map(e=>String(e.relation||e.type||'')));
document.getElementById('legend').innerHTML=[...new Set(allNodes.map(nodeKind))].sort().slice(0,16).map(k=>`<span class="chip"><span class="dot" style="background:${color(k)}"></span>${esc(k)}</span>`).join('');
function show(n,degree){const fields=[['Label',n.label||n.id],['Type',nodeKind(n)],['Connections',degree],...Object.entries(n).filter(([k,v])=>!['label','kind','type'].includes(k)&&v!==null&&v!==''&&typeof v!=='object')];details.innerHTML=fields.map(([k,v])=>`<div class="field"><b>${esc(k)}</b>${esc(v)}</div>`).join('')||'<span class="muted">No details.</span>'}
let svg,viewport,transform={x:0,y:0,k:1},positions=new Map(),selected=null,visibleNodes=[],visibleLinks=[],degrees=new Map();
function forceLayout(nodes,links,w,h){const pos=new Map(),vel=new Map(),degree=new Map(nodes.map(n=>[String(n.id),0]));links.forEach(e=>{const a=endpoint(e.source??e.from),b=endpoint(e.target??e.to);degree.set(a,(degree.get(a)||0)+1);degree.set(b,(degree.get(b)||0)+1)});const kinds=[...new Set(nodes.map(nodeKind))].sort(),kindIndex=new Map(kinds.map((k,i)=>[k,i]));nodes.forEach(n=>{const seed=hash(n.id),angle=(seed%6283)/1000,spread=70+((seed>>>8)%1000)/1000*Math.min(w,h)*.32,cluster=(kindIndex.get(nodeKind(n))||0)/Math.max(1,kinds.length)*Math.PI*2;pos.set(String(n.id),{x:w/2+Math.cos(angle)*spread+Math.cos(cluster)*w*.16,y:h/2+Math.sin(angle)*spread+Math.sin(cluster)*h*.16});vel.set(String(n.id),{x:0,y:0})});const iterations=nodes.length>1200?45:nodes.length>500?70:120,cell=44;for(let step=0;step<iterations;step++){const grid=new Map();nodes.forEach(n=>{const p=pos.get(String(n.id)),key=`${Math.floor(p.x/cell)},${Math.floor(p.y/cell)}`;(grid.get(key)||grid.set(key,[]).get(key)).push(n)});for(const n of nodes){const id=String(n.id),p=pos.get(id),v=vel.get(id),ci=Math.floor(p.x/cell),cj=Math.floor(p.y/cell);v.x+=(w/2-p.x)*.0008;v.y+=(h/2-p.y)*.0008;for(let i=ci-1;i<=ci+1;i++)for(let j=cj-1;j<=cj+1;j++)for(const other of grid.get(`${i},${j}`)||[]){const oid=String(other.id);if(oid===id||oid<id)continue;const q=pos.get(oid),ov=vel.get(oid),dx=p.x-q.x,dy=p.y-q.y,d=Math.max(1,Math.hypot(dx,dy)),min=18+Math.min(12,(degree.get(id)||0)+(degree.get(oid)||0));if(d<min){const f=(min-d)*.018,fx=dx/d*f,fy=dy/d*f;v.x+=fx;v.y+=fy;ov.x-=fx;ov.y-=fy}}}for(const e of links){const a=endpoint(e.source??e.from),b=endpoint(e.target??e.to),p=pos.get(a),q=pos.get(b);if(!p||!q)continue;const av=vel.get(a),bv=vel.get(b),dx=q.x-p.x,dy=q.y-p.y,d=Math.max(1,Math.hypot(dx,dy)),target=58+Math.min(55,Math.log2(2+(degree.get(a)||0)+(degree.get(b)||0))*9),f=(d-target)*.0028,fx=dx/d*f,fy=dy/d*f;av.x+=fx;av.y+=fy;bv.x-=fx;bv.y-=fy}for(const n of nodes){const id=String(n.id),p=pos.get(id),v=vel.get(id);v.x*=.78;v.y*=.78;p.x=Math.max(18,Math.min(w-18,p.x+v.x));p.y=Math.max(18,Math.min(h-18,p.y+v.y))}}return{pos,degree}}
function applyTransform(){if(viewport)viewport.setAttribute('transform',`translate(${transform.x} ${transform.y}) scale(${transform.k})`)}
function fit(){transform={x:0,y:0,k:1};applyTransform()}
function zoom(factor,cx=host.clientWidth/2,cy=host.clientHeight/2){const next=Math.max(.18,Math.min(6,transform.k*factor));transform.x=cx-(cx-transform.x)*(next/transform.k);transform.y=cy-(cy-transform.y)*(next/transform.k);transform.k=next;applyTransform()}
function deconflictLabels(layer){const placed=[];layer.querySelectorAll('.label.major,.label.match').forEach(label=>{label.classList.remove('suppressed');const b=label.getBBox(),box={x:b.x-3,y:b.y-2,w:b.width+6,h:b.height+4};if(placed.some(p=>box.x<p.x+p.w&&box.x+box.w>p.x&&box.y<p.y+p.h&&box.y+box.h>p.y))label.classList.add('suppressed');else placed.push(box)})}
function draw(){loading.hidden=false;requestAnimationFrame(()=>{const q=search.value.trim().toLowerCase(),m=mode.value,k=kind.value,r=relation.value;let nodes=allNodes.filter(n=>(m==='all'||(m==='knowledge'&&isKnowledge(n))||(m==='structure'&&!isKnowledge(n)))&&(!k||nodeKind(n)===k)&&(!q||[n.id,n.label,n.source_file,n.module,n.qualified_name].some(v=>String(v||'').toLowerCase().includes(q))));let ids=new Set(nodes.map(n=>String(n.id)));let links=allLinks.filter(e=>ids.has(endpoint(e.source??e.from))&&ids.has(endpoint(e.target??e.to))&&(!r||String(e.relation||e.type||'')===r));if(r){const connected=new Set(links.flatMap(e=>[endpoint(e.source??e.from),endpoint(e.target??e.to)]));nodes=nodes.filter(n=>connected.has(String(n.id)));ids=connected}visibleNodes=nodes;visibleLinks=links;stats.textContent=`${nodes.length} ${m} Signals · ${links.length} relationships`;host.querySelectorAll('svg,.empty').forEach(el=>el.remove());if(!nodes.length){const e=document.createElement('div');e.className='empty';e.textContent='No matching Signals';host.appendChild(e);loading.hidden=true;return}const w=Math.max(host.clientWidth,500),h=Math.max(host.clientHeight,380),laid=forceLayout(nodes,links,w,h);positions=laid.pos;degrees=laid.degree;const ns='http://www.w3.org/2000/svg';svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',`Atlas graph with ${nodes.length} Signals and ${links.length} relationships`);viewport=document.createElementNS(ns,'g');const edgeLayer=document.createElementNS(ns,'g'),nodeLayer=document.createElementNS(ns,'g');viewport.append(edgeLayer,nodeLayer);svg.appendChild(viewport);const connected=new Map();links.forEach(e=>{const a=endpoint(e.source??e.from),b=endpoint(e.target??e.to),p=positions.get(a),q=positions.get(b);if(!p||!q)return;(connected.get(a)||connected.set(a,[]).get(a)).push(b);(connected.get(b)||connected.set(b,[]).get(b)).push(a);const line=document.createElementNS(ns,'line');line.setAttribute('class','edge');line.dataset.a=a;line.dataset.b=b;line.setAttribute('x1',p.x);line.setAttribute('y1',p.y);line.setAttribute('x2',q.x);line.setAttribute('y2',q.y);edgeLayer.appendChild(line)});const major=new Set([...nodes].sort((a,b)=>(degrees.get(String(b.id))||0)-(degrees.get(String(a.id))||0)).slice(0,moreLabels.checked?120:35).map(n=>String(n.id)));nodes.forEach(n=>{const id=String(n.id),p=positions.get(id),g=document.createElementNS(ns,'g'),c=document.createElementNS(ns,'circle'),t=document.createElementNS(ns,'text'),d=degrees.get(id)||0,radius=Math.min(11,4.5+Math.sqrt(d)*1.25);g.setAttribute('class','node-group');g.dataset.id=id;c.setAttribute('class','node');c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r',radius);c.setAttribute('fill',color(nodeKind(n)));c.setAttribute('tabindex','0');c.setAttribute('role','button');c.setAttribute('aria-label',`${n.label||n.id}, ${nodeKind(n)}, ${d} connections`);t.setAttribute('class',`label${major.has(id)?' major':''}${q?' match':''}`);t.setAttribute('x',p.x+radius+5);t.setAttribute('y',p.y+4);t.textContent=String(n.label||n.id);const select=()=>{selected=id;nodeLayer.querySelectorAll('.node-group').forEach(x=>x.classList.toggle('selected',x.dataset.id===id));edgeLayer.querySelectorAll('.edge').forEach(x=>x.classList.toggle('active',x.dataset.a===id||x.dataset.b===id));show(n,d)};c.addEventListener('click',select);c.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select()}});let dragging=false;c.addEventListener('pointerdown',e=>{e.stopPropagation();dragging=true;c.setPointerCapture(e.pointerId)});c.addEventListener('pointermove',e=>{if(!dragging)return;const rect=svg.getBoundingClientRect(),x=(e.clientX-rect.left-transform.x)/transform.k,y=(e.clientY-rect.top-transform.y)/transform.k;p.x=x;p.y=y;c.setAttribute('cx',x);c.setAttribute('cy',y);t.setAttribute('x',x+radius+5);t.setAttribute('y',y+4);edgeLayer.querySelectorAll('.edge').forEach(line=>{if(line.dataset.a===id){line.setAttribute('x1',x);line.setAttribute('y1',y)}if(line.dataset.b===id){line.setAttribute('x2',x);line.setAttribute('y2',y)}})});c.addEventListener('pointerup',()=>dragging=false);g.append(c,t);nodeLayer.appendChild(g)});let pan=null;svg.addEventListener('pointerdown',e=>{if(e.target!==svg)return;pan={x:e.clientX,y:e.clientY,tx:transform.x,ty:transform.y};svg.classList.add('panning');svg.setPointerCapture(e.pointerId)});svg.addEventListener('pointermove',e=>{if(!pan)return;transform.x=pan.tx+e.clientX-pan.x;transform.y=pan.ty+e.clientY-pan.y;applyTransform()});svg.addEventListener('pointerup',()=>{pan=null;svg.classList.remove('panning')});svg.addEventListener('wheel',e=>{e.preventDefault();const rect=svg.getBoundingClientRect();zoom(e.deltaY<0?1.16:.86,e.clientX-rect.left,e.clientY-rect.top)},{passive:false});host.appendChild(svg);deconflictLabels(nodeLayer);fit();loading.hidden=true})}
let timer;search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(draw,120)});[mode,kind,relation,moreLabels].forEach(el=>el.addEventListener('change',draw));document.getElementById('zoomIn').addEventListener('click',()=>zoom(1.25));document.getElementById('zoomOut').addEventListener('click',()=>zoom(.8));document.getElementById('fit').addEventListener('click',fit);document.getElementById('reset').addEventListener('click',()=>{search.value=kind.value=relation.value='';mode.value=allNodes.some(isKnowledge)?'knowledge':'all';moreLabels.checked=false;selected=null;details.textContent='Select a Signal to inspect its source, type, and relationships.';draw()});let resizeTimer;addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(draw,180)});draw();
})();
</script></body></html>'''
    return template.replace("__TITLE__", safe_title).replace("__ATLAS_DATA__", payload)


def generate_atlas_html(
    atlas: str | Path | Mapping[str, Any], output: str | Path | None = None, *, title: str = "HoloCore Atlas"
) -> Path:
    if isinstance(atlas, Mapping):
        if output is None:
            raise ValueError("output is required when atlas is an in-memory mapping")
        destination = Path(output)
    else:
        source = Path(atlas)
        destination = Path(output) if output is not None else source.with_suffix(".html")
    return generate_atlas_views(atlas, [destination], title=title)[0]


def generate_atlas_views(
    atlas: str | Path | Mapping[str, Any],
    outputs: Iterable[str | Path],
    *,
    title: str = "HoloCore Atlas",
) -> list[Path]:
    """Render once and write the same viewer to all public/compatibility paths."""
    destinations = list(dict.fromkeys(Path(output) for output in outputs))
    if not destinations:
        raise ValueError("at least one Atlas HTML output is required")
    if isinstance(atlas, Mapping):
        graph = atlas
    else:
        source = Path(atlas)
        try:
            graph = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read Atlas graph {source}: {exc}") from exc
    rendered = render_atlas_html(graph, title=title)
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
    return destinations


write_atlas_html = generate_atlas_html
build_atlas_html = generate_atlas_html

__all__ = [
    "ATLAS_VIEWER_VERSION", "render_atlas_html", "generate_atlas_html",
    "generate_atlas_views", "write_atlas_html", "build_atlas_html",
]
