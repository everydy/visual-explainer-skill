---
name: comparison-html
description: "`쉬운 설명` 하위 스킬. 선택지, 관점, 장단점, 차이, 추천 상황을 한눈에 비교하는 `comparison.html`을 만든다. 표, 카드 비교, 기준별 매트릭스, 점수형 비교, before/after, 토글 비교 중 적합한 방식을 고른다."
metadata:
  short-description: comparison.html 비교 시각화 생성
---

# comparison-html

`comparison.html` 하나를 책임지는 하위 스킬이다.

## 검색 호출어

영어 호출어 `comparison html`이 보이면 이 스킬을 우선한다.

- `comparison html`
- `comparison-html`
- `comparison.html`
- `비교 HTML`
- `비교표 HTML`

## 역할

선택지, 관점, 장단점, 차이, 추천 상황을 한눈에 비교하게 만든다.

## 입력

- 비교할 대상들
- 비교 기준
- 장점, 약점, 리스크, 추천 상황
- 저장 파일명: `comparison.html`

## 디자인 판단

- 표, 카드 비교, 기준별 매트릭스, 점수형 비교, before/after, 토글 비교 중 무엇이 가장 맞는지 고른다.
- 비교 기준을 몇 개로 줄여야 한눈에 보이는지 정한다.
- 사용자의 판단을 빠르게 만드는 차이를 강조한다.

## 산출물

- `comparison.html`
- 비교 대상, 비교 기준, 핵심 차이, 추천 상황을 포함한다.

## 검증

- 비교 기준이 명확하다.
- 대상별 차이가 한 화면에서 보인다.
- 장점만 있지 않고 약점이나 리스크도 보인다.
- 사용자가 그래서 뭐가 다른지 바로 말할 수 있다.

## 금지

- 한쪽 선택지를 근거 없이 밀어주지 않는다.
- 모든 차이를 길게 나열해 비교표를 읽기 어렵게 만들지 않는다.
