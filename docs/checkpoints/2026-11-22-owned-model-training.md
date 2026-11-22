# AURIONS Implementation Checkpoint — Owned Model Training and Candidate Preview

**Checkpoint date:** 2026-11-22  
**Repository:** `methaneex-oss/AURIONS`  
**Branch:** `impl/experience-continuity`  
**Verified code HEAD:** `80cef3b4101a33c460fef7fe125b324b432970c9`
**Checkpoint metadata commit:** `819ce3029ea65751bfe1aae3a34054e72741eeea` (superseded by later code commits)  
**Previous implementation checkpoint:** `docs/checkpoints/2026-11-20-memory-context.md`

## Completed implementation

- Added a deterministic, trainable byte-level BPE tokenizer. Its merge table, special-token mapping, vocabulary size and training-corpus SHA-256 are embedded in the model checkpoint.
- The admitted-data training path learns tokenizer merges from the admitted **training split only**. Validation and held-out splits are not used to build the tokenizer.
- Training now rejects manifests whose train, validation and held-out artifacts or content digests are not distinct.
- Reworked sliding-window construction to use PyTorch tensor views rather than materializing a full overlapping copy of the corpus.
- Candidate training must improve both validation and held-out next-token loss relative to the same randomly initialized baseline before a checkpoint is emitted.
- The candidate inference loader restores the exact BPE tokenizer from checkpoint metadata, verifies tokenizer-to-training-split digest lineage, checks model/tokenizer vocabulary agreement, and rejects candidates that are not quarantined or are marked activation-eligible.
- Corrected prompt construction: generation begins with BOS plus prompt tokens and does not incorrectly append EOS before prediction.
- Admitted-data checkpoints can now be loaded and used for bounded local generation in a quarantined preview path. This is not production model activation.

## Exact-head verification

HEAD `7f36a41e07a30a7d16446dc5b48968b8c054ea3a`:

- Model baseline workflow [45070728896](https://github.com/methaneex-oss/AURIONS/actions/runs/45070728896): **passed**. All 33 Python tests passed, including tokenizer round-trip/versioning, admitted training, held-out improvement, checkpoint restoration, candidate inference, worker-process training and synthetic smoke inference.
- C++ Core workflow [45070728915](https://github.com/methaneex-oss/AURIONS/actions/runs/45070728915): **passed**. CMake configure, C++ build/link and CTest passed (1/1).

The model workflow published artifact `aurions-quarantined-model-checkpoints`:
- Artifact ID: `14773590943`
- Size: 1,428,517 bytes
- SHA-256: `70bc224e9d50e222d57e1306a9378d9ddd0f2a047626f936ba4a0c9e441e89d5`
- Expires: 2026-12-06
- Contains the synthetic baseline and the admitted-data candidate checkpoint produced by the worker integration test.

## Capability boundary

Demonstrated: an AURIONS-owned, randomly initialized small causal Transformer can be trained on a rights-admitted, manifest-bound dataset; the training run learns a BPE tokenizer from the training split, measures validation and held-out token loss, persists a lineage-bound quarantined candidate, reloads it and generates bounded text locally.

Not demonstrated: useful general language competence, natural-language understanding, reasoning, autonomous dataset acquisition, independent outcome verification, candidate evaluation against a meaningful external capability benchmark, candidate activation, C++ cognitive-core inference integration, Termux/Android inference performance, or cloud/mobile continuity. The test corpora are controlled fixtures, not a production language corpus. Do not describe this as a capable conversational brain.

## Follow-on implementation — JSONL candidate inference worker

Added `ml/python/aurions_ml/inference_worker.py`, a separate-process JSONL worker that accepts one versioned `candidate_inference_preview` request per line and reads only SHA-256-addressed candidate artifacts from its configured artifact store.

- Strict protocol version and exact-field validation; rejects duplicate JSON keys, unknown fields, invalid UUIDs, unsupported job types, malformed artifact URIs, invalid Unicode, invalid token limits and oversized messages.
- Verifies artifact bytes through the content-addressed store and loads only quarantined, non-activatable candidates.
- Returns one bounded JSON response per request; stdout is protocol-only and diagnostics go to stderr.
- Has no database, governance, credential, activation or live-cognition write interface.
- Added byte-based candidate loading/generation APIs so the worker does not need arbitrary filesystem paths.
- Subprocess tests cover successful preview, unknown/duplicate fields, an activation-eligible forged checkpoint and oversized input.

This worker is independently process-tested, but it is **not yet supervised or invoked by the C++ cognitive core**. Parent-side process lifecycle, resource/time limits, job-scoped filesystem restrictions and C++ response validation remain required before it is a production inference path.

## Next implementation objective

Build the model-independent C++ inference boundary and a bounded separate-process worker adapter that can consume an explicitly selected, quarantined candidate for evaluation only. Use a versioned JSONL contract, strict request/response validation, time/resource bounds, job-scoped artifact access and no worker authority over live cognition or activation. Then connect the returned model output to a real cognition-context consumer and evaluate it on held-out tasks. Do not wire a quarantined candidate into the active runtime.

## Resume instructions

1. Verify the live branch head before editing; preserve this branch and do not modify `main`.
2. Inspect current Python model/tokenizer/training/inference code and the C++ core before changing interfaces.
3. Continue implementation; do not restart the project or replace existing architecture.
4. Keep claims separated into implemented, CI-tested, target-device-tested, independently verified and accepted.
5. No model candidate may be activated without the separate evaluation, governance and owner-approval lifecycle.
