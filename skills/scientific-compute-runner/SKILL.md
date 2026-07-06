---
name: scientific-compute-runner
description: "Use when MAS needs a refs-only scientific compute diagnostic playbook inspired by AcademicForge compute-env-setup, remote-compute-ssh, remote-compute-modal, managed-model-endpoints, and using-model-endpoint. OPL Runway/Connect owns substrate; this skill owns AI diagnostics and deterministic receipt refs only, without writing domain truth, signing owner receipts, creating typed blockers, or claiming publication readiness."
---

# Scientific Compute Runner

Use this optional MAS Scholar Skills specialist when a task needs compute
diagnosis, environment planning, job handoff, or model-endpoint invocation
guidance for scientific workloads. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` patterns from
`compute-env-setup`, `remote-compute-ssh`, `remote-compute-modal`,
`managed-model-endpoints`, and `using-model-endpoint`.

Boundary: OPL Runway, Connect, Fabric, or the configured compute provider owns
runtime substrate, credentials, remote hosts, queues, endpoints, approvals,
harvest, lifecycle, and provider errors. This skill owns only the AI diagnostic
playbook and deterministic receipt ref shape.

This skill is refs-only and no-authority. It can prepare compute diagnostic
refs, environment candidate refs, job plan refs, endpoint request refs,
deterministic helper receipts, and `owner_gate_handoff_ref`; it cannot write
runtime state, domain truth, owner receipt, typed blocker, quality verdict, or
publication readiness.

## Workflow

1. State the workload question, expected inputs/outputs, hardware need, time
   budget, privacy boundary, and owner-approved compute route.
2. Record `compute_requirement_ref`, `environment_probe_ref`,
   `provider_selection_ref`, and `credential_boundary_ref`.
3. Prefer existing OPL substrate readbacks over new scripts. Helpers may only
   produce deterministic receipts: command, inputs, output manifest, sha256,
   exit code, and limitations.
4. For SSH or Modal-style remote compute, bind job plan, staged inputs,
   featured outputs, poll/harvest refs, and failure classification. Do not
   bypass approval or credential boundaries.
5. For managed model endpoints, separate registration/lifecycle ownership from
   inference-call evidence. Record endpoint request/response refs without
   exposing credentials.
6. Route back when the missing piece is owner approval, credential, provider
   configuration, hardware availability, or domain interpretation.

## Handoff Shape

Return:

- `compute_question`
- `compute_requirement_ref`
- `provider_selection_ref`
- `environment_probe_ref`
- `job_plan_ref`
- `endpoint_request_ref`
- `deterministic_receipt_ref`
- `output_manifest_ref`
- `failure_classification_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not treat a clean compute run, harvested file, endpoint response, or helper
receipt as MAS runtime readiness, domain truth, owner acceptance, typed blocker,
or publication readiness.
