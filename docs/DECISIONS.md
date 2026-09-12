# Decisions

Recorded so a fresh session does not re-litigate them. Each one was a real
fork, and the reason matters more than the choice.

## D1 — Solve the rug pull, not the malicious server

**Decided:** the failure mode is a server that was reviewed and approved, then
changed its tool descriptions afterwards.

**Why:** "don't install untrusted MCP servers" is expected, documented, and
already has alarms. Approval that silently never expires does not. A failure
mode practitioners have not yet built an alarm for is what distinguishes this
from the median submission.

**Rejected:** a general MCP security scanner. Too broad to demo and it competes
with a category that already exists.

## D2 — Deterministic core, model only as advisory

**Decided:** hashing and byte comparison decide. `inspect.py` labels text for
human reading and never influences forwarding.

**Why:** two reasons. It survives the question "what if your detector is
wrong?", and it survives the harder test — would this still be valuable if a
user simply pasted the same context into a chat model? State across time plus a
position in the execution path cannot be prompted.

## D3 — stdio transport only

**Decided:** one transport.

**Why:** 7 solo days. A second transport adds no new claim and no new frame in
the video. HTTP is item 2 on the cut list, not a stretch goal.

## D4 — Dashboard is expendable, the video is not

**Decided:** if Gate 2 slips, the dashboard is cut and replaced with coloured
terminal output; the reclaimed hours go to the video.

**Why:** judging is asynchronous. Judges watch a ≤5-minute video and read a
submission page; they most likely never clone the repo. Depth that does not
appear on screen scores nothing. A product without a video loses; a video
without a dashboard wins.

## D5 — Side-by-side as the demo form

**Decided:** one terminal, two columns, same agent and same server on both
sides, with the left column leaking before the right column resolves.

**Why:** the contrast has to be legible in a single frame without narration.
The chosen image is a green ✓ Success appearing at the exact moment credentials
leave — the agent did not error, it worked correctly, and that is the point.

## D6 — The name

**Decided:** Customs.

**Why:** it describes the mechanism — everything is inspected on the way in,
every time, regardless of having been cleared before. A name someone can guess
the function of beats a name that sounds impressive.

## D7 — Submit twelve hours early

**Decided:** target 24 Sept 19:00 WIB, not the 07:00 WIB deadline the next
morning.

**Why:** submissions can be updated; a submission that never uploaded cannot.
Competition platforms are slowest in their final hours.

## D9 — Seal covers name, description, input_schema only

**Decided:** the pinned manifest is `{name, description, input_schema}`.
MCP fields such as `outputSchema`, `title`, and `annotations` are not hashed.

**Why:** the rug-pull failure mode is an instruction change in the tool
description. Output schemas and metadata do not carry agent-directed
instructions in the demo scenario, and hashing everything the protocol allows
would pin cosmetic server updates that never reach the agent's trust surface.

**Rejected:** hashing the full `tools/list` payload verbatim. Stable against
noise the operator did not approve, brittle against SDK field additions, and
harder to explain on screen.

## D8 — Landing page direction: Customs House

**Decided:** warm paper and stamp-bureaucracy typography for the narrative
sections, switching to a dark terminal ground exactly at the demo section.

**Why:** the metaphor comes from the product's own name rather than from a
trend, and the mid-scroll ground change supplies the one deliberate break in
the layout. It also avoids the dark-mode-with-one-acid-accent look that most
submissions will arrive in.
