# Review Workspace Workflow

This pack governs the control boundary for thesis review workspaces.

It does three things:

1. Forces review before advice.
2. Promotes high-risk simple requests back into review.
3. Keeps runtime state in the paper-level governed pack, not in this repo truth pack.

Core path:

1. Enter at `node.review`.
2. Collect the minimum high-level review evidence set.
3. Transition to `node.advice` only after review evidence is complete.
4. Roll back to `node.review` when advice must be reopened under stricter review.

Non-goals:

1. Do not model full expert cognition as a rigid linear state machine.
2. Do not move thesis-specific runtime ledgers into repo truth by force.
