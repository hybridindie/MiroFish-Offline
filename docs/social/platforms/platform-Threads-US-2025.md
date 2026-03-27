# Platform Packet: Threads / US / 2025

## Packet Metadata
- packet_id: PLT-TH-US-2025
- stable_search_ids: [Threads, Meta, Instagram_Threads, Threads_US, United_States, US_market]
- packet_version: 1.0
- enrichment_status: fully_enriched
- last_updated_utc: 2026-03-26T14:00:00Z

## Identity
- platform_id: Threads
- market: US
- content_formats: [text_post, image_post, video, link_post, reply, quote_post]
- track_applicability: [mainstream, hybrid, niche]
- official_docs:
  - community_guidelines_url: https://help.instagram.com/groups/5870592419
  - terms_of_service_url: https://threads.net/legal/terms-of-service
  - content_policy_url: https://threads.net/legal/privacy-policy

## Audience & Usage
- monthly_active_users_m: 275  # source: businessofapps_threads_statistics_2025 (Nov 2024) | quality: high
- daily_active_users_m: 85  # source: internal_estimate | quality: medium
- launch_signups_m: 100  # source: businessofapps_threads_statistics_2025 (first 5 days) | quality: high
- age_distribution_estimate:  # source: sensor_tower_2023 | quality: high
  - 13-17: 5
  - 18-24: 37
  - 25-34: 35
  - 35-44: 15
  - 45+: 8
- gender_split_pct:
  - m: 52
  - f: 48
- device_split_pct:
  - mobile: 90
  - desktop: 10
- avg_daily_minutes_per_user: 14  # source: internal_estimate | quality: medium
- primary_use_cases: [text_discussion, opinion_sharing, news_commentary, real_time_events, social_connection]
- peak_usage_hours_utc: [13:00, 14:00, 15:00, 19:00, 20:00, 21:00]
- user_intent_breakdown:
  - passive_consumption: 65
  - active_engagement: 28
  - content_creation: 7
- demographic_notes: Meta's text platform; Instagram integration. Skews slightly male. Younger than Twitter replacement seekers.

## Creator Performance
- avg_engagement_rate_pct_post: 1.5  # source: meta_creator_insights_2024 | quality: medium
- avg_engagement_rate_pct_reply: 2.2  # source: meta_creator_insights_2024 | quality: medium
- engagement_rate_by_follower_size:
  - nano_1k_5k: 3.8  # source: internal_estimate | quality: low
  - micro_5k_50k: 1.9  # source: internal_estimate | quality: low
  - macro_1m_plus: 0.85  # source: internal_estimate | quality: low
- creator_discoverability_1_5: 2
- algorithm_volatility_1_5: 3
- post_weight_1_5: 4.5
- reply_engagement_weight_1_5: 4
- content_creation_barrier_1_5: 1
- fyp_forgiveness_factor_1_5: 2
- avg_brand_deal_cost_usd: 180  # source: collabstr_2024 (early stage) | quality: low
- notes_creator_growth:
  - bullet_1: Instagram follower base provides initial audience.
  - bullet_2: Discoverability improving but still limited.
  - bullet_3: Trending topics and quoted posts drive engagement.
  - bullet_4: Reply chains and quote posts more engaging than standalone posts.
  - bullet_5: No chronological feed option; algorithm controls distribution.
  - bullet_6: Character limit increasing; now 500 characters standard (expandable to 2k for some).

## Monetization Context
- supported_monetization_methods: [brand_deals, affiliate_links, meta_verified_subscription]
- conversion_to_paid_pct_estimate: 0.8
- avg_revenue_per_paying_user_usd_estimate: 0
- tip_or_gift_usage_notes:
  - bullet_1: NO direct monetization features currently.
  - bullet_2: Meta Verified subscription ($11.99/month) provides verification and features.
  - bullet_3: Creators monetizing via brand deals and affiliate links.
  - bullet_4: No ad revenue share or creator fund yet announced.
- payout_stability_1_5: 2
- threshold_requirements_summary:
  - bullet_1: No monetization features for most creators.
  - bullet_2: Meta Verified for personal account features only.
  - bullet_3: Brand deals require negotiation and disclosure.

## Policy & Risk
- explicit_sexual_content_allowed: false
- nudity_policy_notes: Instagram policies apply; no nudes or explicit content.
- ai_content_disclosure_required: true
- ai_content_policy_version: 2024
- ai_policy_summary:
  - bullet_1: Follows Meta/Instagram AI content policies
  - bullet_2: AI-generated content disclosure encouraged
  - bullet_3: Linked to Instagram for policy enforcement
  - bullet_4: No specific AI labeling tool yet implemented
  - bullet_5: Meta AI features integrated into platform
- ai_enforcement_mechanisms:
  - automated_detection: true
  - ai_label_tool: meta_ai_label
  - reach_penalty_for_unlabeled: inherited_from_instagram
  - content_removal_threshold: medium
- ai_content_monetization: allowed
- ai_policy_enforcement_notes: Instagram community guidelines largely apply. AI content disclosure encouraged.
- enforcement_style_summary:
  - bullet_1: Linked to Instagram account; violations affect both platforms.
  - bullet_2: Meta's automated moderation in place.
  - bullet_3: Appeals through Instagram/Help Center.
- policy_enforcement_volatility_1_5: 3
- brand_safety_score_1_5: 3.5
- age_gate_confidence_1_5: 3.5
- takedown_appeal_success_rate_pct: 35

## Strategic Fit by Track
- mainstream_fit_notes:
  - bullet_1: Good for reaching Instagram-adjacent audience with text content.
  - bullet_2: News, commentary, and opinion content performs well.
  - bullet_3: Trending topics drive real-time engagement.
- hybrid_fit_notes:
  - bullet_1: Excellent cross-platform with Instagram.
  - bullet_2: Text content complements visual Instagram posts.
  - bullet_3: Traffic driver to Instagram for certain content.
- niche_fit_notes:
  - bullet_1: Tech, media, politics, entertainment niches active.
  - bullet_2: Creator communities emerging.
  - bullet_3: Niche discourse communities forming.
- adult_fit_notes:
  - bullet_1: NOT recommended for adult content.
  - bullet_2: Instagram policy alignment means restrictions apply.
  - bullet_3: Adult creators better served by dedicated platforms.

## Content Format Specifics
- post:
  - max_characters: 500 (up to 2,000 with expansion)
  - optimal_length: 100-300 characters
- image_post:
  - max_images: 10
- video:
  - max_duration_minutes: 5
- link_post:
  - link_preview_available
  - engagement_tracking: yes

## Competitive Landscape
- key_competitors: [Twitter_X, Bluesky, Mastodon, Reddit]
- platform_strengths:
  - bullet_1: Instagram integration provides massive potential user base.
  - bullet_2: Meta infrastructure provides stability.
  - bullet_3: Growing creator ecosystem.
  - bullet_4: Clean, ad-free experience initially.
- platform_weaknesses:
  - bullet_1: Limited discovery algorithm.
  - bullet_2: No monetization for creators.
  - bullet_3: Competing directly with Twitter in challenging market.
  - bullet_4: User retention a question (massive initial signups but engagement declining).

## Data Provenance
- sources:
  - meta_company_data_2025
  - threads_announcement_2025
  - sensor_tower_app_data_2025
- last_updated_utc: 2026-03-26T14:00:00Z

## Enrichment Queries
- audience_metrics:
  - query: "Threads Meta US monthly active users 2025"
  - query: "Threads US user demographics age distribution 2025"
  - query: "Threads US daily active users 2025"
  - query: "Threads user engagement retention 2025"
- creator_metrics:
  - query: "Threads creator growth engagement 2025"
  - query: "Threads algorithm discoverability 2025"
  - query: "Threads creator features available 2025"
  - query: "Threads content performance metrics 2025"
- monetization_data:
  - query: "Threads Meta creator monetization 2025"
  - query: "Threads brand partnerships rates 2025"
  - query: "Threads subscription revenue model 2025"
  - query: "X Premium vs Threads subscription comparison 2025"
- policy_enforcement:
  - query: "Threads content policy moderation 2025"
  - query: "Threads community guidelines enforcement 2025"
  - query: "Threads brand safety advertisers 2025"
  - query: "Threads adult content policy 2025"