# AURIONS Builder Checkpoint — Provider Prompt Handling

**Date:** 2026-11-27  
**Branch:** `impl/experience-continuity`  
**Checkpoint HEAD:** `d104aa1bd11495b49ea47a218cbb088f5ac3b3b6`  
**Previous verified security fix:** `255957d7b0fcbd190ee5053deb68cddc5ea8e2c8`

## Bounded work completed

- Provider CLI now accepts prompts from stdin using `--stdin`; stdin is also selected by default when input is piped and no `--prompt` argument is supplied.
- The `--prompt` argument is retained for convenience and is explicitly described as visible in process arguments.
- Input is read with a 65,537-character cap and then checked against the existing 65,536 UTF-8 byte prompt bound before the provider is called.
- Added unit coverage for stdin prompt dispatch and oversized stdin rejection before a network call.
- Updated README usage to demonstrate piping prompts.
- Earlier in this batch, provider redirects were blocked and a real loopback redirect regression test was added.

## Exact evidence

- Provider-runtime unit test step passed on commit `ad683f8065fb9691125e26b2222b2f2d93ae15ac` in model-baseline workflow [45993577645](https://github.com/methaneex-oss/AURIONS/actions/runs/45993577645).
- Full model-baseline workflow was still in progress at checkpoint creation. C++ Core run on `ad683f` was cancelled by subsequent push; a new C++ Core workflow on docs-only commit `d104aa1` was running. Final results must be rechecked.
- No local build/test environment was available in this run; GitHub Actions is the validation source.
- Provider stdin feature has no live provider test; tests mock provider invocation.
- No PR, merge or main-branch modification.

## Review status

Focused source/diff review was performed for the changes. The five required independent review passes were **not completed**. Builder review is not independent acceptance.

## Capability and limitations

The provider runtime's standalone CLI is now safer for entering prompts, but it remains disconnected from the C++ cognitive runtime/router, context/memory pipeline, product UI and model-selection policy. It is not a complete AURIONS conversation capability.

## Next bounded objectives (priority)

1. Recheck exact-head CI, diagnose any failures and rerun after root-cause corrections.
2. Audit the inference boundary and C++ preview flow, including subprocess permissions, timeout, response validation, and quarantine invariants; fix concrete defects.
3. Establish a reproducible integration contract for provider inference with the existing cognition-context interface. Do not rush a broad bridge without end-to-end tests or silently change the owner's model-ownership decision.
4. Prioritize a usable, reproducible entry point and actual target-device validation over more standalone mechanisms.
5. Reconcile experience/belief/strategy persistence with canonical persistence contracts before expanding stores.
6. Run the five separate review passes and maintain an honest release readiness table.

## State discipline

Implemented and committed is not owner-accepted. Tests passing for a small primitive do not mean AURIONS is complete. Resume from this exact branch and inspect live HEAD/CI before touching files.
