# Structure Map Config Contract

Use this reference when writing or debugging `structure-map.config.json` for `structure-map-html`.

## Freedom Boundaries

Low freedom fields are not config fields. Do not edit or regenerate these in an output artifact:

- shell DOM, CSS classes, visual tokens, and toolbar structure
- Cytoscape runtime, layout controls, selection model, and pair detail rendering
- edge label layer, edge label geometry, fallback container, graph meta, and side detail panel
- relation-card markup, role badges, and node/edge sizing helpers

Medium freedom fields are config fields. Change these through JSON only:

- `title`
- `help`
- `legend`
- `fallback`
- `initialDetail`
- `nodes`
- `edges`
- `nodes[].position`

High freedom remains agent judgment:

- which concepts deserve nodes
- relation direction and relation names
- which relations are primary or supporting
- plain-language copy that helps the reader understand the topic
- readable preset coordinates that leave room for relation labels

## Required JSON Shape

```json
{
  "title": "문서 제목",
  "help": "오른쪽 위 ? 도움말 문장",
  "legend": [
    { "type": "problem", "label": "문제/출발점" }
  ],
  "fallback": [
    "Cytoscape.js를 불러오지 못했을 때 보여줄 관계 설명"
  ],
  "initialDetail": {
    "kind": "선택 없음",
    "title": "구조도",
    "body": "노드나 관계선을 선택하기 전 오른쪽 패널 본문",
    "hint": "선택 해제나 탐색 보조 문구"
  },
  "nodes": [
    {
      "id": "problem",
      "label": "문제",
      "type": "problem",
      "detail": "노드를 선택했을 때 보여줄 설명",
      "position": { "x": 0, "y": 0 }
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "problem",
      "target": "concept",
      "label": "긴 관계 설명",
      "displayLabel": "짧은 관계 라벨",
      "detail": "관계선을 선택했을 때 보강 설명"
    }
  ]
}
```

## Validation Rules

- Allowed node `type` values: `problem`, `concept`, `runtime`, `verify`, `doc`.
- Node IDs must be unique.
- Edge IDs must be unique.
- Every edge `source` and `target` must match an existing node ID.
- Every node needs `label`, `type`, `detail`, and numeric `position.x`/`position.y`.
- Every edge needs `source`, `target`, and `label`.
- Every node type used by nodes must appear in `legend`.
- `displayLabel` should be shorter than `label` when the full relation is too long for the graph line.

## Renderer Command

```bash
node structure-map-html/scripts/render-structure-map.mjs \
  --config structure-map-html/examples/structure-map.config.example.json \
  --out /tmp/structure-map.html
```

Use `--template <path>` only for tests or intentional template migration work.

## Exception Path

Do not hand-write `structure-map.html` for normal work. If the topic truly cannot use the renderer, leave a short reason in the final answer and run the normal easy-explainer validator without the strict renderer flag. Template or runtime changes must update:

- `structure-map-html/templates/structure-map-cytoscape.html`
- `structure-map-html/SKILL.md`
- `visual-explainer/scripts/validate-output.py`
