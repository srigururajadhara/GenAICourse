# Guru Enhancements — Requirements Approval Workflow

## 1. Governing rule

**No new implementation begins until the product owner explicitly approves the detailed requirements and acceptance criteria.** Approval of the visual direction or roadmap is not automatically approval of every technical detail or model choice.

## 2. Workflow

1. **Capture:** record the problem, user goal, expected outcome and priority.
2. **Specify:** add functional/non-functional requirements to the FRD with unique IDs.
3. **Design:** update the architecture and UI/UX specification.
4. **Trace:** map every requirement to design, implementation target and test IDs in the RTM.
5. **Test design:** prepare positive, negative, boundary, accessibility and regression cases.
6. **Impact review:** check dependencies, shared `venv312`, baseline isolation, data/index compatibility, latency and cost.
7. **Product-owner review:** present scope, open decisions and acceptance criteria.
8. **Approval gate:** wait for explicit approval for the identified version/scope.
9. **Implementation:** only approved items are developed inside `guru_ai_enhancements`.
10. **Verification:** execute tests and record evidence/status.
11. **Acceptance:** product owner accepts or raises defects/change requests.

## 3. What counts as approval

An explicit statement such as “I approve FRD v0.1 for implementation” or approval of a clearly enumerated subset of requirement IDs. General agreement that the project is a good idea, or acceptance of a design direction, is not sufficient to implement all requirements.

## 4. Changes after approval

Any change to scope, acceptance threshold, architecture, dependency or user data handling must be recorded in `CHANGE_REQUEST_TEMPLATE.md`, impact-assessed and approved before implementation.

## 5. Requirement status model

- Draft
- In Review
- Approved
- Implemented
- Verified
- Accepted
- Deferred / Rejected

Do not mark a requirement Implemented or Verified before code and test evidence exist.
