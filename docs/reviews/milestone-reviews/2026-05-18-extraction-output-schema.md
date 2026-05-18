# Milestone Review: Extraction Output JSON Schema

## Scope Reviewed

Machine-readable `extract_units` output schema rendering:

- AI-layer JSON Schema generator
- CLI command `diamonddust extraction-output-schema`
- docs and guide linkage
- enum drift tests against domain enums
- fixture runtime validation

## Product Goal Alignment

Pass with follow-up. The stage makes provider structured-output planning more concrete while keeping real provider integration blocked behind explicit approval.

## Architecture Boundary Compliance

Pass. The schema generator lives in the provider-neutral AI boundary and imports only domain enum definitions. Domain core remains free of provider SDKs, CLI, and storage dependencies. The CLI only prints the generated schema.

## Cohesion Assessment

Pass. Schema enum values are derived from existing domain enums, reducing duplication. Runtime extraction validation remains in the existing typed validation path.

## Coupling Assessment

Pass with follow-up. The schema generator intentionally depends on domain enum definitions. If future provider-specific schema dialects are needed, they should be added as adapter-level transforms rather than changing domain validation.

## Data and Schema Safety

Pass with follow-up. This stage introduces a machine-readable contract aid but not a persisted artifact schema or runtime JSON Schema validator. Tests cover JSON serializability, top-level shape, enum alignment, and fixture compatibility.

## AI Output Boundary

Pass. No provider was called, no API key values were read, no SDK dependency was added, no raw provider output was persisted, no patch acceptance was recorded, and no formal vault write behavior changed.

## Tests and Evaluation

Pass.

- 19 focused schema/CLI/docs tests passed.
- 201 unit tests passed.
- Compile check passed.
- Diff whitespace check passed.
- Local trial fixture smoke passed.
- Extraction schema CLI smoke passed.
- Domain architecture scan reported 0 violations.

## Dependency and Portability Impact

Pass. No production or development dependency was added.

## Risks

- JSON Schema cannot express every runtime validation rule, especially source references matching top-level `source_input_id`.
- Provider-specific structured-output APIs may require schema transforms later.
- A future runtime JSON Schema validator would require separate dependency review.

## Required Changes Before Continuing

- None for this stage.

## Optional Improvements

- Add provider-specific schema transforms only after the first provider and structured-output mechanism are approved.
- Add runtime JSON Schema validation only if typed validation alone becomes insufficient for real provider debugging.

## Escalation Requests

None. This stage stayed within provider-neutral planning boundaries and did not introduce high-impact behavior.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
