"""Pure deterministic CODEMIND *design simulation*, not a real subagent scheduler."""
from __future__ import annotations

from heapq import heappop, heappush


def simulate_validations(jobs: list[tuple[str, int, bool]], *, max_slots: int = 3) -> dict:
    """Model bounded FIFO host lease admission and release after confirmed cleanup.

    :param jobs: Ordered `(name, duration_units, cleanup_confirmed)` model inputs.
    :param max_slots: Simulated slot bound, never above the three-agent contract.
    :return: Reproducible event timeline; no process is started or monitored.
    """
    if not isinstance(max_slots, int) or isinstance(max_slots, bool) or not 1 <= max_slots <= 3:
        raise ValueError('max_slots must be 1..3')
    if not isinstance(jobs, list) or len(jobs) > 100:
        raise ValueError('jobs must be a bounded list')
    for item in jobs:
        if (not isinstance(item, tuple) or len(item) != 3 or not isinstance(item[0], str)
                or not item[0] or type(item[1]) is not int or not 1 <= item[1] <= 10000
                or type(item[2]) is not bool):
            raise ValueError('invalid declarative validation job')
    free=list(range(max_slots))
    # active entries: (finish, admission_index, slot_id, cleanup_confirmed)
    active=[]
    events=[]
    now=0
    pending=0
    completed=0
    quarantined=0
    peak=0

    def admit():
        nonlocal pending, peak
        while free and pending < len(jobs):
            slot=free.pop(0)
            name,duration,cleanup=jobs[pending]
            events.append({'name':name,'start':now,'finish':now+duration,'slot':slot,'cleanup_confirmed':cleanup})
            heappush(active,(now+duration,pending,slot,cleanup))
            pending+=1
            peak=max(peak,len(active))

    admit()
    while active:
        now=active[0][0]
        # Consume all terminals at this logical clock tick before recycling slots.
        while active and active[0][0]==now:
            _,_,slot,cleanup=heappop(active)
            if cleanup:
                completed+=1
                free.append(slot)
            else:
                quarantined+=1
        free.sort()
        admit()

    return {
        'schema':'codemind-validation-simulation-v1',
        'simulation_only':True,
        'max_slots':max_slots,
        'queued_at_start':max(0,len(jobs)-max_slots),
        'peak_active':peak,
        'completed':completed,
        'quarantined':quarantined,
        'remaining':len(jobs)-pending,
        'makespan':now,
        'events':events,
        'simulated_schedule_complete':completed==len(jobs) and quarantined==0,
    }