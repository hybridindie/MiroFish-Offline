# API Payload Templates

These payloads match the current backend routes.

## 1) Generate ontology

POST /api/graph/ontology/generate

Form fields:
- files: one or more files
- simulation_requirement: required
- project_name: optional
- additional_context: optional

## 2) Build graph

POST /api/graph/build

{
  "project_id": "proj_xxxx",
  "graph_name": "vi-adult-us",
  "chunk_size": 500,
  "chunk_overlap": 50
}

## 3) Create simulation

POST /api/simulation/create

{
  "project_id": "proj_xxxx",
  "enable_twitter": true,
  "enable_reddit": true
}

## 4) Prepare simulation

POST /api/simulation/prepare

{
  "simulation_id": "sim_xxxx",
  "entity_types": ["Creator", "AudienceSegment", "PlatformStakeholder"],
  "use_llm_for_profiles": true,
  "parallel_profile_count": 5,
  "force_regenerate": false
}

## 5) Poll preparation status

POST /api/simulation/prepare/status

{
  "simulation_id": "sim_xxxx"
}

## 6) Start simulation

POST /api/simulation/start

{
  "simulation_id": "sim_xxxx",
  "platform": "parallel",
  "max_rounds": 120,
  "enable_graph_memory_update": true,
  "force": false
}

## 7) Monitor run

GET /api/simulation/sim_xxxx/run-status
GET /api/simulation/sim_xxxx/actions
GET /api/simulation/sim_xxxx/timeline
GET /api/simulation/sim_xxxx/agent-stats
GET /api/simulation/sim_xxxx/posts

## 8) Generate report

POST /api/report/generate

{
  "simulation_id": "sim_xxxx",
  "force_regenerate": false
}

## 9) Poll report status

POST /api/report/generate/status

{
  "simulation_id": "sim_xxxx"
}

## 10) Ask report agent follow-up questions

POST /api/report/chat

{
  "simulation_id": "sim_xxxx",
  "message": "Rank market-platform options by demographic fit and risk-adjusted growth.",
  "chat_history": []
}
