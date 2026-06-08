---
name: structure-map-html
description: "`쉬운 설명` 하위 스킬. 구조도 HTML, 관계도 HTML, 개념 관계 시각화처럼 관계와 의존 이유를 구조도로 이해해야 할 때 `structure-map.html`을 만든다. 관계선, 방향, 관계 라벨, 클릭 설명이 핵심이면 Cytoscape.js를 기본값으로 쓴다."
metadata:
  short-description: structure-map.html 관계도/구조도 생성
---

# structure-map-html

`structure-map.html` 하나를 책임지는 하위 스킬이다.

## 검색 호출어

`structure map html`, `구조도 HTML`, `관계도 HTML`이 보이면 이 스킬을 우선한다.

- `structure map html`
- `structure-map-html`
- `structure-map.html`
- `구조도 HTML`
- `관계도 HTML`
- `노드-엣지 구조도`
- `개념 관계도`

## 역할

구조도는 시각적 요약이 아니라 관계 해석 도구다.

사용자는 `structure-map.html`을 열어 아래 질문에 바로 답을 얻어야 한다.

- 무엇이 무엇과 연결되는가?
- 어떤 방향으로 이어지는가?
- 어떤 관계가 핵심이고 어떤 관계가 보조인가?
- 노드(관계도에서 점처럼 보이는 개념)와 엣지(두 노드 사이의 관계선)가 왜 이어지는가?

## 입력

- 설명 대상의 핵심 개념 목록
- 개념 사이의 관계 후보와 관계 이름
- 관계 방향: 원인 → 결과, 입력 → 처리 → 출력, 문제 → 해결책, 중심 → 파생 등
- 입력 장르: 이야기, 앱, 로직, 브레인스토밍, 연구, 비교 등
- 저장 파일명: `structure-map.html`

## 기본 구현

관계선, 방향, 관계 라벨, 클릭 설명이 핵심이면 Cytoscape.js를 기본값으로 쓴다.

기본 템플릿은 이 파일 옆의 `templates/structure-map-cytoscape.html`이다.
기본 생성기는 `scripts/render-structure-map.mjs`이고, config 계약은 `references/config-contract.md`가 소유한다.

새 `structure-map.html`을 만들 때는 HTML을 처음부터 새로 쓰지 않는다. Do not hand-write `structure-map.html` for normal work. 기본은 아래 순서다.

1. `references/config-contract.md`를 필요할 때만 읽고 JSON config를 작성한다.
2. `examples/structure-map.config.example.json`의 필드 형태를 따른다.
3. 아래 명령으로 템플릿과 config를 결합한다.

```bash
node structure-map-html/scripts/render-structure-map.mjs \
  --config /path/to/structure-map.config.json \
  --out /path/to/structure-map.html
```

4. 생성된 HTML의 `data-template="structure-map-cytoscape-v1"`와 `data-generated-by="structure-map-renderer-v1"`를 유지한다.
5. 템플릿 장치를 제거하거나 renderer를 우회해야 할 만큼 특수한 구조라면, 최종 답변에 이유를 짧게 남기고 엄격 renderer 검증을 쓰지 않는다.

## 자유도 원칙

`skill-creator` 기준으로 이 스킬은 세 단계 자유도를 둔다.

- Low freedom: 템플릿 DOM, CSS, Cytoscape runtime, 관계 라벨 overlay, 선택 모델, 오른쪽 설명 패널, fallback, graph meta는 renderer와 템플릿이 고정한다.
- Medium freedom: 제목, 도움말, legend, fallback 문구, initial detail, nodes, edges, preset 좌표만 JSON config로 바꾼다.
- High freedom: 어떤 개념을 노드로 잡을지, 관계 방향과 관계 이름을 어떻게 정할지, 설명 copy를 얼마나 쉽게 쓸지는 주제에 맞게 판단한다.

자유도 세부 schema와 예외 경로는 `references/config-contract.md`를 본다.

이 문서는 설계 의도를 정한다. 픽셀값, font weight, offset, zoom padding 같은 구현 기준값은 `templates/structure-map-cytoscape.html`과 검증 스크립트를 원본으로 본다. 새 산출물을 만들 때 `SKILL.md`의 숫자를 베껴 맞추는 식으로 작업하지 않는다.

템플릿 기준을 바꿀 때는 아래 세 곳을 함께 갱신한다.

1. `templates/structure-map-cytoscape.html`: 실제 기본 HTML 템플릿
2. 이 `SKILL.md`: 다음 구조도 생성 때 따라야 하는 설계 기준
3. `../visual-explainer/scripts/validate-output.py`: 기준값이 되돌아가거나 빠졌을 때 잡는 검증 규칙

## 핵심 계약

- `graphElements`: 노드와 엣지를 데이터로 분리한다.
- `data-template="structure-map-cytoscape-v1"`: 공식 Cytoscape 구조도 템플릿에서 출발했음을 표시한다.
- `data-generated-by="structure-map-renderer-v1"`: renderer가 공식 템플릿과 JSON config를 결합했음을 표시한다.
- `#cy`: Cytoscape 그래프 container를 둔다.
- `#fallback`: Cytoscape 로딩 실패 시 빈 화면 대신 핵심 관계 목록을 보여준다.
- 기본 layout은 `preset` 좌표를 권장한다. 이는 자동 `grid` 칸 채우기가 아니라, 사람이 읽기 좋은 느슨한 레인과 기준선을 직접 잡는다는 뜻이다.
- 보조 layout은 같은 구조를 더 넓게 보이게 하거나, 주제에 맞는 대체 배치로 둘 수 있다. `breadthfirst`나 `circle`이 필요하면 보조 선택지로 쓸 수 있지만 기본값처럼 자동 적용하지 않는다.
- `fit`: 그래프를 화면 안에 다시 맞추는 조작을 둔다.
- 관계 라벨은 HTML overlay로 표시한다. 기본 라벨은 수평으로 읽히게 두고, 선 중앙점에서 너무 멀거나 가깝지 않게 배치한다.
- 노드 박스는 라벨 길이에 따라 폭과 높이가 달라져야 한다. 고정 폭 카드처럼 모든 노드를 같은 크기로 밀어 넣지 않는다.
- 사용자가 노드를 드래그해 위치를 바꾼 뒤에는 `fit`이나 resize가 layout을 다시 돌리지 않는다.
- 노드나 엣지를 클릭하면 오른쪽 설명 패널이 바뀐다.
- 선택 모델은 단일 노드와 직접 연결된 두 노드 쌍을 명확히 구분한다. 직접 연결되지 않은 후보 전체를 그래프에서 한꺼번에 밝히지 않는다.
- 오른쪽 설명 패널에는 직접 이어진 관계 이름, 방향, `source → target` 경로를 보여주고, 관계 항목을 눌러 다음 쌍 선택으로 이어갈 수 있게 한다.
- 현재 설명 대상과 나머지 문맥은 구분하되, 비선택 항목을 너무 흐리게 만들어 전체 구조를 잃게 하지 않는다.

현재 package supply-chain freeze가 유지되는 동안 Codex는 `npm install`, `npm pack`, `npx`, `pip download` 같은 dependency 다운로드/실행 명령을 쓰지 않는다. CDN prototype은 허용하지만, offline-safe 산출물은 Operator가 검증된 `cytoscape.min.js`를 제공하거나 freeze 해제 뒤 별도 작업으로 로컬 vendor 파일을 둔다.

## 구조 선택

Cytoscape를 기본 렌더러로 쓰되, 입력 성격에 맞춰 그래프 모양을 고른다.

- 노드-엣지 관계도: 개념과 관계 이름이 핵심일 때 쓴다.
- 방향 그래프: 원인, 결과, 입력, 처리, 출력처럼 방향이 중요할 때 쓴다.
- 마인드맵: 중심 주제에서 아이디어가 갈라질 때 쓴다.
- 기능 구조도: 앱 기능, 화면, 데이터, 사용자 행동의 묶음을 보여줄 때 쓴다.
- 로직 차트: 조건, 분기, 예외, 결과를 보여줄 때 쓴다.
- 인물/개념 관계도: 인물, 조직, 개념 사이의 관계 이름과 강도를 보여줄 때 쓴다.
- 생태계 지도: 여러 도구, 스킬, 문서, 검증 명령이 책임을 나누는 구조를 보여줄 때 쓴다.

예외:

- 관계선보다 표 비교가 핵심이면 `comparison-html`로 넘긴다.
- 관계선보다 순서, 단계, 절차, 타임라인이 핵심이면 `flow-html`로 넘긴다.
- 관계가 거의 없고 단순 그룹 소개만 필요하면 CSS 카드 배치를 쓸 수 있다. 이 경우 왜 Cytoscape가 더 적합하지 않은지 산출물 또는 작업 설명에 짧게 남긴다.

## 디자인 판단

- 먼저 관계의 성격을 정한다: 의존, 분리, 포함, 충돌, 검증, 흐름, 소유, 원인.
- 구조 표현은 관계의 성격을 가장 잘 드러내는 방식으로 고른다.
- 선이나 화살표에는 가능한 한 관계 이름을 붙인다.
- 관계 이름을 붙인다면 노드는 관계 라벨 공간까지 고려해 배치한다. 노드끼리만 안 겹치는 것은 충분하지 않다.
- 관계 라벨은 배치의 1급 제약이다. 노드 박스, 화살표 촉, 다른 관계 라벨이 관계 글자를 가리면 구조도 품질 문제가 된다.
- 노드 사이에는 관계 라벨이 들어갈 여백을 둔다. `grid`라는 사용자 표현은 “정돈된 기준선”으로 해석하고, 자동 layout에 모든 노드를 빽빽하게 끼워 맞추라는 뜻으로 해석하지 않는다.
- 관계 라벨은 기본적으로 수평으로 읽히게 둔다. 대각선 선이 많을 때 라벨까지 회전하면 가독성이 떨어진다.
- 관계 라벨은 노드 라벨과 zoom 감각이 어긋나지 않아야 한다. 구체적인 font, padding, offset 값은 템플릿 기준을 따른다.
- 노드 박스는 라벨 길이와 예상 줄 수에 맞게 변해야 한다. 짧은 라벨과 긴 라벨을 같은 고정 폭에 밀어 넣지 않는다.
- 넓은 간격을 쓰더라도 `전체 보기`가 그래프 전체를 담아야 한다. 상단 툴바와 하단 메타 줄이 그래프를 덮는 공간까지 고려한다.
- 관계 라벨이 노드, 다른 관계 라벨, 화살표 끝에 가려지면 노드 간격, 보조 관계 위치, 라벨 offset, 좌표를 조정한다.
- `structure-map.html`의 기본은 관계 구조를 보여주는 정렬형 `preset`이다. 좌표는 무작위가 아니라 열/행 기준선에 맞추되, 빈칸 없이 채우는 자동 `grid`가 되어서는 안 된다.
- `breadthfirst`나 `circle`은 필요하면 보조 layout으로 쓸 수 있다. 다만 기본 산출물에서 관계 라벨 가독성을 해치거나 사용자의 정렬 의도와 충돌하면 쓰지 않는다.
- 노드 클릭 설명에는 해당 개념의 역할과 왜 중요한지를 쓴다.
- 노드 클릭 설명에는 직접 이어진 관계 목록을 함께 보여주되, 그래프에서 후보 노드를 모두 강조하지 않는다.
- 엣지 클릭 설명은 두 끝 노드와 해당 관계선만 설명하는 `pair` 상태로 보여준다.
- 쌍 선택 상세에서 관계 칸은 일반 `detail-card`와 다르게 보이게 한다. 시작/종료 카드 제목은 `시작 노드`, `종료 노드`처럼 추상 라벨만 쓰지 말고 `시작: <노드 이름>`, `종료: <노드 이름>` 형식으로 실제 노드 이름을 포함한다. `.relation-card`는 강한 장식선이나 화살표가 아니라, 시작 노드와 종료 노드 사이의 중립적인 bridge card처럼 보여야 하며, 실제 관계 이름과 설명을 왼쪽 정렬로 표시한다. 브릿지 연결선도 카드 중앙이 아니라 왼쪽 텍스트 흐름에 맞춘다. 제목과 카드 구조가 이미 설명 대상을 보여주므로 `A와 B 사이 관계만 현재 설명 대상` 같은 상단 보조 설명, `관계` 같은 중복 배지, `source → target` 경로를 반복하지 않는다. 쌍 선택 제목처럼 방향을 표시해야 하는 곳은 `${sourceLabel} → ${targetLabel}` 형식으로 쓴다.
- `focusNode`가 `node.connectedEdges().connectedNodes()`로 모든 이웃을 한꺼번에 강조하면 사용자가 현재 설명 대상을 잃기 쉽다.
- 오른쪽 관계 목록은 `[data-next-node-id]`를 중심으로 다음 노드 이동을 처리한다. `[data-edge-id]`는 추적용으로 함께 둘 수 있지만, 클릭 라우팅의 주 기준이면 안 된다.
- 대칭 배치는 실제 관계가 대칭일 때만 쓴다.
- 색상과 위치는 장식이 아니라 그룹, 우선순위, 책임 차이를 보여줄 때만 쓴다.
- 버튼, 상태 pill, 도움말 카드, 상세 카드, 관계 후보 같은 내부 UI 요소는 노드의 round-rectangle 느낌과 맞춰 `8px` 수준의 radius를 둔다.
- legend는 오른쪽 설명 패널 상단에 두지 않는다. 그래프 하단의 `node-count`, `edge-count` 아래쪽/옆쪽 메타 줄에 붙이고, 데스크톱에서는 한 줄로 표시한다. 하단 카운트 라벨은 `노드 N`, `엣지 N`으로 쓴다.
- 모바일에서는 그래프와 설명 패널이 세로로 쌓이게 한다.
- 긴 사용 설명은 상단 본문 문단으로 노출하지 않고 오른쪽 상단 `?` 도움말 안에 둔다.
- 사이드 패널은 현재 선택 설명에 집중한다. legend나 고정된 “읽는 법” 설명 문단은 넣지 않는다.
- legend가 사이드 패널에서 빠졌으므로 `.details` 위쪽 구분선은 두지 않는다. 오른쪽 패널은 선택 설명이 바로 시작되어야 한다.

## 산출물

- `structure-map.html`
- 제목, 오른쪽 상단 `?` 도움말, 하단 한 줄 legend, Cytoscape 그래프, 관계 라벨, 보기 조작, fallback, click detail panel을 포함한다.

## 검증

- 입력에 맞는 구조 표현을 선택했다.
- 핵심 개념이 빠지지 않았다.
- 관계 이름이나 의존 이유가 보인다.
- 관계 라벨이 노드나 다른 라벨에 가려지지 않는다.
- 관계 라벨이 노드 박스나 화살표 촉에 가려지지 않는다.
- 관계 라벨은 `edge-label-layer`의 HTML overlay로 표시된다.
- 관계 라벨은 `edgeLabelGeometry`로 선 중앙점과 법선 offset을 계산한다.
- 관계 라벨은 수평 고정이다. `edgeLabelGeometry()`의 기본 반환 각도는 `0`이어야 한다.
- 관계 라벨 폭은 `measureEdgeLabelWidth`로 측정하고, 너무 짧은 관계선은 `applyEdgeLabelClearance`가 `EDGE_LABEL_LINE_PADDING` 기준으로 벌린다.
- 관계선 길이 보정은 `fitGraphWithClearance`를 통해 초기 layout과 명시적 layout 전환 뒤에 적용된다.
- Cytoscape 기본 edge label은 숨겨져 있고, overlay 라벨이 실제 보이는 관계 라벨을 담당한다.
- 기본 보기는 정렬형 `preset` 구조다. 노드가 사각형 기준선에 맞춰 전개되지만 `grid` 자동 칸 채우기처럼 빽빽하지 않아야 한다.
- 주 흐름과 보조 관계를 함께 보여줄 때는 관계 라벨이 읽히도록 노드 간격, 보조 관계 위치, 라벨 offset을 조정했다.
- `structure-map.html` 안에 `data-template="structure-map-cytoscape-v1"`가 있다.
- renderer 기본 경로를 쓴 경우 `structure-map.html` 안에 `data-generated-by="structure-map-renderer-v1"`가 있다.
- `?` 도움말이 있고, 긴 사용 설명이 상단 본문 문단으로 노출되지 않는다.
- `structure-map.html` 안에 `cytoscape`, `graphElements`, `fallback`, `id="cy"` 또는 `id='cy'`가 있다.
- `정렬 보기`, `넓게 보기`, `전체 보기` 조작이 있다. 선택 해제는 Esc key와 빈 그래프 영역 클릭으로 가능하다.
- legend는 `.graph-meta` 안에 있고, 오른쪽 `.side` 패널 안에 있지 않다.
- `.details`에는 상단 `border-top` 구분선이 없다.
- 데스크톱 `.shell` 높이는 `calc(100vh - ...)` 기반이라 뷰포트 하단에 맞춰진다.
- `전체 보기`는 큰 노드와 넓은 관계 라벨 간격을 쓰더라도 모든 노드와 관계선이 화면 안에 들어오게 한다. `cy.fit`은 고정 숫자 24가 아니라 `FIT_GRAPH_PADDING`을 쓴다.
- 노드 박스 초기 폭과 높이는 라벨 길이와 예상 줄 수에 따라 달라진다. `measureNodeLabelWidth`, `nodeBoxWidth`, `nodeTextMaxWidth`, `estimateNodeLabelLineCount`, `nodeBoxHeight`가 있다.
- `width: 'label'` 같은 deprecated 방식으로 노드 크기를 맞추지 않는다.
- 사용자가 노드를 드래그한 뒤에는 자동 resize나 `전체 보기`가 layout을 다시 실행하지 않는다.
- `selectionState`, `handleNodeTap`, `findDirectEdges`, `applySingleFocus`, `applyPairFocus`, `renderPairDetail`이 있다.
- `focusNode`, `focusEdge`, `clearFocus`가 있더라도 새 선택 모델로 라우팅된다.
- `renderRelationList`, `bindRelationButtons`, `.relation-list`, `[data-next-node-id]`가 있다.
- `.pair-node`, `.pair-edge`, `.dimmed`가 있다.
- 노드 클릭 패널에서 이어진 관계의 이름과 방향을 확인할 수 있다.
- 쌍 선택 패널의 관계 칸은 `.relation-card` 전용 디자인을 쓰며, 시작 노드 카드와 종료 노드 카드 사이의 중간 정보처럼 읽힌다. 연결 표시는 얇은 상하 hint 정도로 제한하고, 장식 화살표처럼 튀지 않는다. 관계 칸 안에 별도 `관계` 제목이나 `source → target` 경로를 반복하지 말고, 실제 관계 문구를 왼쪽 정렬의 본문처럼 둔다.
- 노드 클릭은 후보 노드 전체를 그래프에서 강조하지 않고, 오른쪽 패널의 다음 후보로만 보여준다.
- 엣지 클릭은 두 끝 노드와 해당 관계선만 강조한다.
- 노드 라벨, 관계선, 화살표 촉은 한눈에 읽힐 만큼 커야 한다. 정확한 수치는 템플릿의 현재 기준을 따른다.
- 내부 UI 요소는 노드와 비슷한 radius로 보여서 구조도 전체의 형태 언어가 맞는다.
- 노드와 엣지 클릭 설명이 있다.
- HTML만 열어도 무엇과 무엇이 왜 연결되는지 알 수 있다.
- 글 목록이나 중앙 방사형 포스터가 아니라 구조 판단으로 보인다.
- CSS 카드 예외를 썼다면 Cytoscape를 쓰지 않은 이유가 남아 있다.

기계 검증은 상위 `쉬운 설명` 산출물 폴더에서 아래 명령을 우선한다.

```bash
python3 visual-explainer/scripts/validate-output.py /path/to/output-dir --require-structure-map-renderer
```

## 금지

- 모든 입력을 시스템 관계도나 조직도처럼 만들지 않는다.
- 일반 산출물에서 renderer 없이 `structure-map.html`을 직접 조립하지 않는다.
- bullet 목록을 HTML로 감싼 수준에서 끝내지 않는다.
- 이유 없는 중앙 노드와 대칭 배치로 끝내지 않는다.
- 노드-엣지 관계가 중요한데 CSS 카드 배치와 선 장식만으로 끝내지 않는다.
- 모바일에서 관계선이나 관계 라벨이 모두 사라지게 만들지 않는다.
