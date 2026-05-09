---
name: constraint-escalation
description: "Create escalation requests when a rule, skill, instruction, dependency limit, architecture boundary, permission model, tool limitation, or user request appears to block quality or require high-impact behavior. Use before changing governance, public schema, production dependencies, external services, security, permissions, user data handling, destructive operations, formal write behavior, or review gates."
---

# Constraint Escalation

## Read

- `AGENTS.md`
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md`
- `docs/templates/ESCALATION_REQUEST_TEMPLATE.md`
- The specific docs, skills, plans, or code that create the conflict
- `docs/context/decisions.md` and `docs/context/open-questions.md` when prior context may matter

## Inputs

- Blocked goal
- Conflicting rule, instruction, tool limitation, or project constraint
- Evidence that following the constraint would reduce delivery quality or require high-impact behavior
- Safe fallback options

## Outputs

- An escalation request using the project template
- A clear exact user decision needed
- Updates to the active plan or repo memory when the blocker affects future work
- No implementation of the blocked change before approval

## Workflow

1. State the blocked goal in product terms.
2. Name the conflicting constraint and cite the relevant doc, skill, instruction, or tool limitation.
3. Explain why blindly following the constraint would reduce quality, safety, maintainability, portability, or reviewability.
4. Recommend the smallest permission, rule change, scope change, or fallback that resolves the conflict.
5. Describe risks if approved and the safe fallback if denied.
6. Continue only on unaffected work while waiting.
7. If approved, record the decision where project policy requires and continue within the approved boundary.
8. If denied, use the fallback and do not repeatedly ask unless new evidence appears.

## Does Not Constrain

- Low-risk internal implementation choices inside the approved task scope.
- Non-production helper choices that do not affect runtime behavior or governance.
- The agent's ability to propose better plans or safer alternatives.
- The user's authority over product scope, approvals, permissions, and high-impact tradeoffs.
