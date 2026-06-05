# Visual Explainer Skill Bundle

Standalone Codex skill bundle for Korean easy explanations with four generated HTML views.

## Included Skills

- `visual-explainer`: orchestrates the full Easy Explanation workflow.
- `structure-map-html`: creates a relationship and concept map.
- `flow-html`: creates a process or routing flow.
- `comparison-html`: creates a comparison view.
- `mini-slide-html`: creates a compact slide-style explanation.

## Install

Install all five skill folders from this repo:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo everydy/visual-explainer-skill \
  --path visual-explainer structure-map-html flow-html comparison-html mini-slide-html
```

Restart Codex after installing so the new skills are discovered.

## Trigger

Use phrases such as:

- `쉬운 설명`
- `쉬운설명`
- `$쉬운 설명`
- `visual-explainer`
- `HTML로 쉽게 설명`

The main skill writes a chat explanation and routes to the four HTML subskills.
