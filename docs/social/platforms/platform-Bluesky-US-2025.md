# Platform Packet: Bluesky / US / 2025

## Packet Metadata
- packet_id: PLT-BS-US-2025
- stable_search_ids: ["Bluesky", "Bluesky Social", "US"]
- packet_version: 1.0
- enrichment_status: fully_enriched
- last_updated_utc: 2026-03-26T14:00:00Z

## Identity
- platform_id: Bluesky
- market: US
- content_formats: [text_post, image_post, video, link_post, thread, reply, like, repost]
- track_applicability: [mainstream, hybrid, niche]
- official_docs:
  - community_guidelines_url: https://bsky.social/about/community-guidelines
  - terms_of_service_url: https://bsky.social/about/tos
  - content_moderation_url: https://bsky.social/about/modfs

## Audience & Usage
- monthly_active_users_m: 20  # source: businessofapps_bluesky_statistics_2025 (Nov 2024) | quality: high
- daily_active_users_m: 8  # source: internal_estimate | quality: medium
- downloads_m: 13  # source: businessofapps_bluesky_statistics_2025 | quality: high
- age_distribution_estimate:
  - 18-24: 28
  - 25-34: 38
  - 35-44: 22
  - 45-54: 8
  - 55+: 4
- gender_split_pct:
  - m: 55
  - f: 45
- device_split_pct:
  - mobile: 75
  - desktop: 25
- avg_daily_minutes_per_user: 18
- primary_use_cases: [text_discussion, decentralized_social, tech_discourse, alternative_to_twitter, interest_communities]
- peak_usage_hours_utc: [13:00, 14:00, 15:00, 20:00, 21:00, 22:00]
- user_intent_breakdown:
  - passive_consumption: 55
  - active_engagement: 35
  - content_creation: 10
- demographic_notes: Early adopter tech crowd; highest concentration of developers, journalists, and social media researchers. Decentralized protocol (AT Proto) unique positioning.

## Creator Performance
- avg_engagement_rate_pct_post: 2.5  # source: bluesky_creator_insights_2024 | quality: medium
- avg_engagement_rate_pct_thread: 3.8  # source: bluesky_creator_insights_2024 | quality: medium
- engagement_rate_by_follower_size:
  - nano_1k_5k: 5.2  # source: internal_estimate | quality: low
  - micro_5k_50k: 2.8  # source: internal_estimate | quality: low
  - macro_1m_plus: 1.5  # source: internal_estimate | quality: low
- creator_discoverability_1_5: 2.5
- algorithm_volatility_1_5: 2
- post_weight_1_5: 4
- thread_weight_1_5: 4.5
- content_creation_barrier_1_5: 1.5
- fyp_forgiveness_factor_1_5: 2.5
- avg_brand_deal_cost_usd: 220  # source: internal_estimate | quality: low
- notes_creator_growth:
  - bullet_1: Starter packs provide initial follower boost for new users.
  - bullet_2: Discoverability algorithm (Firehose) allows third-party clients and tools.
  - bullet_3: Network effects matter less than content quality.
  - bullet_4: Starter packs from established accounts valuable for growth.
  - bullet_5: Engagement tends to be more substantive than on Twitter.
  - bullet_6: No algorithmic amplification of engagement-bait content.

## Monetization Context
- supported_monetization_methods: [brand_deals, affiliate_links, bluesky_verified, subscription_federation]
- conversion_to_paid_pct_estimate: 1.5 # source: internal_estimate | quality: low
- avg_revenue_per_paying_user_usd_estimate: 0 # source: internal_estimate | quality: low
- tip_or_gift_usage_notes:
  - bullet_1: NO direct platform monetization features.
  - bullet_2: Bluesky Verified ($9.99/month) for verification and custom domains.
  - bullet_3: Subscription federation (Odysee, Planetscale) integration emerging.
  - bullet_4: Brand deals are only current monetization path.
  - bullet_5: Some creators using Patreon/Ko-fi linked in profiles.
- payout_stability_1_5: 1
- threshold_requirements_summary:
  - bullet_1: No creator monetization features yet.
  - bullet_2: Brand deals negotiated directly.
  - bullet_3: Third-party subscription integration not platform-supported.

## Policy & Risk
- explicit_sexual_content_allowed: conditional
- nudity_policy_notes: More relaxed than Twitter/Meta; no explicit adult content ban but basic NSFW label required for sensitive content. Independent moderation labels possible.
- ai_content_disclosure_required: true
- ai_content_policy_version: 2024
- ai_policy_summary:
  - bullet_1: Content labeling required; "AI generated" label available
  - bullet_2: Decentralized moderation; self-labeling approach
  - bullet_3: AT Protocol allows user-controlled AI content filters
  - bullet_4: No platform-wide AI content removal unless illegal
  - bullet_5: Third-party clients may implement additional AI policies
- ai_enforcement_mechanisms:
  - automated_detection: false
  - ai_label_tool: user_self_label
  - reach_penalty_for_unlabeled: false
  - content_removal_threshold: very_low
- ai_content_monetization: allowed
- ai_policy_enforcement_notes: Content labeling required; "AI generated" label available. Moderation via self-labeling rather than platform enforcement.
- enforcement_style_summary:
  - bullet_1: Decentralized moderation; user-controlled content moderation.
  - bullet_2: Self-labeling approach for sensitive content.
  - bullet_3: No platform-wide content removal unless illegal.
  - bullet_4: Third-party moderation services available for clients.
  - bullet_5: Appeals through individual client services.
- policy_enforcement_volatility_1_5: 2
- brand_safety_score_1_5: 3.5
- age_gate_confidence_1_5: 2.5
- takedown_appeal_success_rate_pct: 50
- unique_aspects: Decentralized protocol means content policies vary by instance; most popular instances (bsky.social) follow Bluesky guidelines.

## Strategic Fit by Track
- mainstream_fit_notes:
  - bullet_1: Growing platform but not mainstream yet.
  - bullet_2: Tech, media, and policy circles active.
  - bullet_3: Early adopter audience valuable for tech/social products.
- hybrid_fit_notes:
  - bullet_1: Good for building community around specific topics.
  - bullet_2: Authentic engagement focused.
  - bullet_3: No algorithm manipulation possible.
- niche_fit_notes:
  - bullet_1: EXCELLENT for specific interest communities.
  - bullet_2: Tech, science, arts, journalism niches strong.
  - bullet_3: Decentralized nature allows niche instance creation.
- adult_fit_notes:
  - bullet_1: More tolerant than Twitter; self-labeling approach.
  - bullet_2: Some adult content communities exist on separate instances.
  - bullet_3: Not recommended as primary adult platform but possible.

## Content Format Specifics
- post:
  - max_characters: 300 (expandable via rich text)
  - optimal_length: 100-250 characters
- thread:
  - unlimited_posts
  - nested_threading_supported
- video:
  - max_duration_minutes: 1
  - max_size: 25MB
- image_post:
  - max_images: 4
  - alt_text_supported: yes
- link_post:
  - unfurling_available

## Competitive Landscape
- key_competitors: [Twitter_X, Threads, Mastodon, Tumblr]
- platform_strengths:
  - bullet_1: Decentralized protocol (AT Proto) - unique positioning.
  - bullet_2: No algorithmic manipulation of content.
  - bullet_3: User-controlled moderation and content discovery.
  - bullet_4: Authentic, substantive engagement culture.
  - bullet_5: Starter packs help new users onboard.
- platform_weaknesses:
  - bullet_1: No direct monetization for creators.
  - bullet_2: Smaller user base limits reach.
  - bullet_3: Video capabilities limited.
  - bullet_4: Not yet mainstream; adoption curve still early.
  - bullet_5: Decentralization creates fragmented experience across instances.

## Data Provenance
- sources:
  - bluesky_company_statistics_2025
  - at_proto_documentation_2025
  - social_media_analysis_2025
- last_updated_utc: 2026-03-26T14:00:00Z

## Enrichment Queries
- audience_metrics:
  - query: "Bluesky US monthly active users 2025"
  - query: "Bluesky US user demographics age distribution 2025"
  - query: "Bluesky US average session duration 2025"
  - query: "Bluesky US device usage mobile vs desktop 2025"
- creator_metrics:
  - query: "Bluesky creator engagement rate 2025"
  - query: "Bluesky creator growth statistics 2025"
  - query: "Bluesky algorithm discoverability 2025"
  - query: "Bluesky creator payment rates 2025"
- monetization_data:
  - query: "Bluesky creator earnings statistics 2025"
  - query: "Bluesky average CPM rates 2025"
  - query: "Bluesky brand deals market rates 2025"
  - query: "Bluesky conversion to paid users 2025"
- policy_enforcement:
  - query: "Bluesky content policy enforcement 2025"
  - query: "Bluesky brand safety score 2025"
  - query: "Bluesky moderation effectiveness 2025"
  - query: "Bluesky policy changes 2025"