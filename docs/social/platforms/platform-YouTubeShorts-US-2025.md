# Platform Packet: YouTube Shorts / US / 2025

## Packet Metadata
- packet_id: PLT-YTS-US-2025
- stable_search_ids: [YouTube_Shorts, Google, YouTube, YouTubeShorts_US, United_States, US_market]
- packet_version: 1.0
- enrichment_status: fully_enriched
- last_updated_utc: 2026-03-26T14:00:00Z

## Identity
- platform_id: YouTube_Shorts
- market: US
- content_formats: [short_video, long_form_video, live, community_post]
- track_applicability: [mainstream, hybrid, niche]
- official_docs:
  - community_guidelines_url: https://www.youtube.com/communityguidelines
  - ads_policy_url: https://support.google.com/youtube/answer/2801973
  - ai_content_policy_url: https://support.google.com/youtube/answer/12308490

## Audience & Usage
- monthly_active_users_m: 150  # source: businessofapps_youtube_statistics_2025 | quality: high
- daily_active_users_m: 110  # source: internal_estimate | quality: medium
- shorts_daily_views_b: 70  # source: business_insider_2024 | quality: high
- age_distribution_estimate:  # source: similarweb_2024 | quality: medium
  - 13-17: 10
  - 18-24: 30
  - 25-34: 32
  - 35-44: 16
  - 45+: 12
- gender_split_pct:
  - f: 46
  - m: 54
- device_split_pct:
  - mobile: 90
  - desktop: 10
- avg_daily_minutes_per_user: 32  # source: internal_estimate | quality: medium
- primary_use_cases: [entertainment, education, music, comedy, how_to, product_reviews]
- peak_usage_hours_utc: [18:00, 19:00, 20:00, 21:00, 22:00]
- user_intent_breakdown:
  - passive_consumption: 60
  - active_engagement: 25
  - content_creation: 15
- demographic_notes: Most balanced gender split of major platforms. Strong 18-34 demographic. High intent for educational and how-to content. Higher income correlation than TikTok.

## Creator Performance
- avg_reach_rate_pct_short_video: 7.5
- avg_engagement_rate_pct_short_video: 3.2
- avg_engagement_rate_pct_long_video: 4.5
- creator_discoverability_1_5: 3.5
- algorithm_volatility_1_5: 3.5
- short_video_weight_1_5: 4
- long_form_weight_1_5: 5
- content_creation_barrier_1_5: 3.5
- fyp_forgiveness_factor_1_5: 3.5
- notes_creator_growth:
  - bullet_1: Shorts serve as discovery funnel to long-form content; cross-promotion heavily rewarded.
  - bullet_2: YouTube Partner Program (YPP) required for monetization; 1k subscribers + 4k watch hours (or 10M Shorts views in 90 days).
  - bullet_3: Shorts feed algorithm separate from main recommendation but gaining prominence.
  - bullet_4: Channel growth faster on Shorts for entertainment/comedy niches.
  - bullet_5: Audio library access for music and sound effects is major advantage.
  - bullet_6: Thumbnails and titles matter even for short-form content.

## Monetization Context
- supported_monetization_methods: [ad_revenue_share, super_thanks, channel_memberships, brand_deals, affiliate_links, YouTube_Shopping]
- conversion_to_paid_pct_estimate: 2.8
- avg_revenue_per_paying_user_usd_estimate: 4.50
- tip_or_gift_usage_notes:
  - bullet_1: Shorts Feed Ads revenue share: creators receive 45% of ad revenue from Shorts (variable CPM $0.01-0.06 per view).
  - bullet_2: Super Thanks available on both Shorts and long-form for one-time tips.
  - bullet_3: Channel memberships require 30k+ subscribers (or 500k short-form views in last 90 days).
  - bullet_4: Brand deals highly lucrative; $200-$2,000 per 10k followers for established channels.
- payout_stability_1_5: 4.5
- threshold_requirements_summary:
  - bullet_1: YPP requires 1k subscribers + 4k watch hours (or 10M valid Shorts views in 90 days).
  - bullet_2: Shorts monetization specifically: 4k watch hours or 10M Shorts views in 90 days.
  - bullet_3: Super Thanks requires YPP enrollment.
  - bullet_4: Shopping features require 10k subscribers.

## Policy & Risk
- explicit_sexual_content_allowed: false
- nudity_policy_notes: Severe restrictions; nudity not permitted except in limited educational/artistic contexts. More restrictive than TikTok or Instagram.
- ai_content_disclosure_required: true
- ai_content_policy_version: 2024
- ai_policy_summary:
  - bullet_1: Inherits YouTube AI content policies
  - bullet_2: Altered content label required for AI-generated or modified videos
  - bullet_3: Voice cloning audio requires disclosure
  - bullet_4: Photorealistic content requires heightened disclosure
- ai_enforcement_mechanisms:
  - automated_detection: true
  - ai_label_tool: altered_content_label
  - reach_penalty_for_unlabeled: demonetization
  - content_removal_threshold: medium
- ai_content_monetization: allowed_with_disclosure
- ai_policy_enforcement_notes: AI-generated content must be disclosed. Synthetic media depicting real people requires disclosure label.
- enforcement_style_summary:
  - bullet_1: More conservative content policies than competitors; demonetization common for borderline content.
  - bullet_2: Three-strike system for community guideline violations.
  - bullet_3: Appeals process transparent but slow.
- policy_enforcement_volatility_1_5: 3.5
- brand_safety_score_1_5: 4.5
- age_gate_confidence_1_5: 4.5
- takedown_appeal_success_rate_pct: 40

## Strategic Fit by Track
- mainstream_fit_notes:
  - bullet_1: Best-in-class monetization for video creators.
  - bullet_2: Strong for entertainment, education, and how-to content.
  - bullet_3: Shorts-to-long-form funnel highly effective for revenue generation.
- hybrid_fit_notes:
  - bullet_1: Excellent cross-promotion between Shorts and long-form content.
  - bullet_2: Strong brand advertising ecosystem.
  - bullet_3: Good for building loyal subscriber base.
- niche_fit_notes:
  - bullet_1: Educational and tutorial niches perform exceptionally well.
  - bullet_2: Gaming, tech, and comedy niches dominant.
  - bullet_3: Music promotion highly effective via Shorts.
- adult_fit_notes:
  - bullet_1: NOT suitable for explicit adult content.
  - bullet_2: Strict enforcement; immediate demonetization and potential termination.
  - bullet_3: Alternative platforms (OnlyFans, Fansly) required for adult content creators.

## Content Format Specifics
- short_video:
  - max_duration_sec: 60 (increased from 60 to 180 in late 2024; 60 optimal)
  - optimal_duration_sec: 30-45
  - aspect_ratios: [9:16, 1:1]
  - trending_audio_importance_1_5: 4
- long_form:
  - min_duration_minutes: 1
  - optimal_duration_minutes: 8-20
- live:
  - avg_viewer_count: 200-500 for mid-tier creators
  - interactive_features: [super_chat, super_stickers, memberships]

## Competitive Landscape
- key_competitors: [TikTok, Instagram_Reels, Snapchat_Spotlight]
- platform_strengths:
  - bullet_1: Highest CPM and monetization potential among short-form platforms.
  - bullet_2: Only platform where short-form can directly feed long-form revenue.
  - bullet_3: Massive existing creator ecosystem and brand advertising market.
  - bullet_4: Robust audio library and music licensing.
- platform_weaknesses:
  - bullet_1: Shorts algorithm less proven for viral discovery than TikTok.
  - bullet_2: Higher content production standards expected.
  - bullet_3: Monetization thresholds higher than competitors.

## Data Provenance
- sources:
  - pew_social_media_demographics_2025
  - youtube_creator_insights_2025
  - google_creator_connector_2025
  - tubefilter_creator_economy_2025
- last_updated_utc: 2026-03-26T14:00:00Z

## Enrichment Queries
- audience_metrics:
  - query: "YouTube Shorts US monthly active users 2025"
  - query: "YouTube Shorts US user demographics 2025"
  - query: "YouTube Shorts US average view duration 2025"
  - query: "YouTube Shorts US engagement rates 2025"
- creator_metrics:
  - query: "YouTube Shorts US creator growth statistics 2025"
  - query: "YouTube Shorts US algorithm discovery 2025"
  - query: "YouTube Shorts US payment per view 2025"
  - query: "YouTube Shorts US CPM rates by niche 2025"
- monetization_data:
  - query: "YouTube Shorts US creator fund payment rates 2025"
  - query: "YouTube Shorts US revenue share 2025"
  - query: "YouTube Shorts US brand deals average cost 2025"
  - query: "YouTube Shorts US monetization requirements 2025"
- policy_enforcement:
  - query: "YouTube Shorts US content policy 2025"
  - query: "YouTube Shorts US music copyright 2025"
  - query: "YouTube Shorts US demonetization reasons 2025"
  - query: "YouTube Shorts US advertiser friendly guidelines 2025"