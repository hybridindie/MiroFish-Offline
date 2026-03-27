# Platform Packet: Facebook / US / 2025

## Packet Metadata
- packet_id: PLT-FB-US-2025
- stable_search_ids: [Facebook, Meta, Facebook_US, United_States, US_market]
- packet_version: 1.0
- enrichment_status: fully_enriched
- last_updated_utc: 2026-03-26T14:00:00Z

## Identity
- platform_id: Facebook
- market: US
- content_formats: [text_post, image_post, video, short_video, story, live, group, marketplace]
- track_applicability: [mainstream, hybrid, niche]
- official_docs:
  - community_guidelines_url: https://www.facebook.com/communitystandards
  - ads_policy_url: https://www.facebook.com/policies/ads
  - ai_content_policy_url: https://www.facebook.com/help/2307648819696455

## Audience & Usage
- monthly_active_users_m: 270  # source: businessofapps_facebook_statistics_2025 (North America) | quality: high
- daily_active_users_m: 195  # source: businessofapps_facebook_statistics_2025 (global DAU 2.145B) | quality: high
- global_mau_b: 3.08  # source: businessofapps_facebook_statistics_2025 | quality: high
- age_distribution_estimate:  # source: datareportal_hootsuite_2024 | quality: high
  - 13-17: 3
  - 18-24: 21.8
  - 25-34: 31.2
  - 35-44: 20.4
  - 45-54: 12.3
  - 55+: 14.3
- gender_split_pct:  # source: datareportal_hootsuite_2024 | quality: high
  - f: 43.5
  - m: 56.5
- device_split_pct:
  - mobile: 84.5
  - desktop: 14.3
  - desktop_only: 1.2
- avg_daily_minutes_per_user: 31.2  # source: statista_2024 | quality: high
- primary_use_cases: [social_connection, news_consumption, local_community, entertainment, marketplace, events]
- peak_usage_hours_utc: [11:00, 12:00, 13:00, 19:00, 20:00, 21:00]
- user_intent_breakdown:
  - passive_consumption: 60
  - active_engagement: 28
  - content_creation: 12
- demographic_notes: Largest reach of any platform. Skews older (35+) compared to TikTok/Instagram. Strong suburban and rural penetration. Highest income diversity.

## Creator Performance
- avg_reach_rate_pct_post: 3.2  # source: meta_creator_studio_2024 | quality: medium
- avg_reach_rate_pct_short_video: 5.8  # source: meta_creator_studio_2024 | quality: medium
- avg_engagement_rate_pct_post: 1.8  # source: influencermarketinghub_benchmark_2024 | quality: high
- avg_engagement_rate_pct_short_video: 2.9  # source: meta_creator_studio_2024 | quality: medium
- avg_engagement_rate_pct_video: 2.4  # source: meta_creator_studio_2024 | quality: medium
- engagement_rate_by_follower_size:
  - nano_1k_5k: 4.2  # source: influencermarketinghub_benchmark_2024 | quality: high
  - micro_5k_50k: 2.1  # source: internal_estimate | quality: medium
  - macro_1m_plus: 1.1  # source: influencermarketinghub_benchmark_2024 | quality: high
- creator_discoverability_1_5: 2.5
- algorithm_volatility_1_5: 3
- short_video_weight_1_5: 4
- content_creation_barrier_1_5: 2
- fyp_forgiveness_factor_1_5: 2.5
- avg_brand_deal_cost_usd: 380  # source: collabstr_2024 | quality: medium
- notes_creator_growth:
  - bullet_1: Organic reach severely limited; algorithm prioritizes friends/family content.
  - bullet_2: Facebook Reels receive algorithmic boost but still lower than Instagram Reels distribution.
  - bullet_3: Groups are most effective discovery mechanism for new audiences.
  - bullet_4: Cross-posting from Instagram receives reduced distribution.
  - bullet_5: Paid promotion almost essential for meaningful reach growth.
  - bullet_6: Longer-form video (in-feed) performs better than short-form for engagement.

## Monetization Context
- supported_monetization_methods: [ad_revenue_share, brand_deals, in_stream_ads, stars_tips, subscriber_badges, marketplace, subscriptions]
- conversion_to_paid_pct_estimate: 1.8  # source: internal_estimate | quality: low
- avg_revenue_per_paying_user_usd_estimate: 2.60  # source: internal_estimate | quality: low
- tip_or_gift_usage_notes:
  - bullet_1: Facebook Stars available during live streams ($0.01 per star to creator).
  - bullet_2: In-stream ads pay 55% revenue share to creators (minimum 10k followers).
  - bullet_3: Brand collaborations market available to eligible creators.
  - bullet_4: Subscriptions ($4.99-$49.99/month) for exclusive content.
- payout_stability_1_5: 3.5  # source: internal_estimate | quality: low
- threshold_requirements_summary:
  - bullet_1: In-stream ads require 10k followers and 600k total watch minutes in last 60 days.
  - bullet_2: Stars available to creators 18+ with 1k followers.
  - bullet_3: Subscriptions require 10k+ followers (varies).
  - bullet_4: Monetization Manager review required.

## Policy & Risk
- explicit_sexual_content_allowed: false
- nudity_policy_notes: More restrictive than Instagram; all nudity prohibited except breastfeeding in specific contexts. Artistic exceptions extremely limited.
- ai_content_disclosure_required: true
- ai_content_policy_version: 2024
- ai_policy_summary:
  - bullet_1: All AI-generated or AI-modified content must be labeled
  - bullet_2: "Made with AI" label available and promoted by Meta
  - bullet_3: Photorealistic AI content requires prominent disclosure
  - bullet_4: AI-generated text content does not require disclosure
  - bullet_5: Synthetic media depicting public figures restricted
- ai_enforcement_mechanisms:
  - automated_detection: true
  - ai_label_tool: meta_ai_label
  - reach_penalty_for_unlabeled: true
  - content_removal_threshold: medium
- ai_content_monetization: allowed_with_disclosure
- ai_policy_enforcement_notes: AI-generated content must be labeled. Meta's policies evolving rapidly; increased enforcement expected.
- enforcement_style_summary:
  - bullet_1: Automated enforcement dominant; inconsistent for borderline content.
  - bullet_2: Appeal process available but success rates low.
  - bullet_3: "Reduced distribution" more common than full takedown for minor violations.
- policy_enforcement_volatility_1_5: 3.5  # source: internal_estimate | quality: low
- brand_safety_score_1_5: 4  # source: internal_estimate | quality: low
- age_gate_confidence_1_5: 3.5  # source: internal_estimate | quality: low
- takedown_appeal_success_rate_pct: 25  # source: internal_estimate | quality: very_low

## Strategic Fit by Track
- mainstream_fit_notes:
  - bullet_1: Largest US user base; excellent for reach but limited engagement.
  - bullet_2: Strong for local community building and events.
  - bullet_3: Facebook Groups powerful for niche community building.
  - bullet_4: Marketplace valuable for e-commerce integration.
- hybrid_fit_notes:
  - bullet_1: Facebook Marketplace provides e-commerce opportunity.
  - bullet_2: Groups can drive high-intent audiences.
  - bullet_3: Lower CPMs than Instagram but larger reach potential.
- niche_fit_notes:
  - bullet_1: Groups are best discovery mechanism for niche interests.
  - bullet_2: Local/niche community pages can build loyal followings.
  - bullet_3: Marketplace useful for physical product niches.
- adult_fit_notes:
  - bullet_1: NOT suitable for explicit adult content.
  - bullet_2: Strict enforcement; immediate account restrictions.
  - bullet_3: Use as discovery only with strict age-gated approach.

## Content Format Specifics
- short_video:
  - max_duration_minutes: 4
  - optimal_duration_minutes: 1-2
  - aspect_ratios: [16:9, 4:5, 1:1, 9:16]
- story:
  - max_duration_sec: 20 (photo), 30 (video)
- live:
  - max_duration_hours: 8
  - interactive_features: [stars, reactions, live_polls, live_qa]
- group:
  - max_members: 100k+
  - private_group_availability: true

## Competitive Landscape
- key_competitors: [TikTok, Instagram, YouTube, Snapchat, LinkedIn]
- platform_strengths:
  - bullet_1: Largest overall user base in US.
  - bullet_2: Facebook Groups provide unique community-building capability.
  - bullet_3: Marketplace integration for e-commerce.
  - bullet_4: Strong event and local community features.
- platform_weaknesses:
  - bullet_1: Lowest organic reach among major platforms for creators.
  - bullet_2: Demographic skews older; younger audiences migrating to TikTok/Instagram.
  - bullet_3: Monetization significantly less lucrative than Instagram or YouTube.

## Data Provenance
- sources:
  - pew_social_media_demographics_2025
  - meta_company_data_2025
  - facebook_creator_insights_2025
  - hootsuite_social_media_report_2025
- last_updated_utc: 2026-03-26T14:00:00Z

## Enrichment Queries
- audience_metrics:
  - query: "Facebook US monthly active users 2025"
  - query: "Facebook US user demographics age distribution 2025"
  - query: "Facebook US average session duration 2025"
  - query: "Facebook US device usage mobile vs desktop 2025"
- creator_metrics:
  - query: "Facebook creator reach rate engagement rate 2025"
  - query: "Facebook algorithm discoverability new creators 2025"
  - query: "Facebook Creator Studio tools 2025"
  - query: "Facebook average CPM cost per thousand 2025"
- monetization_data:
  - query: "Facebook in-stream ads revenue share 2025"
  - query: "Facebook Stars payout rates 2025"
  - query: "Facebook brand deal average cost 2025"
  - query: "Facebook conversion rate free to paid 2025"
- policy_enforcement:
  - query: "Facebook content policy enforcement 2025"
  - query: "Facebook appeal success rate 2025"
  - query: "Facebook brand safety score advertisers 2025"
  - query: "Facebook age verification effectiveness 2025"