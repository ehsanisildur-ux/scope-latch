# StudioNet proofs

Deployed through GenLayer CLI on gasless StudioNet (chain 61999).

Contract: `0xce35C4aD8e0B08e309863c35a3551478f3057fA8`.

[Deployment transaction](https://explorer-studio.genlayer.com/tx/0x422fbeee26ac8706effb8324d6853d057dc57e3543a2463a28b185dcc6bb3811) · [successful CLI run](https://github.com/ehsanisildur-ux/scope-latch/actions/runs/37182040834) · [deployment manifest](deployment.json).

All 11 receipts are FINALIZED, MAJORITY_AGREE and execution-successful. Contract source bytes match the published source (SHA-256 `8f13ceb1150a88c4aee19556bf4c5576a6e11accc7970b71d57d9e099a163841`). Each write was followed by an onchain state read.

| Scenario | Transaction | Verified behavior |
|---|---|---|
| Atomic grant | [receipt](https://explorer-studio.genlayer.com/tx/0x9d72ba3e2116040828f49305242e6608af6292e1c8ae6e5babe5521603530a75) | Database and routing granted together |
| Conflict queue | [receipt](https://explorer-studio.genlayer.com/tx/0x1462f020196ed13b7d94156e5267a19762998f2e58c160e38f7ab431d6fa114d) | Conflicting request waits |
| FIFO barrier | [receipt](https://explorer-studio.genlayer.com/tx/0x1bdd5d0c018202a135960bc697dacabeb55614d6b1d8bb8625e21b7a7bc27402) | Free identity resource cannot bypass blocked head |
| Read-only plan | [receipt](https://explorer-studio.genlayer.com/tx/0x8f475096d17181a96d87b8d8ba07942374e6720f7fde39ce5b671a78f25250bb) | NO_LOCKS |
| Ambiguous plan | [receipt](https://explorer-studio.genlayer.com/tx/0x2555c34eb856b13f6c07c6d2a1580e6ecfeb3ea3740449946b816828e32facd8) | REVIEW without acquiring locks |
| Cancel barrier | [receipt](https://explorer-studio.genlayer.com/tx/0x2b05f9aea5982c6eaf78af67d82ccb51a8771c5483e64e422c183c91d98c0097) | Cancellation admits identity waiter |
| Release original | [receipt](https://explorer-studio.genlayer.com/tx/0x1f4db8d7e4482fd663925b92f7d221efef4a34b208287300e518ef7685e6a560) | Database and routing freed |
| Reuse | [receipt](https://explorer-studio.genlayer.com/tx/0xb954bf49315ad00715691c29d1e28a58d8ea59ae5a221d56d31409c84cc63a18) | Released resources acquired again |
| Release reuse | [receipt](https://explorer-studio.genlayer.com/tx/0x466afee9c527e9da5127db55000a5bf7b437c483e50ce4ab1af477308cf4a2a0) | Reused resources freed |
| Release identity | [receipt](https://explorer-studio.genlayer.com/tx/0x28332895e51e751de96f37a41ae9b053aa799a8477ac86af6a458aa9cab583b0) | All resource slots free |

Receipts preserve dissent: FIFO barrier has three agree/two disagree; reuse has three agree/one disagree/one idle. Majority agreement does not mean unanimity.

Run `node scripts/verify-proofs.cjs` to check receipt outcomes, source hashes, quote substrings, plan commitments, footprints and lock invariants. The verifier checks recorded evidence offline; the CLI run performed live reads.

The initial run stopped after five successful requests when the RPC gateway returned HTML during cancellation submission. The complete run above uses a fresh ephemeral account and pool. Synthetic plans demonstrate coordination, not execution; ephemeral proof accounts are not retained for continued operation of this pool.
