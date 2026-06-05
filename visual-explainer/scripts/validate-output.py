#!/usr/bin/env python3
"""Validate the files and final response produced by the 쉬운 설명 skill."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = [
    "structure-map.html",
    "flow.html",
    "comparison.html",
    "mini-slide.html",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate easy-explainer HTML artifacts and optional final response links."
    )
    parser.add_argument("output_dir", type=Path, help="Directory containing the four HTML files.")
    parser.add_argument(
        "--last-message",
        type=Path,
        help="Optional final assistant response file that should link all four HTML files.",
    )
    parser.add_argument(
        "--require-local-cytoscape",
        action="store_true",
        help="Require structure-map.html to use assets/cytoscape/cytoscape.min.js and forbid CDN URLs.",
    )
    return parser


def validate_html_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing file: {path}"]
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    if "<html" not in lower:
        errors.append(f"missing <html> tag: {path}")
    if "</html>" not in lower:
        errors.append(f"missing </html> tag: {path}")
    if "<title" not in lower:
        errors.append(f"missing <title>: {path}")
    if len(re.sub(r"\s+", "", text)) < 500:
        errors.append(f"file looks too small to be useful: {path}")
    return errors


def validate_structure_map(path: Path, require_local_cytoscape: bool) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing file: {path}"]

    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    script_blocks = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", text, flags=re.IGNORECASE)
    for index, script in enumerate(script_blocks, start=1):
        if not script.strip():
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=True) as handle:
            handle.write(script)
            handle.flush()
            try:
                result = subprocess.run(
                    ["node", "--check", handle.name],
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except FileNotFoundError:
                errors.append("node is required to validate inline JavaScript syntax in structure-map.html")
                continue
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip().splitlines()
            first_line = detail[0] if detail else "unknown JavaScript syntax error"
            errors.append(f"inline script {index} has JavaScript syntax error: {first_line}")

    required_fragments = {
        'data-template="structure-map-cytoscape-v1"': "missing official Cytoscape template marker in structure-map.html",
        "cytoscape": "missing Cytoscape reference in structure-map.html",
        "graphelements": "missing graphElements data in structure-map.html",
        "fallback": "missing fallback in structure-map.html",
        "preset": "missing preset layout in structure-map.html",
        "alignedpositions": "missing aligned preset positions in structure-map.html",
        "applypresetpositions": "missing preset layout switcher in structure-map.html",
        "정렬 보기": "missing aligned layout control label 정렬 보기 in structure-map.html",
        "순환 보기": "missing circle layout control label 순환 보기 in structure-map.html",
        "fit": "missing fit control in structure-map.html",
        "clearfocus": "missing clearFocus interaction in structure-map.html",
        "selectionstate": "missing selectionState pair-selection model in structure-map.html",
        "handlenodetap": "missing handleNodeTap node routing in structure-map.html",
        "finddirectedges": "missing direct edge lookup in structure-map.html",
        "applysinglefocus": "missing single-node focus behavior in structure-map.html",
        "applypairfocus": "missing pair-node focus behavior in structure-map.html",
        "renderpairdetail": "missing pair detail panel renderer in structure-map.html",
        "relation-card": "missing dedicated pair relation card in structure-map.html",
        "relation-main": "missing main relation text in pair relation card in structure-map.html",
        "relation-path": "missing relation path text in relation shortcut list in structure-map.html",
        "focusnode": "missing focusNode compatibility wrapper in structure-map.html",
        "focusedge": "missing focusEdge compatibility wrapper in structure-map.html",
        "renderrelationlist": "missing related edge list renderer in structure-map.html",
        "bindrelationbuttons": "missing relation shortcut binding in structure-map.html",
        "relation-list": "missing related edge list UI in structure-map.html",
        "data-next-node-id": "missing next-node relation shortcuts in structure-map.html",
        "pair-node": "missing pair-node visual state in structure-map.html",
        "pair-edge": "missing pair-edge visual state in structure-map.html",
        "text-background-shape": "missing edge label badge background shape in structure-map.html",
        "edge-label-layer": "missing HTML overlay layer for edge labels in structure-map.html",
        "edge-label-badge": "missing HTML overlay badge for edge labels in structure-map.html",
        "edgedisplaylabel": "missing edge display label helper in structure-map.html",
        "displaylabel": "missing optional edge display label data in structure-map.html",
        "edgelabelnodescale": "missing edge label node zoom scale helper in structure-map.html",
        "edgelabelnormaloffset": "missing edge label normal offset helper in structure-map.html",
        "measureedgelabelwidth": "missing edge label width measurement in structure-map.html",
        "applyedgelabelclearance": "missing post-layout edge label clearance pass in structure-map.html",
        "fitgraphwithclearance": "missing fitGraphWithClearance layout finalizer in structure-map.html",
        "edgelabelgeometry": "missing edge label geometry calculation in structure-map.html",
        "edgeneedscurve": "missing edge curve need detector in structure-map.html",
        "edgecurvestyle": "missing edge curve style helper in structure-map.html",
        "edgecurvedistance": "missing curved edge distance helper in structure-map.html",
        "control-point-distances": "missing Cytoscape curved edge control-point distance in structure-map.html",
        "renderedposition": "missing renderedPosition-based edge geometry in structure-map.html",
        "renderedgelabels": "missing HTML overlay edge label renderer in structure-map.html",
        "scheduleedgelabels": "missing scheduled edge label redraw in structure-map.html",
        "graph-meta": "missing graph-meta status row in structure-map.html",
        "legend": "missing legend in structure-map.html",
        "node-count": "missing node-count status chip in structure-map.html",
        "edge-count": "missing edge-count status chip in structure-map.html",
        "measurenodelabelwidth": "missing node label width measurement in structure-map.html",
        "nodeboxwidth": "missing label-based node box width function in structure-map.html",
        "nodetextmaxwidth": "missing label-based node text max width function in structure-map.html",
        "estimatenodelabellinecount": "missing node label line count estimation in structure-map.html",
        "nodeboxheight": "missing label-based node box height function in structure-map.html",
        "userpositionedgraph": "missing user drag position preservation state in structure-map.html",
    }
    for fragment, message in required_fragments.items():
        if fragment not in lower:
            errors.append(message)

    if 'id="cy"' not in lower and "id='cy'" not in lower:
        errors.append("missing #cy graph container in structure-map.html")

    for fragment in ["source", "target", "label"]:
        if fragment not in lower:
            errors.append(f"missing {fragment} fields for graph relationships in structure-map.html")

    if re.search(r"connectededges\s*\(\s*\)\s*\.\s*connectednodes\s*\(", lower):
        errors.append("structure-map.html should not highlight every connected node from focusNode")
    if re.search(r"name\s*:\s*['\"]grid['\"]", text):
        errors.append("structure-map.html should not use Cytoscape grid auto-layout; use loose preset coordinates")
    if re.search(r"id\s*=\s*['\"]clear['\"]", text):
        errors.append("structure-map.html should not include a visible clear selection button")
    if "선택 해제 버튼" in text:
        errors.append("structure-map.html should not mention a clear selection button in hints")
    if not re.search(r"\.relation-card\s*\{[\s\S]*?background\s*:\s*#f8fafb[\s\S]*?text-align\s*:\s*left", text):
        errors.append("relation-card should use a quiet left-aligned bridge-card style")
    if not re.search(r"\.relation-card::before,[\s\S]*?\.relation-card::after[\s\S]*?left\s*:\s*24px", text):
        errors.append("relation-card bridge connector should align with the left text flow")
    if not re.search(r"\.relation-card::before[\s\S]*?top\s*:\s*-10px", text):
        errors.append("relation-card should include a subtle top connector hint")
    if not re.search(r"\.relation-card::after[\s\S]*?bottom\s*:\s*-10px", text):
        errors.append("relation-card should include a subtle bottom connector hint")
    if re.search(r"\.relation-card[\s\S]*?rotate\(45deg\)", text):
        errors.append("relation-card should not use decorative arrowheads")
    if re.search(r"\.relation-card\s*\{[\s\S]*?linear-gradient", text):
        errors.append("relation-card should not use a decorative gradient")
    if re.search(r"\.relation-card\s*\{[\s\S]*?inset\s+3px\s+0\s+0\s+var\(--blue\)", text):
        errors.append("relation-card should not use a strong blue side stripe")
    if not re.search(r"<div\s+class=[\"']relation-card[\"'][\s\S]*?<span\s+class=[\"']relation-main[\"']", text):
        errors.append("renderPairDetail should render dedicated relation-card markup")
    if not re.search(r"function\s+relationDirectionGlyph\(edge,\s*sourceNode,\s*targetNode\)[\s\S]*?['\"]↓['\"][\s\S]*?['\"]↑['\"]", text):
        errors.append("relation-card should derive an up/down direction glyph")
    if not re.search(r"<span\s+class=[\"']relation-main[\"']>\$\{directionGlyph\}\s+\$\{escapeHtml\(edge\.label\)\}", text):
        errors.append("relation-card should prefix relation text with the direction glyph")
    if re.search(r"<div\s+class=[\"']relation-card[\"'][\s\S]*?<b>\s*관계\s*</b>", text):
        errors.append("relation-card should not include a redundant relation badge")
    if re.search(r"<div\s+class=[\"']relation-card[\"'][\s\S]*?<span\s+class=[\"']relation-path[\"']", text):
        errors.append("relation-card should not repeat source-to-target path text")
    if "받아옴" in text or "내보냄" in text:
        errors.append("relation shortcut list should not use 받아옴/내보냄 wording")
    if re.search(r"function\s+relationShortcut\(graph,\s*edge,\s*nodeId\)[\s\S]*?['\"](?:->|<-)['\"]", text):
        errors.append("relation shortcut list should not use ASCII arrows")
    if not re.search(r"function\s+relationShortcut\(graph,\s*edge,\s*nodeId\)[\s\S]*?['\"]→['\"][\s\S]*?['\"]←['\"]", text):
        errors.append("relation shortcut list should derive ←/→ direction labels")
    if not re.search(r"<span\s+class=[\"']relation-path[\"']>\$\{escapeHtml\(relation\)\}</span>", text):
        errors.append("relation shortcut list should show only the short direction and neighbor label")
    if not re.search(r"const\s+incomingEdges\s*=\s*edges\.filter\([\s\S]*?data\(['\"]target['\"]\)\s*===\s*nodeId", text):
        errors.append("relation shortcut list should split incoming edges into 이전 후보")
    if not re.search(r"const\s+outgoingEdges\s*=\s*edges\.filter\([\s\S]*?data\(['\"]source['\"]\)\s*===\s*nodeId", text):
        errors.append("relation shortcut list should split outgoing edges into 다음 후보")
    if "renderRelationGroup(graph, '이전 후보', nodeId, incomingEdges)" not in text or "renderRelationGroup(graph, '다음 후보', nodeId, outgoingEdges)" not in text:
        errors.append("relation shortcut list should render 이전 후보 and 다음 후보 groups separately")
    if not re.search(r"function\s+renderPairRelationList\(graph,\s*sourceNode,\s*targetNode", text):
        errors.append("pair detail should use a pair-aware previous/next relation list")
    if not re.search(r"function\s+canonicalPairFromDirectEdges\(directEdges\)[\s\S]*?edge\.source[\s\S]*?edge\.target", text):
        errors.append("pair selection should normalize source/target from actual edge direction")
    if re.search(r"applyPairFocus\(cy\.getElementById\(lastNodeId\),\s*node,\s*directEdges\)", text):
        errors.append("node pair selection should not use click order as pair direction")
    if "applyPairFocus(canonicalPair.sourceNode, canonicalPair.targetNode, directEdges)" not in text:
        errors.append("node pair selection should apply canonical edge direction")
    if not re.search(r"const\s+previousEdges\s*=\s*sourceNode\.connectedEdges\(\)[\s\S]*?edge\.target\s*===\s*sourceId", text):
        errors.append("pair detail previous candidates should come into the source node")
    if not re.search(r"const\s+nextEdges\s*=\s*targetNode\.connectedEdges\(\)[\s\S]*?edge\.source\s*===\s*targetId", text):
        errors.append("pair detail next candidates should leave the target node")
    if "renderPairRelationList(cy, sourceNode, targetNode" not in text:
        errors.append("renderPairDetail should render pair-aware previous/next candidates")
    if ".relation-group + .relation-group" not in text:
        errors.append("relation shortcut groups should have spacing between previous and next sections")
    if "사이 관계만 현재 설명 대상" in text:
        errors.append("pair detail header should not repeat the current target description")
    if "만 현재 설명 대상" in text:
        errors.append("single detail should not repeat the current target description")
    if re.search(r"id=[\"']edge-count[\"'][^>]*>\s*관계", text) or re.search(r"edgeCount\.textContent\s*=\s*`관계", text):
        errors.append("edge-count status chip should use 엣지, not 관계")
    detail_card_pattern = r"<div\s+class=[\"'][^\"']*\bdetail-card\b[^\"']*[\"']"
    if re.search(r"<b>\s*(시작|종료)\s*:", text):
        errors.append("pair detail card titles should not include 시작:/종료: prefixes")
    if not re.search(detail_card_pattern + r"[\s\S]*?detail-card-heading[\s\S]*?<b>\$\{escapeHtml\(sourceLabel\)\}</b>[\s\S]*?roleBadgeMarkup\(sourceNode\)", text):
        errors.append("pair start card should render source node label followed by role badge")
    if not re.search(detail_card_pattern + r"[\s\S]*?detail-card-heading[\s\S]*?<b>\$\{escapeHtml\(targetLabel\)\}</b>[\s\S]*?roleBadgeMarkup\(targetNode\)", text):
        errors.append("pair end card should render target node label followed by role badge")
    if "${sourceLabel} -> ${targetLabel}" in text or "${sourceLabel} -&gt; ${targetLabel}" in text:
        errors.append("visible pair direction should use → instead of ASCII ->")
    if "${sourceLabel} → ${targetLabel}" not in text:
        errors.append("visible pair direction should render sourceLabel → targetLabel")
    if not re.search(r"\.role-badge\s*\{[\s\S]*?border-radius\s*:\s*var\(--radius\)", text):
        errors.append("detail role badges should use the shared user-flow radius")
    if not re.search(r"\.role-badge\s*\{[\s\S]*?font-size\s*:\s*11px", text):
        errors.append("detail role badges should be visually smaller than the detail title")
    if not re.search(r"\.details\s+strong\s*\{[\s\S]*?font-size\s*:\s*20px", text):
        errors.append("detail title should be larger for stronger hierarchy")
    if not re.search(r"\.detail-title-row\s*\{[\s\S]*?align-items\s*:\s*center", text):
        errors.append("detail title row should align title and role badge side by side")
    if not re.search(r"\.detail-card-heading\s*\{[\s\S]*?align-items\s*:\s*center", text):
        errors.append("pair detail card heading should align role badge and node title side by side")
    if not re.search(r"\.detail-card\s+b\s*\{[\s\S]*?font-size\s*:\s*15px", text):
        errors.append("pair detail card node title should be larger than before")
    if not re.search(r"const\s+titleMarkup\s*=\s*badgeMarkup[\s\S]*?detail-title-row[\s\S]*?<strong>\$\{escapeHtml\(title\)\}</strong>[\s\S]*?detail-badges", text):
        errors.append("single detail role badge should sit beside the title")
    for label in ["문제/출발점", "개념/설계", "실행/연결", "검증", "문서/운영"]:
        if label not in text:
            errors.append(f"missing detail role badge label: {label}")
    if not re.search(r"function\s+roleBadgeMarkup\(nodeOrType\)[\s\S]*?role-badge", text):
        errors.append("missing reusable detail role badge renderer")
    if not re.search(r"function\s+roleCardClass\(nodeOrType\)[\s\S]*?role-card-\$\{escapeHtml\(meta\.className\)\}", text):
        errors.append("missing reusable role card class renderer")
    for class_name, background in [
        ("role-card-problem", "#fef2f2"),
        ("role-card-concept", "#ecfdf3"),
        ("role-card-runtime", "#fefce8"),
        ("role-card-verify", "#fff7ed"),
        ("role-card-doc", "#f5f3ff"),
    ]:
        if not re.search(rf"\.detail-card\.{class_name}\s*\{{[\s\S]*?background\s*:\s*{re.escape(background)}", text):
            errors.append(f"missing role-matched detail card background: {class_name}")
    if not re.search(r"setDetail\([\s\S]*?renderRelationList\(cy,\s*node[\s\S]*?roleBadgeMarkup\(node\)", text):
        errors.append("single-node detail should place the node role badge near the title")
    if "roleBadgeMarkup(sourceNode)" not in text or "roleBadgeMarkup(targetNode)" not in text:
        errors.append("pair detail should show separate role badges for start and end nodes")
    if "roleCardClass(sourceNode)" not in text or "roleCardClass(targetNode)" not in text:
        errors.append("pair detail cards should use role-matched backgrounds")
    if not re.search(r"\.runtime\s*\{\s*color\s*:\s*var\(--yellow\)", text):
        errors.append("runtime role color should use yellow, not active-selection blue")
    if not re.search(r"\.role-badge\.runtime\s*\{[\s\S]*?background\s*:\s*#fefce8[\s\S]*?color\s*:\s*#a16207", text):
        errors.append("runtime role badge should use yellow theme")
    if not re.search(r"selector:\s*['\"]node\[type=[\"']runtime[\"']\]['\"][\s\S]*?'border-color'\s*:\s*'#ca8a04'[\s\S]*?'background-color'\s*:\s*'#fefce8'", text):
        errors.append("runtime node should use yellow theme instead of active blue")

    node_style_match = re.search(r"selector:\s*['\"]node['\"][\s\S]*?style:\s*\{([\s\S]*?)\n\s*\}", text)
    node_style = node_style_match.group(1) if node_style_match else ""
    if not node_style:
        errors.append("missing base node style in structure-map.html")
    if node_style and not re.search(r"['\"]font-size['\"]\s*:\s*(NODE_LABEL_FONT_SIZE|8[0-9]|9\d|\d{3,})", node_style):
        errors.append("node font-size should be at least 80 or use NODE_LABEL_FONT_SIZE in structure-map.html")
    if node_style and not re.search(r"['\"]text-max-width['\"]\s*:\s*nodeTextMaxWidth", node_style):
        errors.append("node text-max-width should use nodeTextMaxWidth in structure-map.html")
    if node_style and not re.search(r"\bwidth\s*:\s*nodeBoxWidth", node_style):
        errors.append("node width should use nodeBoxWidth in structure-map.html")
    if node_style and not re.search(r"\bheight\s*:\s*nodeBoxHeight", node_style):
        errors.append("node height should use nodeBoxHeight in structure-map.html")
    if not re.search(r"\bconst\s+NODE_BOX_MIN_WIDTH\s*=\s*560\s*;", text):
        errors.append("NODE_BOX_MIN_WIDTH should mirror user-flow graph card width at 5x scale")
    if not re.search(r"\bconst\s+NODE_BOX_MAX_WIDTH\s*=\s*560\s*;", text):
        errors.append("NODE_BOX_MAX_WIDTH should keep user-flow graph card width stable at 5x scale")
    if not re.search(r"\bconst\s+NODE_BOX_MIN_HEIGHT\s*=\s*230\s*;", text):
        errors.append("NODE_BOX_MIN_HEIGHT should mirror user-flow graph card height at 5x scale")
    if not re.search(r"\bconst\s+NODE_CORNER_RADIUS\s*=\s*40\s*;", text):
        errors.append("NODE_CORNER_RADIUS should mirror user-flow 8px radius at 5x scale")
    if not re.search(r"--radius\s*:\s*8px\s*;", text):
        errors.append("template radius should mirror user-flow --radius: 8px")
    if node_style and not re.search(r"['\"]border-color['\"]\s*:\s*['\"]#b8c3d2['\"]", node_style):
        errors.append("base node border color should mirror user-flow graph card border #b8c3d2")
    if node_style and not re.search(r"['\"]border-width['\"]\s*:\s*10\b", node_style):
        errors.append("base node border width should mirror user-flow 2px at 5x scale")
    if node_style and not re.search(r"\bshape\s*:\s*['\"]round-rectangle['\"]", node_style):
        errors.append("base node shape should mirror user-flow round-rectangle node cards")
    if node_style and not re.search(r"['\"]corner-radius['\"]\s*:\s*NODE_CORNER_RADIUS", node_style):
        errors.append("base node corner radius should use NODE_CORNER_RADIUS")
    if re.search(r"\bwidth\s*:\s*['\"]label['\"]", text):
        errors.append("node width should not use deprecated width: 'label' in structure-map.html")

    edge_style_match = re.search(r"selector:\s*['\"]edge['\"][\s\S]*?style:\s*\{([\s\S]*?)\n\s*\}", text)
    edge_style = edge_style_match.group(1) if edge_style_match else ""
    pair_edge_style_match = re.search(r"selector:\s*['\"]\.pair-edge['\"][\s\S]*?style:\s*\{([\s\S]*?)\n\s*\}", text)
    pair_edge_style = pair_edge_style_match.group(1) if pair_edge_style_match else ""
    focused_style_match = re.search(r"selector:\s*['\"]\.focused['\"][\s\S]*?style:\s*\{([\s\S]*?)\n\s*\}", text)
    focused_style = focused_style_match.group(1) if focused_style_match else ""
    pair_node_style_match = re.search(r"selector:\s*['\"]\.pair-node['\"][\s\S]*?style:\s*\{([\s\S]*?)\n\s*\}", text)
    pair_node_style = pair_node_style_match.group(1) if pair_node_style_match else ""
    selected_node_style_match = re.search(r"selector:\s*['\"]node:selected['\"][\s\S]*?style:\s*\{([\s\S]*?)\n\s*\}", text)
    selected_node_style = selected_node_style_match.group(1) if selected_node_style_match else ""
    if edge_style and not re.search(r"['\"]font-size['\"]\s*:\s*(3[2-9]|[4-9]\d|\d{3,})", edge_style):
        errors.append("edge label font-size should be at least 32 in structure-map.html")
    if pair_edge_style and not re.search(r"['\"]arrow-scale['\"]\s*:", pair_edge_style):
        errors.append("selected pair-edge should define arrow-scale in structure-map.html")
    if pair_edge_style and not re.search(r"\bwidth\s*:", pair_edge_style):
        errors.append("selected pair-edge should define width in structure-map.html")
    if focused_style and not re.search(r"['\"]border-color['\"]\s*:\s*['\"]#2563eb['\"]", focused_style):
        errors.append("focused node should use user-flow active blue #2563eb")
    if focused_style and not re.search(r"['\"]border-width['\"]\s*:\s*10\b", focused_style):
        errors.append("focused node should keep the base 5x node border width")
    if pair_node_style and not re.search(r"['\"]border-color['\"]\s*:\s*['\"]#2563eb['\"]", pair_node_style):
        errors.append("pair-node should use user-flow active blue #2563eb")
    if pair_node_style and not re.search(r"['\"]border-width['\"]\s*:\s*10\b", pair_node_style):
        errors.append("pair-node should keep the base 5x node border width")
    if selected_node_style and not re.search(r"['\"]border-color['\"]\s*:\s*['\"]#2563eb['\"]", selected_node_style):
        errors.append("selected node should use user-flow active blue #2563eb")
    if selected_node_style and not re.search(r"['\"]border-width['\"]\s*:\s*10\b", selected_node_style):
        errors.append("selected node should keep the base 5x node border width")
    if pair_edge_style and not re.search(r"['\"]line-color['\"]\s*:\s*['\"]#2563eb['\"]", pair_edge_style):
        errors.append("selected pair-edge should use user-flow active blue line #2563eb")
    if pair_edge_style and not re.search(r"['\"]target-arrow-color['\"]\s*:\s*['\"]#2563eb['\"]", pair_edge_style):
        errors.append("selected pair-edge should use user-flow active blue arrow #2563eb")
    if pair_edge_style and not re.search(r"\bwidth\s*:\s*8\.8\b", pair_edge_style):
        errors.append("selected pair-edge should not grow wider than the base edge width 8.8")
    if edge_style and not re.search(r"\blabel\s*:\s*['\"]['\"]", edge_style):
        errors.append("native Cytoscape edge label should be hidden because overlay labels own relation labels")
    if not re.search(r"\.edge-label-badge\s*\{[\s\S]*?font\s*:\s*(7[0-9]{2})\s+([5-9]\d|\d{3,})px/1\.15", text):
        errors.append("overlay edge label font should stay large and readable in structure-map.html")
    if not re.search(r"\.edge-label-badge\s*\{[\s\S]*?padding\s*:", text):
        errors.append("overlay edge label should define readable padding in structure-map.html")
    if not re.search(r"\.edge-label-badge\s*\{[\s\S]*?background\s*:\s*rgba\(255,\s*255,\s*255,\s*0\.9\)", text):
        errors.append("edge-label-badge background should mirror user-flow label opacity 0.9")
    if not re.search(r"\.edge-label-badge\s*\{[\s\S]*?border-radius\s*:\s*var\(--radius\)", text):
        errors.append("edge-label-badge should use the user-flow 8px radius token")
    edge_label_badge_style = re.search(r"\.edge-label-badge\s*\{([\s\S]*?)\n\s*\}", text)
    if edge_label_badge_style and "box-shadow" in edge_label_badge_style.group(1):
        errors.append("edge-label-badge should not use box-shadow")
    edge_label_pair_style = re.search(r"\.edge-label-badge\.is-pair\s*\{([\s\S]*?)\n\s*\}", text)
    if edge_label_pair_style and "box-shadow" in edge_label_pair_style.group(1):
        errors.append("selected edge-label-badge should not use box-shadow")
    if not re.search(r"\bconst\s+EDGE_LABEL_OFFSET\s*=", text):
        errors.append("missing EDGE_LABEL_OFFSET in structure-map.html")
    if not re.search(r"\bconst\s+EDGE_LABEL_SELECTED_OFFSET\s*=", text):
        errors.append("missing EDGE_LABEL_SELECTED_OFFSET in structure-map.html")
    if not re.search(r"\bconst\s+EDGE_LABEL_FONT_SIZE\s*=", text):
        errors.append("missing EDGE_LABEL_FONT_SIZE in structure-map.html")
    if not re.search(r"\bconst\s+EDGE_LABEL_FONT_SIZE\s*=\s*50\s*;", text):
        errors.append("EDGE_LABEL_FONT_SIZE should mirror user-flow edge label font at 5x scale")
    if not re.search(r"\bconst\s+EDGE_LABEL_PADDING_Y\s*=", text):
        errors.append("missing EDGE_LABEL_PADDING_Y in structure-map.html")
    if not re.search(r"\bconst\s+EDGE_LABEL_PADDING_X\s*=", text):
        errors.append("missing EDGE_LABEL_PADDING_X in structure-map.html")
    if not re.search(r"\bconst\s+EDGE_LABEL_PADDING_Y\s*=\s*15\s*;", text):
        errors.append("EDGE_LABEL_PADDING_Y should mirror user-flow edge label padding at 5x scale")
    if not re.search(r"\bconst\s+EDGE_LABEL_PADDING_X\s*=\s*15\s*;", text):
        errors.append("EDGE_LABEL_PADDING_X should mirror user-flow edge label padding at 5x scale")
    if not re.search(r"\bconst\s+EDGE_LABEL_HORIZONTAL_PADDING\s*=\s*EDGE_LABEL_PADDING_X\s*\*\s*2\s*;", text):
        errors.append("EDGE_LABEL_HORIZONTAL_PADDING should derive from EDGE_LABEL_PADDING_X in structure-map.html")
    if "edgeLabelZoomScale" in text or "EDGE_LABEL_MIN_SCALE" in text or "EDGE_LABEL_MAX_SCALE" in text:
        errors.append("edge label should sync to node zoom without old clamp-based zoom scaling")
    if not re.search(r"function\s+edgeLabelNodeScale\(\)\s*\{[\s\S]*?return\s+cy\.zoom\(\)\s*\|\|\s*1\s*;[\s\S]*?\}", text):
        errors.append("edgeLabelNodeScale should return cy.zoom() from the Cytoscape scope")
    if not re.search(r"function\s+edgeLabelNormalOffset\(edgeElement\)[\s\S]*?edgeElement\.hasClass\(['\"]pair-edge['\"]\)\s*\?\s*EDGE_LABEL_SELECTED_OFFSET\s*:\s*EDGE_LABEL_OFFSET[\s\S]*?return\s+offset\s*\*\s*edgeLabelNodeScale\(\)", text):
        errors.append("edgeLabelNormalOffset should return pair/default offset scaled by node zoom")
    normal_offset_match = re.search(r"function\s+edgeLabelNormalOffset\(edgeElement\)\s*\{([\s\S]*?)\n\s*\}", text)
    if normal_offset_match and re.search(r"labelHeight|EDGE_LABEL_FONT_SIZE\s*\*\s*1\.15|labelHeight\s*/\s*2", normal_offset_match.group(1)):
        errors.append("edgeLabelNormalOffset should not add label height; geometry should use edge midpoint plus zoom-scaled normal offset")
    if not re.search(r"const\s+offset\s*=\s*edgeLabelNormalOffset\(edgeElement\)", text):
        errors.append("edgeLabelGeometry should use dynamic label normal offset")
    if re.search(r"parts\[parts\.length\s*-\s*1\]", text):
        errors.append("edgeDisplayLabel should not force edge labels down to the final token")
    if not re.search(r"function\s+edgeDisplayLabel\(edgeDataOrLabel\)[\s\S]*?displayLabel[\s\S]*?predicateLabel[\s\S]*?shortLabel[\s\S]*?label", text):
        errors.append("edgeDisplayLabel should prefer optional display/predicate/short labels before full label")
    if not re.search(r"const\s+text\s*=\s*edgeDisplayLabel\(edgeDataOrLabel\)", text):
        errors.append("measureEdgeLabelWidth should measure the displayed edge label")
    if not re.search(r"measureEdgeLabelWidth\(edgeElement\.data\(\)\)\s*\*\s*edgeLabelNodeScale\(\)", text):
        errors.append("edge label clearance should measure displayed edge label width with node zoom scale")
    if "scale(${labelScale})" in text:
        errors.append("edge label zoom sync should not alter the old transform-based positioning")
    if not re.search(r"button\.style\.fontSize\s*=\s*`\$\{EDGE_LABEL_FONT_SIZE\s*\*\s*labelScale\}px`", text):
        errors.append("overlay edge labels should sync font size with the node zoom rule")
    if not re.search(r"button\.style\.padding\s*=\s*`\$\{EDGE_LABEL_PADDING_Y\s*\*\s*labelScale\}px\s*\$\{EDGE_LABEL_PADDING_X\s*\*\s*labelScale\}px`", text):
        errors.append("overlay edge labels should sync padding with the node zoom rule")
    if not re.search(r"button\.style\.left\s*=\s*`\$\{geometry\.x\}px`", text):
        errors.append("overlay edge labels should place the label center with left")
    if not re.search(r"button\.style\.top\s*=\s*`\$\{geometry\.y\}px`", text):
        errors.append("overlay edge labels should place the label center with top")
    if not re.search(r"button\.textContent\s*=\s*displayLabel", text):
        errors.append("overlay edge labels should show the optional display label when present")
    if re.search(r"angle\s*:", text):
        errors.append("edgeLabelGeometry should not return angle; overlay edge labels should stay horizontal")
    if not re.search(r"button\.style\.transform\s*=\s*['\"]translate\(-50%,\s*-50%\)['\"]", text):
        errors.append("overlay edge label transform should only center the label")
    if not re.search(r"function\s+edgeCurveStyle\(edgeElement\)[\s\S]*?edgeNeedsCurve\(edgeElement\)[\s\S]*?unbundled-bezier[\s\S]*?straight", text):
        errors.append("edgeCurveStyle should use straight as default and unbundled-bezier only when needed")
    if not re.search(r"function\s+edgeCurveDistance\(edgeElement\)[\s\S]*?if\s*\(!edgeNeedsCurve\(edgeElement\)\)\s*return\s+0", text):
        errors.append("edgeCurveDistance should return 0 when a straight edge is enough")
    if re.search(r"\.edge-label-badge\.is-dimmed\s*\{[\s\S]*?opacity\s*:\s*0\.[0-5]\b", text):
        errors.append("dimmed overlay edge labels should not become too faint")
    if re.search(r"selector:\s*['\"]\.dimmed['\"][\s\S]*?opacity\s*:\s*0\.[0-5]\b", text):
        errors.append("dimmed graph elements should not become too faint")
    if not re.search(r"\.shell\s*\{[\s\S]*?height\s*:\s*calc\(100vh\s*-\s*\d+px\)", text):
        errors.append("desktop shell height should be viewport-based in structure-map.html")
    if not re.search(r"@media\s*\(max-width:\s*860px\)[\s\S]*?#cy\s*\{[\s\S]*?top\s*:\s*58px[\s\S]*?\.edge-label-layer\s*\{[\s\S]*?top\s*:\s*58px", text):
        errors.append("mobile edge-label-layer top should match #cy top 58px in structure-map.html")
    if not re.search(r"<div\s+class=[\"']graph-meta[\"'][\s\S]*?<ul\s+class=[\"']legend[\"']", text):
        errors.append("legend should live inside graph-meta in structure-map.html")
    side_match = re.search(r"<aside\s+class=[\"']side[\"'][\s\S]*?</aside>", text)
    if side_match and re.search(r"<ul\s+class=[\"']legend[\"']", side_match.group(0)):
        errors.append("legend should not live in the side detail panel in structure-map.html")
    if not re.search(r"\.legend\s*\{[\s\S]*?display\s*:\s*flex[\s\S]*?flex-wrap\s*:\s*nowrap", text):
        errors.append("legend should render as a single-line flex row in structure-map.html")
    details_style_match = re.search(r"\.details\s*\{([\s\S]*?)\n\s*\}", text)
    if details_style_match and "border-top" in details_style_match.group(1):
        errors.append("details panel should not have a top divider after legend moves to graph-meta")
    if not re.search(r"\bconst\s+EDGE_LABEL_LINE_PADDING\s*=", text):
        errors.append("missing EDGE_LABEL_LINE_PADDING in structure-map.html")
    if not re.search(r"\bconst\s+EDGE_LABEL_CLEARANCE_ITERATIONS\s*=", text):
        errors.append("missing EDGE_LABEL_CLEARANCE_ITERATIONS in structure-map.html")
    if not re.search(r"\bconst\s+GRAPH_MIN_ZOOM\s*=", text):
        errors.append("missing GRAPH_MIN_ZOOM in structure-map.html")
    if not re.search(r"\bconst\s+FIT_GRAPH_PADDING\s*=", text):
        errors.append("missing FIT_GRAPH_PADDING in structure-map.html")
    if not re.search(r"\bminZoom\s*:\s*GRAPH_MIN_ZOOM", text):
        errors.append("Cytoscape minZoom should use GRAPH_MIN_ZOOM in structure-map.html")
    if re.search(r"cy\.fit\s*\(\s*cy\.elements\(\)\s*,\s*24\s*\)", text):
        errors.append("cy.fit should not use narrow 24px padding in structure-map.html")
    if not re.search(r"cy\.fit\s*\(\s*cy\.elements\(\)\s*,\s*FIT_GRAPH_PADDING\s*\)", text):
        errors.append("cy.fit should use FIT_GRAPH_PADDING in structure-map.html")
    if not re.search(r"measureEdgeLabelWidth\s*\(\s*edgeElement\.data\(\)\s*\)", text):
        errors.append("edge clearance should measure each displayed relation label width in structure-map.html")
    if not re.search(r"applyEdgeLabelClearance[\s\S]*?measureEdgeLabelWidth[\s\S]*?EDGE_LABEL_LINE_PADDING", text):
        errors.append("applyEdgeLabelClearance should compare edge length to label width plus padding in structure-map.html")
    if not re.search(r"userPositionedGraph[\s\S]*?EDGE_LABEL_CLEARANCE_ITERATIONS", text):
        errors.append("edge clearance should preserve user-dragged graph positions in structure-map.html")
    if edge_style and not re.search(r"['\"]text-margin-y['\"]\s*:\s*-\s*(7[8-9]|[8-9]\d|\d{3,})", edge_style):
        errors.append("edge label should sit above the line with text-margin-y at least -78 in structure-map.html")
    if edge_style and not re.search(r"['\"]text-background-padding['\"]\s*:\s*(1[2-9]|[2-9]\d|\d{3,})", edge_style):
        errors.append("edge label background padding should be at least 12 in structure-map.html")
    if edge_style and not re.search(r"['\"]text-rotation['\"]\s*:\s*['\"]none['\"]", edge_style):
        errors.append("edge label text-rotation should be none in structure-map.html")
    if edge_style and re.search(r"['\"]text-rotation['\"]\s*:\s*['\"]autorotate['\"]", edge_style):
        errors.append("edge label text-rotation should not use autorotate in structure-map.html")

    if require_local_cytoscape:
        local_asset = path.parent / "assets" / "cytoscape" / "cytoscape.min.js"
        if not local_asset.exists():
            errors.append(f"missing local Cytoscape asset: {local_asset}")
        if "assets/cytoscape/cytoscape.min.js" not in lower:
            errors.append("structure-map.html does not reference assets/cytoscape/cytoscape.min.js")
        cdn_patterns = [
            "https://unpkg.com",
            "https://cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
        ]
        for pattern in cdn_patterns:
            if pattern in lower:
                errors.append(f"structure-map.html should not reference CDN URL when local Cytoscape is required: {pattern}")

    return errors


def validate_last_message(path: Path, output_dir: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"last message file not found: {path}"]
    text = path.read_text(encoding="utf-8")
    for file_name in REQUIRED_FILES:
        if file_name not in text and str(output_dir / file_name) not in text:
            errors.append(f"last message does not mention {file_name}")
    return errors


def main() -> int:
    args = build_parser().parse_args()
    output_dir = args.output_dir.expanduser().resolve()

    if not output_dir.exists():
        print(f"output directory not found: {output_dir}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for file_name in REQUIRED_FILES:
        path = output_dir / file_name
        errors.extend(validate_html_file(path))
        if file_name == "structure-map.html":
            errors.extend(validate_structure_map(path, args.require_local_cytoscape))

    if args.last_message:
        errors.extend(validate_last_message(args.last_message.expanduser().resolve(), output_dir))

    if errors:
        for error in errors:
            print(f"fail: {error}")
        return 1

    print("easy explainer output ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
