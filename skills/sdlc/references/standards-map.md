# Risk-Selected Standards Map

Use standards as question sets. Do not turn every listed practice or quality characteristic into a deliverable.

## OWASP SAMM v2

SAMM defines five business functions and fifteen practices:

| Function | Practices | Feature-level use |
|---|---|---|
| Governance | Strategy and Metrics; Policy and Compliance; Education and Guidance | Apply only when organizational policy, measurement, training, or external obligations are in scope |
| Design | Threat Assessment; Security Requirements; Secure Architecture | Select changed trust boundaries, misuse cases, security acceptance, and architecture constraints |
| Implementation | Secure Build; Secure Deployment; Defect Management | Reuse build/dependency/deploy gates and record material defects |
| Verification | Architecture Assessment; Requirements-driven Testing; Security Testing | Prove requirements and changed security controls with targeted tests/review |
| Operations | Incident Management; Environment Management; Operational Management | Apply when runtime, environment, data protection, detection, response, or decommissioning changes |

A feature usually touches a subset. A formal SAMM maturity assessment is an organizational exercise and is not implied by High mode.

## ISO/IEC 25010:2023

The current product-quality model has nine characteristics. Use these high-level prompts without claiming certification or reproducing proprietary standard text:

| Characteristic | Ask only when changed |
|---|---|
| Functional suitability | Does the behavior meet the real requirement completely and correctly? |
| Performance efficiency | Does the change affect latency, throughput, capacity, or resource use? |
| Compatibility | Does it alter coexistence, interoperability, formats, APIs, or versions? |
| Interaction capability | Does it affect usability, accessibility, learnability, or error prevention? |
| Reliability | Does it affect availability, fault tolerance, recoverability, or continuity? |
| Security | Does it affect confidentiality, integrity, authenticity, accountability, or resistance? |
| Maintainability | Does it increase coupling, complexity, duplication, test cost, or change risk? |
| Flexibility | Does it alter adaptability, scalability, installability, or replaceability? |
| Safety | Could failure create harm or unacceptable risk? |

## Minimal Mapping Rule

1. Identify the changed behavior and boundary.
2. Select at most the materially affected characteristics/practices.
3. Convert each into one acceptance question or existing gate.
4. Add a new artifact only when the answer cannot be proven otherwise.
5. Stop after the selected evidence passes.

## Sources

- OWASP SAMM model: https://owaspsamm.org/model/
- OWASP SAMM core: https://github.com/owaspsamm/core
- ISO/IEC 25010:2023 abstract and status: https://www.iso.org/standard/78176.html
