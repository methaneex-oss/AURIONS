# Planning review and repository import notes

**Review date:** 2026-11-11  
**Repository:** [methaneex-oss/AURIONS](https://github.com/methaneex-oss/AURIONS)  
**Source:** [AURION — Project Control Center & Initial Engineering Specification](https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204)

## Import scope

The complete content of the canonical Notion planning page was retrieved and imported into [INITIAL-ENGINEERING-SPECIFICATION.md](INITIAL-ENGINEERING-SPECIFICATION.md). The imported body was approximately 117,393 characters before the repository header and provenance note. The import includes the owner-decision register, architecture, cognitive cycle, persistence model, proposed SQL DDL for all three SQLite databases, event and worker contracts, artifact storage, authorization, encryption, recovery, retention/deletion, testing, roadmap, work packages, risk register and final planning gates.

A workspace search for `AURION` returned this canonical planning page as the only matching page. No second AURION planning page was found in that search.

## Review findings

1. **Decision precedence:** The source grew through successive additions. Earlier sections contain provisional designs and earlier status snapshots. Where those conflict with later final engineering resolutions (especially the final sections on cross-store consistency, artifacts, encryption, authentication, risk classes, worker boundaries and security defaults), the later final resolutions are the current planning baseline. Preserve the earlier text as history; do not treat it as equally current.
2. **Repeated and missing section numbers:** The source repeats section numbers 32 and 33 and jumps from section 23 to 26. This appears to be accumulated document history. No missing content has been invented and the source has not been renumbered during import.
3. **Naming:** The repository/system identifier is **AURIONS**, with the final S denoting **System**, per the owner's clarification. The historical planning document uses **AURION** as its working name and expansion. The import preserves that historical wording and records the repository naming clarification at the top.
4. **DDL status:** The SQL is a proposed baseline, not a validated schema. It has not been executed against the target SQLite build. Table constraints, indexes, migrations, transaction boundaries and crash/fault behaviour remain to be tested.
5. **Device evidence:** The Termux, Android, memory, compiler, llama.cpp and model measurements are historical observations. Basic inference succeeded, but sustained performance, thermal behaviour, battery use, memory pressure and background execution have not been established. Re-measure before making runtime commitments.
6. **Dependency and security evidence:** Exact dependency versions/licences and implementation-specific threat-model/residual-risk review remain open. The design requirements are not evidence that a secure implementation exists.
7. **Current repository state:** The repository contains planning documentation only. No C++ implementation, Python worker, database migration, device configuration or runtime data has been added by this import.

## Current planning-to-engineering state

- [x] Canonical planning record imported.
- [x] Repository entry point and planning index created.
- [x] Import scope and known document inconsistencies recorded.
- [ ] WP-00: establish and verify the actual C++ build/test baseline.
- [ ] WP-01: implement and test shared contracts and message validation.
- [ ] Execute and validate the proposed SQLite schema and migrations.
- [ ] Verify dependency versions/licences and target-device capabilities.
- [ ] Complete implementation-specific threat-model and residual-risk review.

## Maintenance rule

The Notion control center remains the historical planning authority. GitHub is the implementation source of truth. Material owner decisions and accepted engineering changes must be reflected in both places; routine implementation evidence, code, tests and CI results belong in this repository. Never mark a gate complete without recorded evidence.
