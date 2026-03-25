# Data Requirements

Use this checklist to assemble the source packet for each track.

## Minimum data package per track

1. Demographics
- Region-level age distribution (adult segments only for adult track)
- Gender split
- Language preferences
- Device and usage-time patterns

2. Platform visibility
- Reach and discoverability assumptions
- Typical content format performance
- Engagement norms by platform
- Algorithm volatility notes

3. Growth indicators
- Follower growth benchmarks
- Retention and repeat engagement rates
- Community participation indicators
- Trend half-life assumptions

4. Monetization indicators
- Subscription conversion benchmarks
- Pricing band references
- Tip and upsell behavior assumptions
- Churn references at 30/60/90 days

5. Policy and compliance
- Platform terms and policy excerpts
- Age-verification requirements
- Regional legal constraints
- Payment processor constraints

6. Competitive landscape
- Comparable virtual influencer profiles
- Channel mix examples
- Content cadence benchmarks
- Failure case examples

## Suggested source file structure

Create one folder per track and place all source files there.

Example:
- input/mainstream/
- input/hybrid/
- input/adult/

Inside each folder include:
- demographics.csv
- platform_metrics.csv
- monetization_benchmarks.csv
- policy_notes.md
- competitors.md
- assumptions.md

## Assumption standardization

To keep cross-track comparisons fair, lock these assumptions before running:

1. Time horizon and simulation rounds
2. Content production cadence
3. Creative quality baseline
4. Budget envelope
5. Team operating constraints

## Adult-track specific requirements

1. 18+ audience assumptions only
2. Explicit age-gating and moderation assumptions
3. Jurisdiction-specific legal notes
4. Payment and deplatform contingency notes
5. Brand partnership exclusion and approval criteria

## Assembled package in this repo

Use the prepared structure at:
- docs/scenarios/virtual-influencer-market-platform/input/

Track folders:
- docs/scenarios/virtual-influencer-market-platform/input/mainstream/
- docs/scenarios/virtual-influencer-market-platform/input/hybrid/
- docs/scenarios/virtual-influencer-market-platform/input/adult/

Shared provenance log:
- docs/scenarios/virtual-influencer-market-platform/input/source-log.csv
