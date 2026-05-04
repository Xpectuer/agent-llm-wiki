# Schema Note

> Explains the organizational decisions behind this wiki.

## Why This Structure Works

This wiki adopts a three-layer architecture: **raw/** for immutable source materials, **wiki/** for LLM-authored knowledge pages, and **reports/** for operational outputs. This separation ensures that original evidence is never silently overwritten, while the knowledge layer can evolve freely through ingest, query, and lint cycles.

The target audience for this wiki is someone who needs to quickly find reliable answers grounded in original sources — whether that is a future version of myself, a new team member, or a colleague looking for specific information. Every wiki page traces back to at least one raw source, and every answer cites the wiki pages it drew from.

## Key Structural Decisions

**1. Wikilink-based cross-referencing.** Using `[[page-name]]` syntax creates a dense web of internal links. This makes it easy to navigate between related concepts without relying on a rigid hierarchy. The lint script enforces a minimum cross-reference density, preventing pages from becoming isolated.

**2. Append-only log.** The `wiki/log.md` file records every operation in chronological order. This creates an audit trail that shows how the wiki evolved, which materials were ingested when, and what issues were found during lint passes. It also helps future readers understand the wiki's growth pattern.

**3. Three-operation workflow.** Separating ingest (adding knowledge), query (retrieving knowledge), and lint (maintaining structure) into distinct operations keeps each step focused. Ingest is about fidelity to sources. Query is about synthesizing answers with citations. Lint is about structural health — finding orphans, contradictions, and gaps.

## Adaptation for Different Users

If the wiki needed to serve a different audience (e.g., a non-technical manager instead of an engineer), the main change would be in page categorization and vocabulary. The index would use domain-specific categories instead of generic ones (concepts/entities/sources/synthesis), and wiki pages would prioritize plain-language summaries over technical detail. The three-layer architecture and three-operation workflow would remain the same, as they are format-agnostic.
