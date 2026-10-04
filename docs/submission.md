# Ready contribution

Category: Builder -> Intelligent Contracts

Title: ScopeLatch: Consensus-derived FIFO resource semaphore

## Notes / Description

ScopeLatch is a standalone GenLayer semaphore for cooperating clients sharing test infrastructure. A deployment fixes resource rules and admitted wallets. Clients submit commit-pinned execution plans and SHA-256 hashes; leader and validators independently fetch full texts and derive USED, UNUSED or UNCERTAIN for every resource. Exact decision agreement and source-anchor checks determine the reservation footprint. The FIFO scheduler grants all required locks together or none; a blocked head prevents overtaking. Creator-only cancellation and release automatically admit eligible waiters, and released resources can be reused. Uncertain plans get REVIEW without locks; read-only plans get NO_LOCKS. StudioNet CLI proofs cover atomic grants, conflicts, FIFO blocking, cancellation, uncertainty and reuse. The repo includes a pinned GenVM contract, 18 direct tests and sanitized receipts. Synthetic plans demonstrate coordination, not actual execution; clients must honor the locks.

## Evidence

- Contract: https://github.com/ehsanisildur-ux/scope-latch/blob/main/contracts/scope_latch.py
- Repository: https://github.com/ehsanisildur-ux/scope-latch
- Onchain proofs: https://github.com/ehsanisildur-ux/scope-latch/blob/main/proofs/README.md

StudioNet contract: `0xce35C4aD8e0B08e309863c35a3551478f3057fA8`.

Deployment: https://explorer-studio.genlayer.com/tx/0x422fbeee26ac8706effb8324d6853d057dc57e3543a2463a28b185dcc6bb3811

All 11 receipts finalized with MAJORITY_AGREE and successful execution; source commitments and every recorded lock state passed verification. Receipts retain dissenting votes.
