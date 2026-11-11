# Planning documentation

This directory contains the planning baseline imported from the canonical Notion project control center.

## Canonical source

- [Initial engineering specification](INITIAL-ENGINEERING-SPECIFICATION.md) — full planning record, including owner decisions, architecture, proposed database DDL, event/worker contracts, artifact lifecycle, governance, security, testing, roadmap and final planning gates.
- [Notion project control center](https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204) — original planning source and decision history.

## Status discipline

The specification distinguishes owner decisions, accepted baselines, proposals, unresolved items, validated evidence and implementation status. A design being documented is not proof that it has been implemented or tested.

At import time:
- Planning design was consolidated.
- Exact dependency/license inventory, target-device measurements, execution of the complete DDL, migration/fault testing, and implementation-specific threat-model review remained evidence gates.
- No implementation code or database migrations had been performed.
- Implementation work begins with WP-00 and WP-01; do not reopen settled owner decisions without concrete contradictory evidence or material risk.

## Editorial note

The source document accumulated several planning additions over time and contains repeated section numbers (including repeated 32 and 33 headings), plus historical statements that reflect earlier project status. The imported specification preserves that history rather than silently rewriting it. Future edits should resolve navigation and numbering while retaining decision provenance and the change log.
