# Input Data Package

This folder contains the structured source packet used by the scenario.

## Structure

- mainstream/
- hybrid/
- adult/

Each track folder contains:
- demographics.csv
- platform_metrics.csv
- monetization_benchmarks.csv
- policy_notes.md
- competitors.md
- assumptions.md

## How to use

1. Fill assumptions first and keep time horizon and budget consistent across tracks.
2. Fill demographics and platform metrics from validated third-party sources.
3. Document source links and confidence in source-log.csv.
4. Keep adult track strictly 18+ and include compliance controls.

## Recommended evidence quality flags

- high: direct platform release, regulator source, audited market report
- medium: reputable industry publication, triangulated estimates
- low: anecdotal, single-source estimate, unverified benchmark
