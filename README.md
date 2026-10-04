# ScopeLatch

A standalone GenLayer FIFO semaphore for shared software test infrastructure. Consensus derives an execution plan's exact resource footprint; the deterministic scheduler admits all required locks atomically or none. This is concurrency coordination, not a ranking, auction, certificate or graph-proposal protocol.

The deployment freezes 1–4 resource rules and 1–5 admitted clients. Clients request reservations using commit-pinned public plans and SHA-256. Leader and validators independently fetch each full plan and derive USED/UNUSED/UNCERTAIN for every resource, including implicit use and negated actions. Exact decision equality plus a full-source anchor check gates admission. Uncertainty records REVIEW without entering the queue; an established empty footprint records NO_LOCKS.

Requests with known nonempty footprints join a bounded FIFO queue. The oldest blocked request prevents later requests from overtaking, even when they need unrelated resources. The scheduler never acquires a partial footprint. A creator can cancel a waiting request or release an active request; both operations automatically grant eligible queued requests. Released resources can be reserved again. No administrator can rewrite classifications or steal a client's locks.

## Interface

- Constructor: JSON resource rules `{id,rule}` and admitted wallet addresses.
- `request(url,sha256)`: fetch, classify, validate and schedule a plan.
- `cancel(index)`: creator only; WAITING requests.
- `release(index)`: creator only; ACTIVE requests.
- `get_state()`: complete source-bound requests, statuses, queue cursor and resource holders.

```sh
pip install -r requirements.txt
genvm-lint download --version v0.2.16
genvm-lint check contracts/scope_latch.py --json
pytest tests/direct/ -q
```

[Contract](contracts/scope_latch.py) · [Architecture](docs/architecture.md) · [Live proofs](proofs/README.md)

## Practical limits

This is a cooperating-client primitive: software must consult and honor its onchain locks. It does not enforce changes to external databases or prove plan execution. Fixed admitted clients can still block progress by retaining locks or by leaving a blocked head queued. There is deliberately no forced expiry that would allow simultaneous critical sections. Catalogue, membership and plans cannot be edited; 24 requests bound lifetime storage. Start a new pool after exhaustion. Public source hashes commit to bytes, not an author's identity. Synthetic plans demonstrate semantics and scheduling, not actual infrastructure use. Live proofs target gasless StudioNet, chain61999, a testing environment.
