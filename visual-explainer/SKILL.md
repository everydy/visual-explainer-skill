---
name: 쉬운 설명
description: 어려운 개념, 구조, 흐름, 비교를 공부하듯 이해해야 할 때 쓰는 설명 오케스트레이터. 채팅창에는 친절한 공부용 설명을 쓰고, 항상 `structure-map.html`, `flow.html`, `comparison.html`, `mini-slide.html` 네 HTML 문서를 만들도록 하위 스킬을 라우팅한다. `쉬운설명`, `쉬운 설명`, `$쉬운설명`, `$쉬운 설명`, `비주얼 익스플레이너`, `visual-explainer`, `HTML로 시각화`, `PPT처럼 설명` 요청에 사용한다.
metadata:
  short-description: 쉬운 설명, HTML 시각화 설명 오케스트레이터
---

# 쉬운 설명

복잡한 내용을 공부하듯 이해해야 할 때 쓰는 상위 스킬이다.

이 스킬은 모드를 고르지 않는다. 한 번 실행하면 항상 같은 기본 묶음을 만든다.

1. 채팅창 공부용 설명
2. `structure-map.html`
3. `flow.html`
4. `comparison.html`
5. `mini-slide.html`

## 언제 쓸까

- 사용자가 “쉽게 설명”, “쉬운 설명”, “구조적으로 보여줘”라고 했다.
- 어려운 용어와 개념을 같이 공부해야 한다.
- 여러 개념의 관계, 흐름, 비교가 한 번에 얽혀 있다.
- HTML, 이미지, PPT식 설명, 시각 자료가 필요하다.

## 검색 호출어

아래 표현이 보이면 이 스킬을 우선한다.

- `쉬운 설명`
- `쉬운설명`
- `쉬운 설명 스킬`
- `$쉬운설명`
- `$쉬운 설명`
- `비주얼 익스플레이너`
- `visual-explainer`
- `HTML로 쉽게 설명`
- `구조도로 쉽게 설명`

## 오케스트레이터 계약

- 먼저 채팅창에 친절한 공부용 설명을 쓴다.
- 어려운 용어는 채팅 설명과 HTML의 보이는 문구 모두에서 첫 등장 때 바로 푼다.
- 네 하위 스킬을 모두 호출하는 고정 fan-out 구조로 진행한다.
- 어떤 HTML을 만들지 선택하지 않는다. 항상 네 개를 모두 만든다.
- 하위 스킬의 세부 디자인은 각 하위 스킬이 판단한다.
- 하위 스킬을 호출할 때 `반드시 풀어야 하는 어려운 용어` 목록과 각 뜻풀이를 함께 넘긴다.
- 최종 답변에는 네 HTML 파일 링크를 모두 제공한다.
- 네 HTML을 어떤 순서로 보면 좋은지 짧게 안내한다.

## 어려운 용어 풀이 규칙

`plain-language-closeout`의 어려운 용어 풀이 규칙을 이 스킬에도 적용한다. 이 규칙은 채팅창 설명뿐 아니라 `structure-map.html`, `flow.html`, `comparison.html`, `mini-slide.html` 안의 제목, 카드, 노드, 관계 라벨, 범례, 캡션 같은 보이는 문구에도 적용한다.

- 어려운 용어를 쓰면 첫 등장 때 같은 줄이나 같은 카드 안에서 바로 뜻을 푼다.
- 채팅창에서는 첫 등장을 `**용어**(뜻풀이)` 형식으로 쓴다.
- HTML 안에서는 첫 등장을 `용어(뜻풀이)`처럼 인라인으로 풀거나, 공간이 좁으면 제목은 짧게 두고 바로 아래 보조 문구에서 뜻을 푼다.
- 같은 산출물 안에서 이미 풀어쓴 용어는 이후에 `용어`만 써도 된다.
- 영어 기술어는 제품명, 파일명, 명령어, 실제 UI 라벨처럼 꼭 필요한 경우에만 남긴다.
- 내부 작업 이름, CLI 상태명, 아키텍처 용어를 그대로 보여줘야 하면, 사용자가 이해할 수 있는 생활어 풀이를 곁들인다.
- 노드나 버튼처럼 공간이 좁은 요소에는 어려운 용어만 단독으로 두지 않는다. 짧은 제목과 쉬운 보조 설명을 함께 둔다.
- 용어 풀이가 화면을 복잡하게 만들면 용어 수를 줄이고, 핵심 5-12개만 먼저 푼다.

## 하위 스킬

- `structure-map-html`: 개념 관계와 구조를 보여준다.
- `flow-html`: 절차, 순서, 라우팅, 분기를 보여준다.
- `comparison-html`: 선택지와 관점 차이를 비교한다.
- `mini-slide-html`: 작은 슬라이드 묶음처럼 핵심을 넘겨 보게 한다.

`structure-map.html`을 만들 때는 `structure-map-html`의 JSON config를 먼저 만들고 `structure-map-html/scripts/render-structure-map.mjs`로 생성한다. 관계 구조도가 필요한데 HTML을 처음부터 새로 짜지 않는다.

```bash
node structure-map-html/scripts/render-structure-map.mjs \
  --config /path/to/structure-map.config.json \
  --out /path/to/output-dir/structure-map.html
```

config의 세부 필드와 자유도 경계는 `structure-map-html/references/config-contract.md`를 필요할 때만 읽는다.

구조도 템플릿의 시각 기준은 `structure-map-html` 하위 스킬이 소유한다. 노드 라벨 크기, 관계 라벨 크기, 관계 라벨 위치, 노드 박스 크기처럼 사용자가 화면에서 직접 보는 기준을 바꿀 때는 템플릿만 고치지 않고 `structure-map-html/SKILL.md`와 `scripts/validate-output.py`도 함께 맞춘다.

## 입력 정리

하위 스킬을 호출하기 전에 아래를 짧게 정리한다.

- 설명 대상 원문
- 핵심 개념 목록
- 반드시 풀어야 하는 어려운 용어와 쉬운 뜻풀이
- 대상 독자
- HTML 저장 폴더
- 각 HTML 파일명

용어 목록은 아래처럼 만든다.

```md
어려운 용어 풀이:
- PR lock: 이미 열린 PR이 끝날 때까지 새 실행을 막는 잠금
- route: 실행할 계획 문서를 받아 작업 queue로 넘기는 단계
- deferred request: 지금 실행하지 않고 나중에 다시 처리할 보류 요청
```

## 산출물 검증

완료 전 아래를 확인한다.

- 채팅 설명에 핵심 개념과 어려운 용어 풀이가 있다.
- 네 HTML의 주요 제목, 카드, 노드, 라벨에 어려운 용어가 단독으로 방치되지 않는다.
- 네 HTML 파일이 모두 만들어졌다.
- 네 링크가 실제 파일을 가리킨다.
- 최종 답변이 “무엇부터 보면 되는지”를 짧게 안내한다.

기계적으로 확인할 때는 아래 스크립트를 쓴다.

```bash
python3 scripts/validate-output.py /path/to/output-dir --last-message /path/to/last-message.md
```

이 스크립트는 네 HTML 파일 존재, 기본 HTML 구조, 최종 답변의 네 파일명 언급을 확인한다.
`structure-map.html`은 공식 Cytoscape 템플릿 표식과 핵심 인터랙션도 확인한다.
renderer 경로를 쓴 일반 산출물은 아래처럼 엄격 표식도 함께 확인한다.

```bash
python3 scripts/validate-output.py /path/to/output-dir --last-message /path/to/last-message.md --require-structure-map-renderer
```

## 금지

- 네 HTML 중 일부만 만들고 끝내지 않는다.
- `structure-map.html` 하나로 모든 시각화를 대체하지 않는다.
- HTML 링크 없이 채팅 설명만 하고 끝내지 않는다.
- 어려운 용어를 노드, 카드, 관계 라벨에 그대로 던져 두고 사용자가 추측하게 만들지 않는다.
- 깊은 설명이 필요 없는 짧은 마무리 답변에는 이 스킬을 쓰지 않는다. 그런 경우 `클로즈 아웃`이 맞다.
