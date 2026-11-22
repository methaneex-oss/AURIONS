# AURIONS Implementation Checkpoint — Owned Model Training and Cognitive Preview

**Checkpoint date:** 2026-11-22  
**Repository:** `methaneex-oss/AURIONS`  
**Branch:** `impl/experience-continuity`  
**Verified implementation HEAD:** `195363a5ad52855dc69c36f5c6fa990711157003`  
**Previous implementation checkpoint:** `docs/checkpoints/2026-11-20-memory-context.md`

## Implemented and verified

### Owned model training

- Added a deterministic, trainable byte-level BPE tokenizer. The checkpoint carries the exact merge table, special-token mapping, vocabulary size and training-corpus SHA-256.
- BPE merges are learned only from the admitted training split. Validation and held-out splits do not influence tokenizer fitting.
- Training split artifacts and digests must be distinct for train, validation and held-out data.
- BPE fitting has a training-only minimum-token constraint. It cannot merge the training split below one full model context window.
- The owned causal Transformer now uses a 256-token context for admitted-data candidates.
- Sliding-window construction uses tensor views rather than materializing a full overlapping copy of the corpus.
- A candidate is retained only when both validation loss and held-out loss improve against its own random-initialization baseline.
- Candidate loading verifies dataset lineage, tokenizer-to-training-split digest binding, model/tokenizer vocabulary agreement, finite training metrics and quarantine status.
- Inference rejects a prompt that exceeds the candidate's context window; it no longer silently drops older evidence through implicit truncation.

### Candidate inference worker and C++ process adapter

- `ml/python/aurions_ml/inference_worker.py` exposes a versioned JSONL `candidate_inference_preview` protocol.
- The worker validates exact request fields, protocol version, UUID, artifact URI, prompt size and token limit; duplicate keys, unknown fields and malformed inputs are rejected.
- It reads the selected SHA-256-addressed artifact from its configured artifact store and loads only a quarantined, non-activatable candidate.
- The C++ `InferenceAdapter` interface and POSIX `PythonProcessInferenceAdapter` launch the worker without a shell, pass a restricted environment, enforce a 15-second default deadline and a 64 KiB response cap, and validate job identity, artifact digest, protocol status and quarantine state.
- This is a bounded subprocess adapter, not an OS sandbox. The worker still runs under the same OS user identity and filesystem permissions. Deployment must provide a job-scoped artifact-store directory and stronger isolation before treating the worker as hostile-code containment. A hard memory limit is not yet enforced.

### C++ cognition-to-model preview

The C++ CLI now exposes:

```text
aurions cognition preview <database> <python-executable> <artifact-store> <artifact-uri> <query> [max-items] [max-new-tokens]
```

The command retrieves relevant experience records and beliefs from the existing stores, builds a compact evidence-only prompt, and invokes the selected quarantined candidate through the process adapter.

- Only sensitivity-level-zero observations are included.
- Beliefs without evidence are omitted.
- A belief is omitted if any attached evidence is not public.
- Provenance, belief domain, confidence, epistemic status, stance and reliability are retained in the prompt.
- Included and omitted evidence counts are returned with the generated preview.
- Prompt framing uses actual newline separators and is checked against the candidate's real tokenizer/context length in the end-to-end test.
- The preview cannot revise beliefs, write memories, activate the model or execute actions.

## CI evidence at the verified implementation HEAD

- **AURIONS owned model baseline:** [workflow 45073271992](https://github.com/methaneex-oss/AURIONS/actions/runs/45073271992), commit `195363a5ad52855dc69c36f5c6fa990711157003`: **passed**. The run completed the Python model/admission/inference suite, C++ configure/build/CTest, the real C++ → retrieved cognition evidence → admitted candidate preview, synthetic checkpoint production, local checkpoint inference and artifact publication.
- **C++ Core:** [workflow 45073272062](https://github.com/methaneex-oss/AURIONS/actions/runs/45073272062), same commit: **passed**. Configure, build and CTest passed.
- **Published workflow artifact:** `aurions-quarantined-model-checkpoints`, artifact ID `14774151917`, size 1,529,987 bytes, SHA-256 `0a473c8391ec3cb7386fbd393b39a171961c9a8696462acf977ebd57ba08d5e9`. It contains the synthetic baseline and admitted-data candidate checkpoints. Expires 2026-12-06.

## What this demonstrates—and what it does not

**Demonstrated:** an AURIONS-owned, randomly initialized causal Transformer can be trained from a rights-admitted, manifest-bound dataset; learn and persist its own BPE tokenizer; improve next-token loss on validation and held-out splits; reload the resulting quarantined candidate; and generate a bounded preview from evidence assembled by the C++ experience and belief stores. The full cross-language path is exercised in CI.

**Not demonstrated:** useful general language competence, robust natural-language understanding, general reasoning, independent outcome verification, autonomous dataset acquisition, meaningful task-level accuracy, production-scale training, candidate activation, belief revision from model output, action execution, Termux/Android performance, or multi-device/cloud continuity. The training corpora used in CI are controlled synthetic fixtures, not a production language corpus. A loss improvement on those fixtures is not proof of intelligence or useful conversational ability.

The model output is currently an evidence-conditioned **preview only**. It is not trusted as a fact, cannot update beliefs, and cannot authorize actions. Candidate activation remains blocked pending a separate evaluation and governance lifecycle with owner approval.

## Next implementation objective

Build a task-level candidate evaluation loop that uses held-out, rights-admitted examples and reports measurable behaviour beyond next-token loss. The evaluator must compare candidate output with a baseline, preserve dataset and prompt lineage, reject unsupported or unsafe outputs, and produce a reproducible promotion decision. Keep candidates quarantined until evaluation and owner-approval gates are genuinely satisfied. Do not treat a passing preview integration as proof of general understanding.

## Resume instructions

1. Verify the live branch HEAD before editing; preserve `impl/experience-continuity` and do not modify `main`.
2. Continue implementation from this checkpoint; do not restart or redesign the existing architecture.
3. Keep claims separated into implemented, CI-tested, target-device-tested, independently verified and accepted.
4. Treat a candidate as quarantined until separate evaluation and owner approval authorize promotion.
5. Prioritize observable learning and behaviour over adding mechanisms or documentation volume.
