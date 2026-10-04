# Consensus and exclusion invariant

Clients own proposed plans. Public documents supply the exact plan text. The contract owns acquisition, semantic footprint agreement and an authoritative exclusion ledger for cooperating clients. There is no frontend-computed footprint.

1. A client submits an immutable raw GitHub URL and byte hash. The contract fetches and checks the complete UTF-8 document, capped at8,000 bytes.
2. Leader and validators classify EVERY fixed resource. Validator classification sees the complete document and rules but no proposed leader decisions. Every decision, including UNUSED and UNCERTAIN, must match exactly. Different valid quotations are allowed; an additional validator call checks the leader's anchors and omissions against the full plan.
3. USED indexes produce a sorted footprint deterministically. Any UNCERTAIN yields REVIEW and no queue slot eligible for locking. An empty known footprint yields NO_LOCKS. Hash and model failures do not append requests.
4. The bounded queue maintains a monotonic cursor to the oldest pending request. Admission assigns every requested lock simultaneously. A blocked head stops the drain. No later request can overtake it.
5. Creator release clears every held resource and drains the queue; creator cancellation removes a waiting barrier and drains it. Active requests cannot cancel; waiting requests cannot release.

Invariant: each resource holder is either -1 or an ACTIVE request containing that resource; every ACTIVE request holds its complete footprint, and WAITING/REVIEW/NO_LOCKS/CANCELLED/RELEASED hold none. All-or-nothing acquisition prevents partial acquisition within a request. Clients can still deadlock across requests if they retain one reservation while waiting for another; protocol clients must avoid that pattern. There is no liveness guarantee when clients refuse to release.

The plan commitment binds catalogue, original request ID, creator, locator, byte hash, decisions, quotes and footprint. Its committed initial status is WAITING, REVIEW or NO_LOCKS; scheduling status subsequently changes without changing the source commitment. Membership and catalogue are immutable. There are no certificate consumption methods, owner-controlled versions or confidence tolerances.
