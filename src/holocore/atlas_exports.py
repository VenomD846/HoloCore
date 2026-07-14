"""Stable, Graphify-style Atlas exports."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .atlas_html import render_atlas_html

def export_atlas(atlas: Any, output: str | Path, formats: list[str] | None = None) -> dict[str, Any]:
    graph = atlas.load_graph(); destination = Path(output); destination.mkdir(parents=True, exist_ok=True); formats = formats or ["json", "html", "markdown", "manifest"]; files: dict[str, str] = {}
    if "json" in formats:
        path = destination / "graph.json"; path.write_text(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"); files["json"] = str(path)
    if "html" in formats:
        path = destination / "graph.html"; path.write_text(render_atlas_html(graph), encoding="utf-8"); files["html"] = str(path)
    if "markdown" in formats:
        path = destination / "GRAPH_REPORT.md"; atlas.write_report(path); files["markdown"] = str(path)
    manifest = {"schema_version": 1, "generator": "holocore-atlas", "source_digest": graph.get("graph", {}).get("source_digest", ""), "formats": files}
    if "manifest" in formats:
        path = destination / "manifest.json"; files["manifest"] = str(path); manifest["formats"] = files; path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["formats"] = files; return manifest
