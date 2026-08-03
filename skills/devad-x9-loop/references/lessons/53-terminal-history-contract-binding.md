# Lesson 53: Terminal History Contract Binding

Bug class: terminal historical Work Orders can become unreadable when a current
runtime validator evolves and doctor recomputes identity against current bytes.

Rule:
- Terminal historical Work Orders are inventory evidence. Doctor may verify
  them against the contract binding stored in the immutable Work Order only
  after the packet hash matches the database row, the task and order are
  terminal, and no active dispatch is being trusted from that task.
- Current dispatch, model-call, result-consumption, and nonterminal doctor
  gates use the current runtime validator binding and fail closed on drift.
- Terminal historical context capsules follow the same inventory boundary:
  doctor may verify the immutable `context_capsule_ref` path, hash, and size
  without revalidating that old capsule against the current source manifest.
  Active/current and nonterminal gates still validate context against current
  runtime/source bytes.

Never silently rewrite, upgrade, delete, move, or reclassify a historical Work
Order to make doctor pass. Packet, program, feature, worktree, active
claim/resource, unbound context, and tampered context/source references remain
real failures.
