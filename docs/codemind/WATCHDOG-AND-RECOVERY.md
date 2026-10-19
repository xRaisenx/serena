# Dual-runtime watchdog and recovery contract (design, not yet deployed)

## Discovery before service registration
Identify the existing Windows Commander executable, config, current process owner, runtime interface and installed supervisor. Discover the Serena runner and actual health endpoint/transport. Do not invent ports or silently replace an installed launcher.

## Supervisor independence
- CODEMIND Serena observes Commander health through a read-only MCP status tool. The current implementation checks process presence only; it must NOT infer healthy MCP service from a PID.
- Windows Commander already offers serena_rescue_status, serena_rescue_logs and serena_rescue_restart. Automatic polling and recovery are NOT implemented by this fork.
- The target design uses an OS independent supervisor for each process. Each observes peer health but cannot recursively kill/restart its peer in a cycle.
- Loss of Serena must not kill Commander; loss of Commander must not kill Serena.
- No automatic shutdown or GUI interruption while implementing the watchdog.

## Failure classification
STARTING -> READY -> DEGRADED -> RECOVERING -> READY or CIRCUIT_OPEN. Persist last-known-good source/version, owner, failure fingerprint and restart history. A TCP listener alone is insufficient proof; authenticated MCP initialize and bounded read-only call is the readiness criterion.

## Guardrails before automatic recovery
- Exponential backoff and a minimum cooldown.
- At most three identical recovery attempts before circuit breaker/manual inspection.
- Restart only the failed child process, never broad process trees or arbitrary user apps.
- Preserve task/session identity, checkpoints, operation ownership and in-flight work.
- Do not circumvent repository mutation governance using the other process.
- Protect service credentials; use operating-system-protected storage or environment injection.
- Prefer read-only observation before any restart attempt.

## Validation
1. Cold start and shutdown with correct ownership.
2. Serena-only crash simulation: Commander persists and can observe/recover it without stopping.
3. Commander-only crash simulation: Serena persists and can observe failure without unbounded restarts.
4. Both fail: independent OS supervision recovers without circular storm.
5. Missing session token and unauthorized restart are denied.
6. Process and LSP child failures are independently classified.
7. CPU and RAM remain within the user's prescribed execution budget.
8. Reboot and logon lifecycle pass with the same release version and working MCP contracts.

No recovery acceptance can be claimed until every applicable fault-injection test is executed on the intended Windows host.
