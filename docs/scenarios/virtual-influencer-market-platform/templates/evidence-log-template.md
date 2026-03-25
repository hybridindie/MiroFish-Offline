# Evidence Log Template

Use this during and after simulation runs to capture traceable evidence behind recommendations.

| timestamp | track | market | platform | evidence_type | source_endpoint | summary | impact_dimension | confidence_low_med_high |
|---|---|---|---|---|---|---|---|---|
| 2026-03-18T00:00:00Z | adult | US | OnlyFans | action_pattern | /api/simulation/{id}/actions | Subscription intent rises after teaser cadence change | monetization | medium |
| 2026-03-18T00:00:00Z | hybrid | US | X + Reddit | sentiment_shift | /api/simulation/{id}/timeline | Polarization spike after policy event | risk | high |
| 2026-03-18T00:00:00Z | mainstream | US | TikTok | visibility_change | /api/simulation/{id}/posts | Reach decays after algorithm shift | visibility | medium |

## Notes

- Keep one evidence log per track.
- Tag each item with one primary impact dimension.
- Use this log when finalizing score adjustments.
