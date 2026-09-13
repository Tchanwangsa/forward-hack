# Field triage — the procedure, executed

**What this is.** Outage watch establishes *what* happened and that nobody wrote it
down. This is the tier that establishes *why*, by running the operations team's own
triage procedure against the estate and writing the result where the ops team writes
it — the troubleshooting log, whose `Action Taken` column is blank on 66% of its rows
because the work happens on a phone call and never reaches the spreadsheet.

**The hinge:** the agent does not reason about root cause. It *follows a controlled
document*. OPS-SOP-004 is a real procedure with a revision number, an owner, an
approver and a decision tree, and the agent walks it clause by clause. That is the
difference between a diagnosis a quality team can sign off on and a paragraph a model
produced. A cause the procedure cannot reach is escalated, never invented.

---

## 1. The document and its twin

| | |
|---|---|
| Controlled PDF | [`mock-company/sops/OPS-SOP-004-Outage-Triage.pdf`](../mock-company/sops/OPS-SOP-004-Outage-Triage.pdf) |
| Executable twin | [`reference-data/sop/OPS-SOP-004-outage-triage.yaml`](../reference-data/sop/OPS-SOP-004-outage-triage.yaml) |
| Typesetter | `make sop` → `backend/tools/sop_pdf.py` |

Both come off one definition, so on the day of issue they cannot disagree. Afterwards
they can — somebody edits one and not the other — and the YAML pins the issued PDF by
SHA-256. Triage refuses to run against a document that has moved (`SupersededProcedure`),
because an agent confidently and traceably following a superseded revision is worse than
an agent with no procedure at all.

Every action the agent logs carries `OPS-SOP-004 rev 3.0`. When the SOP moves to 4.0,
last quarter's decisions still say which rules they were made under.

## 2. The decision tree

Eight steps, worked in order. Each is complete when its checks have been performed and
**recorded — whether or not they found anything** (§3 C3).

| | Step | Asks | Concludes |
|---|---|---|---|
| §5.1 | Establish scope | One unit, or the whole site? | → §5.4 when site-wide |
| §5.2 | Rule out expected absence | Did somebody mean for this to stop? | `expected-removal` |
| §5.3 | Power and dock | Is it getting power? | `power-loss` |
| §5.4 | Site network path | Can the site reach us? | `site-network` |
| §5.5 | Data box service | Is the aggregator shipping? | `data-box-backlog` |
| §5.6 | Hub device | Is the unit healthy? | `device-fault` |
| §5.7 | Patch link | Is the consumable the problem? | `consumable-patch` |
| §5.8 | Classify and record | What gets written down? | `unknown-escalate` |

**§5.2 runs before any technical check, deliberately.** The commonest reason a hub stops
reporting is that the patient was discharged, died, or the unit was moved — and an
incident row written for that is a false signal that ends up in a rate, in a report and
eventually in front of a regulator. A benign close is still recorded: a closed episode
with no record is indistinguishable from an episode nobody looked at.

**§5.7 is last and is asked, not asserted.** Everything below it in the stack produces
the same reading, and a radio cannot see a piece of tape. `consumable-patch` carries a
confidence below the queue's question threshold, so it renders as a question for the
ward — the same rule `ADHESIVE` already obeys in [`TELEMETRY-API.md`](TELEMETRY-API.md) §5.

## 3. The eight tools

Read-only, every one. §3 C1 and [`TELEMETRY-API.md`](TELEMETRY-API.md) §7 say the same
thing from two directions: remote access to a customer's estate is granted for diagnosis,
and a product that quietly widens it to remediation has changed what the customer agreed
to. There is no ninth tool that restarts anything, and `test_the_tool_set_is_the_granted_one`
fails if one appears.

```
fleet.hub_status       fleet state, peers affected, the site-wide question
fleet.heartbeat_gaps   where the silence starts and whether it ended
registers.context      prior incidents, planned-works notices — read before touching
ward.occupancy         bed occupied at onset: yes or no, and nothing else (§3 C2)
power.socket_check     PDU port, last draw, dock, battery at silence
net.path_check         tunnel, DNS, loss, rtt, local segment
ssh.databox            collector, queue depth, disk, cert — the site aggregator
ssh.hub                uptime, restarts, POST, link margin — one session, two steps
```

Each returns **metrics** (which the procedure's conditions read) and a **transcript**
(what the analyst would have seen). The transcript is provenance, not decoration: if the
agent says the upload queue was 21,060 deep, the queue shows the line it read that from.
A step that reads a session an earlier step opened says so rather than appearing skipped.

## 4. How it is honest

The estate layer ([`triage/estate.py`](../backend/asteria/triage/estate.py)) derives one
**situation** per episode — the hidden cause the tools then reflect. The runner never
sees it. It reads tool output, follows the tree, and reaches an outcome, so comparing
the two is a real score rather than a tautology, and the run that lands on
`unknown-escalate` because nothing matched is the procedure working.

Situations are derived, not random: a site cluster is overwhelmingly a network event, a
`DISPLAY` fault is a device, a hub the inventory has decommissioned was pulled on
purpose. Randomness only chooses between causes the evidence leaves open, seeded on the
episode's own artifact reference so a re-run reaches the same place.

**Current run:** 288 episodes, 281 diagnoses matching the situation, 59 escalated as
inconclusive, 16 closed as not an incident, 2,074 checks. The misses are almost all
patch cases sitting above the −85 dBm the procedure sets at §6 — which is a finding
about the threshold, not a bug in the agent, and exactly the kind of thing this scoring
exists to surface.

## 5. What it writes

| Output | Where | Note |
|---|---|---|
| Drafted row | `PM-Data-Check-and-Troubleshooting-Log` | `Issue Found`, `Action Taken`, the right one of the four issue columns, and what was cleared first |
| Completion | the incident row's `Notes` | offered only when the cell is blank and no other bot has claimed it |
| `TriageRun` + steps | the audit trail | every clause, every probe, every transcript, the revision in force |

`Checked By` is never drafted. A check has a name against it because somebody is
accountable for it, and the agent is not a person — it is blank by design until a
reviewer's name goes on the row. Nothing here commits: capture is autonomy level 3,
always.

---

## 6. Next: the fleet simulator

Everything above runs over a frozen NDJSON file with a fixed clock. The next step makes
the fleet move.

**A generator posts real events at an accelerated clock** — the demo setting
[`TELEMETRY-API.md`](TELEMETRY-API.md) §4 already names, not a second code path. Shape of it:

- **Scenarios, not events.** One hidden root cause unfolds over time: a site cutover
  emits eleven offlines across ninety seconds, then silence, then a return. That is what
  makes episode grouping visible live, and a scenario is exactly a `Situation` — so
  `estate.derive` gains an injection path and nothing downstream changes.
- **Poisson arrivals with a diurnal curve**, per-hub hazard weighted by cohort so the
  planted stories keep emerging (SW 1.1.0 carries higher `ALERT-FALSE` intensity) and
  night-shift network windows land at night. One scenario every few minutes of demo time
  is watchable; more is noise.
- **One hidden cause drives both sides.** The scenario decides the telemetry *and* the
  tool responses, so when the agent SSHes the data box the disk really is full. The
  diagnosis stays derived rather than scripted, and the live demo is also an eval.
- **The loop closes on screen:** events land → outage watch drafts the row → triage runs
  the procedure → the diagnosis and the drafted troubleshooting row appear, with the
  transcripts behind them. Nothing committed without a human, at any speed.
