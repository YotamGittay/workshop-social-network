# Workshop Presentation Refinement Design

Date: 2026-09-16
Status: Approved

## Goal

Refine `docs/workshop-presentation.html` into an 18-slide, repo-first workshop deck based on the supplied *Software Engineering in the AI Era* notes.

## Audience and Emphasis

Students and recent graduates are the primary audience. The deck introduces agent-assisted engineering briefly, then teaches architecture and engineering judgment through this repository's React, FastAPI, PostgreSQL, MinIO, nginx, and Docker Compose implementation.

## Structure

The deck will contain exactly 18 slides:

1. Title and workshop premise
2. Learning outcomes
3. Engineer-agent workflow
4. Coding-agent anatomy and tool choice
5. Effective prompts and safe delegation
6. Application scope
7. Repository architecture
8. HTTP request path and API
9. Simplified identity and trust boundary
10. Relational data model
11. Feed query and scaling tradeoff
12. Photo storage and consistency
13. Stateful and stateless components
14. Docker Compose topology
15. Notes versus current implementation
16. Verification, testing, and observability
17. Cursor live-demo workflow
18. Closing checklist and discussion

## Editorial Direction

- Use factual titles such as “Application architecture,” “Feed query,” and “Verification.”
- Remove slogan-only transition slides and dramatic imperatives.
- Merge overlapping material instead of shrinking 47 slides into dense text.
- Preserve the central thesis: agents accelerate implementation while engineers retain responsibility.
- Keep product comparison brief and avoid volatile feature-by-feature rankings.
- Tie examples, paths, commands, and discrepancies to this repository.
- Keep one concise slide identifying differences between the PDF notes and current code.

## Visual and Interaction Design

- Retain the existing restrained editorial palette, typography, cards, tables, and code blocks.
- Keep keyboard, click, touch, hash navigation, overview, speaker notes, progress, and print support.
- Keep slides legible at 1440×900 and responsive on narrower screens.
- Avoid decorative title-only slides and unnecessary animation.

## Constraints

- One self-contained HTML file.
- No JavaScript or CSS dependencies beyond the existing web fonts.
- No application behavior or source-code changes outside the presentation.
- Preserve accurate repository facts and explicitly label teaching-only identity.

## Verification

- Confirm exactly 18 slide sections and 18 overview entries.
- Validate balanced section tags and required navigation script.
- Render representative content-heavy, code, table, and dark slides at 1440×900 using headless Chrome.
- Inspect screenshots for clipping, overflow, contrast, and excessive density.
