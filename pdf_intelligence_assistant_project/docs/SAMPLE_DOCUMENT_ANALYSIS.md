# Sample Document Analysis — spotify_web_app_architecture.pdf

## 1. Source identity

- File: `spotify_web_app_architecture.pdf`
- Pages: 6
- Title in source: **Spotify-like Web App – Full Architecture & Feature List**
- Purpose in this project: Initial sample for PDF extraction, summaries, entity/relation extraction, hybrid retrieval, citations and negative-question tests.

## 2. What the PDF says

The PDF is a high-level architecture and feature checklist for a Spotify-like web application designed to scale to 100,000+ daily users. It is not evidence of Spotify's actual internal architecture.

It covers:

- **Page 1:** Frontend and backend technology overview; storage and infrastructure; API Gateway/BFF, Auth, User Profile and Catalog services.
- **Page 2:** Search & Discovery, Library & Playlist, Playback & Session, Streaming/Media Delivery, Recommendation, Social, Subscription/Billing, Ads, Creator Portal, Media Processor and Analytics services.
- **Page 3:** Notification and Admin services; storage layout for PostgreSQL, Redis, Elasticsearch/OpenSearch, ClickHouse, object storage/CDN and message queues; frontend route structure.
- **Page 4:** Additional frontend routes and global UI components; user authentication, player, library/playlist and catalog feature checklists.
- **Page 5:** Search, recommendations, social, monetization, ads, creator portal, moderation, analytics and security requirements.
- **Page 6:** Concludes that the document summarizes a Spotify-like architecture and feature checklist for a large-scale web application.

## 3. Source-supported examples for extraction

### Technologies and infrastructure

- Frontend lists Next.js, React, TypeScript, Tailwind CSS, React Query, Zustand/Recoil/Jotai, HLS.js, HTML5 Audio/Web Audio API, OAuth2/OIDC and PWA capabilities (page 1).
- Backend lists Node.js, TypeScript, NestJS, REST, gRPC or message bus, and API Gateway technologies such as Nginx/Envoy/Kong (page 1).
- Data/storage includes PostgreSQL, Redis, Elasticsearch/OpenSearch, ClickHouse, S3-compatible object storage and CDN (pages 1 and 3).
- Infrastructure includes Docker, Kubernetes, Vault/Secrets Manager, GitHub Actions/GitLab CI, Prometheus, Grafana and OpenTelemetry (page 1).

### Services

The document enumerates services including API Gateway/BFF, Auth & Identity, User Profile, Catalog, Search & Discovery Index, Library & Playlist, Playback & Session, Streaming/Media Delivery, Recommendation & Personalization, Social & Activity, Subscription & Billing, Ads, Content Ingestion & Creator Portal, Media Processor, Analytics & Events, Notification and Admin & Backoffice (pages 1–3).

### Explicitly described relations suitable for graph tests

- The Search & Discovery Index Service is powered by Elasticsearch/OpenSearch (page 2).
- The Playback & Session Service stores playback state and manages sessions/devices; it provides a WebSocket channel for real-time player updates (page 2).
- The Media Processor transcodes uploads using FFmpeg and writes processed files to object storage (page 2).
- Analytics & Events stores events in ClickHouse/data warehouse and feeds the Recommendation Service with listening data (pages 2–3).
- PostgreSQL is assigned user/profile/subscription/playlist and some catalog metadata; Redis is assigned session/cache and playback-state uses; Elasticsearch/OpenSearch is assigned full-text search indexes; ClickHouse is assigned analytics events (page 3).

Do not create relationships merely because two entities appear in the same list or section. Use an exact supporting sentence or passage.

## 4. Suggested golden questions

| ID | Question | Expected handling |
|---|---|---|
| Q-001 | Which frontend technologies are listed? | Answer with technologies explicitly listed on page 1 and cite page 1. |
| Q-002 | What does the Playback & Session Service manage? | State playback state, sessions and active devices; mention WebSocket updates; cite page 2. |
| Q-003 | Which search technology powers the Search & Discovery Index Service? | Elasticsearch/OpenSearch; cite page 2. |
| Q-004 | What does the Media Processor do? | Describes transcoding, multiple bitrates/HLS manifests, waveforms/loudness/audio analysis and writing outputs to object storage; cite page 2. |
| Q-005 | How is listening data used by recommendations? | Analytics & Events feeds Recommendation Service with listening data; cite pages 2–3. |
| Q-006 | List the data storage technologies and their stated roles. | Summarize PostgreSQL, Redis, Elasticsearch/OpenSearch, ClickHouse and object storage/CDN based on page 3. |
| Q-007 | What are the global UI components? | Persistent bottom player, left navigation, top bar and queue/Now Playing side panel; cite page 4. |
| Q-008 | What security measures are listed? | HTTPS, secure cookies, HSTS, input validation, rate limiting, RBAC, data export/deletion and audit logging; cite page 5. |
| Q-009 | What is the specified daily active user capacity? | The document describes a design capable of serving 100,000+ daily users; cite page 6. Do not present this as a tested benchmark. |
| Q-010 | What is the CEO's salary? | Abstain: this PDF does not provide the information. |
| Q-011 | Is this confirmed to be Spotify's real production architecture? | Abstain/qualify: the document describes a Spotify-like web app architecture; it does not establish that this is Spotify's actual internal design. |
| Q-012 | Which service manages subscription renewals and invoices? | Subscription & Billing Service; cite page 2. |

## 5. Graph extraction example

A supported graph assertion can be represented as:

- Entity: `Analytics & Events Service` (SERVICE)
- Relation: `FEEDS`
- Entity: `Recommendation Service` (SERVICE)
- Evidence: source passage stating that Analytics & Events feeds Recommendation Service with listening data
- Provenance: page 3 and supporting chunk ID generated during ingestion

`FEEDS` may be added to the controlled relationship schema only if approved; otherwise map to a carefully defined `PROVIDES` or `SUPPORTS` relation without changing the original meaning.

## 6. Extraction caveats

- The PDF is an architecture feature list and contains many bullets; preserve bullet grouping and section context.
- Some stack options are alternatives (for example, Zustand/Recoil/Jotai and Kafka/NATS/RabbitMQ). Do not convert alternatives into claims that all are simultaneously deployed.
- Many items are suggested technologies or optional features. Preserve modal language such as “e.g.”, “optionally”, “could” and “if needed”.
- The 100,000+ daily-user statement is a design-capability description in the document, not an independently verified load-test result.
