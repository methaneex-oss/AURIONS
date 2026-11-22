# AURIONS Implementation Checkpoint — Owned Model Training and Candidate Preview

**Checkpoint date:** 2026-11-22  
**Repository:** `methaneex-oss/AURIONS`  
**Branch:** `impl/experience-continuity`  
**Verified code HEAD:** `067a977511b54c6762cbd5993acddc8231dafdb0`
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

## Verified model training and tokenizer

- Model baseline workflow [45071010301](https://github.com/methaneex-oss/AURIONS/actions/runs/45071010301) on Python code commit `80cef3b4101a33c460fef7fe125b324b432970c9`: **passed**, 37/37 Python tests. This verifies BPE training, train-split digest binding, held-out improvement, admitted-candidate reload/generation and the JSONL worker's request-validation and rejection paths.
- C++ Core workflow [45071010285](https://github.com/methaneex-oss/AURIONS/actions/runs/45071010285) on code commit `80cef3b4101a33c460fef7fe125b324b432970c9`: **passed**, CMake configure/build and CTest (1/1).
- Artifact `aurions-quarantined-model-checkpoints`: ID `14772832963`, size 1,428,509 bytes, SHA-256 `6578ac6b0ebbe89fddab11d5fe976619111fbb4a74a524d3f33032adce7c5136`, expires 2026-12-06. It contains the synthetic baseline and admitted-data candidate checkpoint from the worker integration test.

The later C++ process-adapter verification is recorded separately below; its exact code HEAD is `067a977511b54c6762cbd5993acddc8231dafdb0`.

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

## Follow-on implementation — C++ inference process adapter

Added a model-independent C++ `InferenceAdapter` interface and a POSIX `PythonProcessInferenceAdapter`, exposed through:

```text
aurions model preview <python-executable> <artifact-store> <artifact-uri> <prompt> [max-new-tokens 1-128]
```

The adapter launches `aurions_ml.inference_worker` without a shell, sends a versioned JSONL request, closes the request stream, reads a bounded response, validates protocol/job identity/candidate digest/quarantine state/token limit, and returns only preview text. It enforces a 15-second default wall-clock deadline, a 64 KiB response cap, and a restricted environment allowlist that excludes ambient API keys and credentials. The Python worker itself is constrained to one CPU thread.

The C++ integration test uses a fake worker and verifies Unicode/quote/backslash/newline round-tripping, successful candidate preview, worker rejection propagation, secret-environment non-disclosure and oversized-response termination.

- C++ Core workflow [45071592983](https://github.com/methaneex-oss/AURIONS/actions/runs/45071592983) on code HEAD `067a977511b54c6762cbd5993acddc8231dafdb0`: **passed**. Configure/build passed; CTest passed (2/2), including the new process-preview test.
- Python model workflow [45071427010](https://github.com/methaneex-oss/AURIONS/actions/runs/45071427010) on Python code commit `9b0d198af2cd6a9ee969ea6d0920c24e4bd8bb80`: **passed**, 37/37 tests. No Python model/worker code changed after that tested commit in this C++ adapter milestone.

**Remaining boundary:** this is a subprocess adapter, not an OS sandbox. The worker still runs under the same user identity and filesystem permissions; the parent must provide a job-scoped artifact-store directory and deployment-level isolation before treating it as a hostile-code sandbox. CPU thread fan-out, wall-clock time and response bytes are bounded; a hard memory limit is not yet enforced. The C++ cognitive core does not yet build prompts from memory/beliefs or use model output to update a decision.

## Next implementation objective

Connect the preview adapter to a real, bounded cognition-context consumer that uses retrieved experiences and beliefs as evidence, preserves provenance/uncertainty, and measures output against held-out tasks. Keep candidate inference quarantined; do not allow generated text to revise beliefs or execute actions until independent evaluation and governance exist. and a bounded separate-process worker adapter that can consume an explicitly selected, quarantined candidate for evaluation only. Use a versioned JSONL contract, strict request/response validation, time/resource bounds, job-scoped artifact access and no worker authority over live cognition or activation. Then connect the returned model output to a real cognition-context consumer and evaluate it on held-out tasks. Do not wire a quarantined candidate into the active runtime.

## Resume instructions

1. Verify the live branch head before editing; preserve this branch and do not modify `main`.
2. Inspect current Python model/tokenizer/training/inference code and the C++ core before changing interfaces.
3. Continue implementation; do not restart the project or replace existing architecture.
4. Keep claims separated into implemented, CI-tested, target-device-tested, independently verified and accepted.
5. No model candidate may be activated without the separate evaluation, governance and owner-approval lifecycle.
