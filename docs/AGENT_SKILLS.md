# RecallRadar AI Agent Skills

## Purpose

This project can use selected skills from https://www.skills.sh/ to guide implementation. Skills are installed only when they directly support the RecallRadar build.

## Installed Skills

### fastapi-python

Source:

```text
https://github.com/mindrally/skills --skill fastapi-python
```

Use for:

- FastAPI backend structure.
- Pydantic patterns.
- Async API design.
- Dependency injection.
- Backend error handling.
- Clean Python service boundaries.

### next

Source:

```text
https://github.com/hairyf/skills --skill next
```

Use for:

- Next.js application structure.
- App Router patterns.
- Server and client component decisions.
- Data fetching.
- Routing and layouts.
- Frontend performance conventions.

### tailwindcss

Source:

```text
https://github.com/mindrally/skills --skill tailwindcss
```

Use for:

- Responsive dashboard styling.
- Utility-first component layout.
- Consistent spacing and visual hierarchy.
- Mobile-friendly operational screens.

### postgresql-best-practices

Source:

```text
https://github.com/mindrally/skills --skill postgresql-best-practices
```

Use for:

- PostgreSQL schema design.
- Index selection.
- JSONB usage.
- UUID and timestamp conventions.
- Query and performance considerations.

### transformers-huggingface

Source:

```text
https://github.com/mindrally/skills --skill transformers-huggingface
```

Use for:

- Hugging Face Transformers integration.
- Model selection.
- Text classification.
- Summarization.
- Sentence similarity.
- Token classification.
- Later document and vision model integration.

### create-project-app

Source:

```text
C:\Users\Conno\.codex\skills\create-project-app
```

Use for:

- Turning generated app ideas into coding-ready project prep.
- Creating required docs before implementation.
- Locking MVP scope, architecture, data model, API design, UX direction, testing, deployment, and final implementation plans.
- Repeating the RecallRadar-style preparation workflow for future projects.

### shadcn

Source:

```text
https://github.com/shadcn/ui --skill shadcn
```

Use for:

- Component composition guidance.
- Accessible dashboard primitives.
- Premium card, badge, table, dialog, and feedback patterns.
- Keeping the redesign polished without sacrificing readability or workflow clarity.

## Skills Considered But Not Installed

### Playwright

Playwright/browser automation is useful for RecallRadar, but the visible skills.sh audit metadata for the first Playwright options was weaker than the core skills installed above.

Decision:

- Do not install a Playwright skill yet.
- Use direct Playwright tooling or project-local tests when frontend verification begins.
- Revisit skill installation later if a stronger audited option is preferred.

### Redis

Redis is useful for V2 background jobs, but V1 can start with synchronous calls or simple FastAPI background tasks.

Decision:

- Do not install Redis-specific skills before V1 implementation.
- Revisit when adding queues, caching, or async inference workers.

## Usage Rule

Before using an installed skill in a future implementation step, read that skill's `SKILL.md` and follow only the parts relevant to the current task.
