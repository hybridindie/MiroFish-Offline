# Execution Playbook

This playbook maps the scenario to MiroFish-Offline workflow and API routes.

## Objective

Identify the best market and platform mix for a virtual influencer initiative, including a mainstream track and an adult-platform track, using comparable metrics.

## Scenario tracks to run

Run at least three tracks with the same base narrative.

1. Mainstream track
- Discovery: short-form video and mainstream social channels
- Conversion: community and creator support channels

2. Hybrid track
- Discovery: mainstream channels
- Conversion: mixed premium channels and owned audience channels

3. Adult-platform track
- Discovery: age-compliant teaser channels only
- Conversion: adult subscription channel (for example, OnlyFans)
- Guardrails: strict 18+, legal review, payment continuity planning

## Required setup

1. Infrastructure
- Backend, frontend, Neo4j, and LLM model are running.
- Models needed include your chat model and embedding model.

2. Input package
- Market demographic datasets by region
- Platform audience and policy summaries
- Competitor examples
- Revenue benchmark assumptions

3. Project naming
- Use one project per scenario track to keep outputs clean.
- Suggested naming: vi-mainstream-us, vi-hybrid-us, vi-adult-us

## Runbook by application step

### Step 1: Ontology generation

Route: POST /api/graph/ontology/generate

What to provide:
- files: market and platform evidence files
- simulation_requirement: scenario objective, target audience, constraints
- project_name: explicit track name
- additional_context: optional policy and legal notes

Success criteria:
- ontology generated
- project_id captured

### Step 1b: Graph build

Route: POST /api/graph/build

What to provide:
- project_id
- optional graph_name

Success criteria:
- task completes
- graph_id captured

### Step 2: Simulation environment setup

Route: POST /api/simulation/create

What to provide:
- project_id
- graph_id optional if already attached to project

Then call: POST /api/simulation/prepare

What to provide:
- simulation_id
- optional entity_types if you want to constrain personas
- use_llm_for_profiles true
- parallel_profile_count default 5
- force_regenerate false unless rerunning

Monitor with: POST /api/simulation/prepare/status

Success criteria:
- status becomes ready
- profile files and simulation config are generated

### Step 3: Run simulation

Route: POST /api/simulation/start

What to provide:
- simulation_id
- platform parallel
- max_rounds set to your test horizon
- enable_graph_memory_update true for richer report evidence

Monitor with:
- GET /api/simulation/{simulation_id}/run-status
- GET /api/simulation/{simulation_id}/actions
- GET /api/simulation/{simulation_id}/timeline
- GET /api/simulation/{simulation_id}/agent-stats
- GET /api/simulation/{simulation_id}/posts

Success criteria:
- run reaches completed state
- action and post logs are non-empty

### Step 4: Generate report

Route: POST /api/report/generate

What to provide:
- simulation_id
- force_regenerate false

Monitor with: POST /api/report/generate/status

Optional analysis chat:
- POST /api/report/chat

Success criteria:
- report status completed
- report content and supporting evidence available

## Scoring framework

Use the CSV template in templates/platform-market-scoring-template.csv.

Weighted score:

MarketPlatformScore = 0.30 D + 0.25 V + 0.20 G + 0.20 M - 0.05 R

Where:
- D = demographic fit score (0-100)
- V = visibility score (0-100)
- G = growth score (0-100)
- M = monetization score (0-100)
- R = risk penalty score (0-100)

## Adult-platform decision gates

A track is no-go if any of these are true:

1. Compliance risk score above 70
2. Age-gating confidence below your policy threshold
3. Revenue concentration above 60 percent on a single adult platform without fallback
4. Missing legal review for target geography

## Recommended outputs

For each track, produce:

1. Top market-platform recommendations
2. Segment-level demographic fit notes
3. Visibility and growth drivers by platform
4. Monetization assumptions and sensitivity
5. Risk register and mitigations
6. Go or no-go recommendation with triggers

## Quality checks before final decision

1. Verify assumptions were consistent across tracks
2. Confirm no minors or mixed-age targeting assumptions were used in adult track
3. Check that risk penalties were applied, not ignored
4. Confirm each recommendation has an operational fallback plan
