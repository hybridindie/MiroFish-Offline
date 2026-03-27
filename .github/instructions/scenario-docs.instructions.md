---
description: "Scenario-documentation guidance for market/platform prompts, especially when updating platform assumptions, risk priors, and real-vs-virtual creator analysis."
applyTo: "docs/scenarios/**"
---

# Scenario Documentation Guidelines

## Source Of Truth
- Treat the platform packets in `docs/social/` as the factual source for platform ownership, AI-content policy, geography, monetization, and enforcement assumptions.
- Use the supporting corpus in `docs/social/` for persona, journey, topic, and integration context when a scenario prompt makes cross-platform or audience claims.
- Prefer conditional wording when a source describes evolving policy or partial compatibility instead of a universal rule.

## Conventions
- Keep scenario prompts aligned with the latest packet data and avoid combining separate platform policy families into a single claim.
- Distinguish platform ownership and policy stacks accurately. For example, Lemon8 should follow ByteDance assumptions rather than Meta assumptions unless the source corpus says otherwise.
- Treat regional short-video platforms such as Kwai as separate concentration risks unless the source corpus explicitly groups them with another ownership or policy cluster.
- For adult-platform recommendations, avoid absolute claims about AI-creator compatibility. Include rights, identity, disclosure, payment, and legal caveats when the corpus indicates evolving rules.
- Preserve the existing scoring, event, and decision-output structure when refreshing factual priors in a prompt template.

## Key Reference Files
- Prompt templates: `docs/scenarios/virtual-influencer-market-platform/templates/`
- Platform packets: `docs/social/`
- Supporting corpus: `docs/social/integration/`, `docs/social/journeys/`, `docs/social/topics/`, `docs/social/personas/`