---
quick_id: 261005-q3t
status: complete
---

# Summary

Server: 52/52 tests pass (commit 39ef42c). Client: `npm run build` passes; verified in the browser: over-checkout shows "Only 10 available -- can't check out 50." with capacity/available unchanged; checkout 4 then checkin 1 gives available 7, capacity 10.

Removed from the UI (backend routes kept): request/release controls and the requests list. The `Modal`, `Checkout`, and `RestockForm` components were deleted.
