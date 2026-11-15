# Guru — Requirement Approval and Change-Control Workflow

## Principle

No new feature or material change is implemented until the product owner has reviewed and explicitly approved the requirement.

## Workflow

1. **Identify:** Record the user problem and proposed enhancement in `FEATURE_BACKLOG.md` or a new change request.
2. **Clarify:** Define actors, workflow, inputs, outputs, exceptions, data handling and constraints.
3. **Specify:** Add uniquely numbered FR/NFR requirements and measurable acceptance criteria to the FRD.
4. **Assess:** Review design, API, data, RAG, privacy, security, testing, cost and deployment impacts.
5. **Present for approval:** Share the complete requirement and ask the product owner to approve, reject or defer it.
6. **Baseline:** After approval, mark the requirement Approved, update the version and add RTM rows and test IDs.
7. **Implement:** Develop only the approved scope.
8. **Verify:** Execute the tests and record evidence; update RTM status.
9. **Release and document:** Update README, architecture, setup instructions, change log and release notes.

## Approval vocabulary

- **Approved:** Scope and acceptance criteria are authorised for implementation.
- **Rejected:** Do not implement; retain the decision and rationale.
- **Deferred:** Keep in backlog; no development is authorised.
- **Needs clarification:** Return to requirements analysis; no development is authorised.

A discussion, suggestion or inclusion in a backlog is not approval.
