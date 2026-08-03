# Sources and Adoption Decisions

**Reviewed:** 2026-07-19

These sources informed the skill. They are not runtime dependencies.

## Adopted

| Source | Bound revision/status | Adopted idea | Important limit |
|---|---|---|---|
| Local `ultra-reasoning-protocol` | SHA-256 `E582C7F59284DAC072A347B024EB05D7938E9632799F0F7BBD3F8E1F5201D0A0` | Risk-scaled depth, current evidence, alternative routes, challenge, verification, source versus activation readiness | No model-tier enforcement or exposed chain of thought |
| DietrichGebert/ponytail | `16f29800fd2681bdf24f3eb4ccffe38be3baec6b` | YAGNI/reuse/stdlib/native/installed-dependency/minimum-change ladder; read fully before minimizing | No unconditional one-line preference; never cut security, data protection, accessibility, or task-specific proof |
| OWASP SAMM core | `bc2b5474ab248effbc357c389bec372b0f5e200f` on `develop`; official site reports SAMM v2 five functions/fifteen practices | Risk-selected secure lifecycle questions | No automatic organizational maturity assessment or full practice matrix |
| ISO/IEC 25010:2023 | Published 2023-11, edition 2 | Nine product-quality characteristics as acceptance lenses | No certification claim, proprietary-text reproduction, or fake scoring |
| zircote-plugins/sdlc-quality | `292e3ac23bb8e0def1cae94fcb1e5023349e050d` | Lifecycle domains and required/recommended/optional distinction | No default full audit, project scaffolding, 0-100 score, or CI installation |
| OWASP Secure Agent Playbook | `79fea6b9115b55687818f8c4073844ee9ba907a6` | Evidence-backed specialized security procedures when a concrete domain warrants them | No automatic 17-skill or agent-team invocation |
| Kaademos/secure-sdlc-agents | `c6ec9104af2160a8b0e1edde9ae74e9e4bc8fb3a` | A specialist can help at a specific lifecycle gap | No routine eight-agent pipeline, template flood, MCP install, or token-heavy context |

Ponytail and zircote-plugins/sdlc-quality are MIT licensed. OWASP SAMM is CC BY-SA 4.0. This skill paraphrases high-level concepts and links the authoritative sources; it does not vendor their code or full text.

## Rejected as Defaults

- Installing any MCP server, plugin, scanner, dashboard, or CI workflow merely because it appears in a framework list
- Running every lifecycle specialist for every task
- Treating a compliance score as product evidence
- Generating Makefiles, templates, ADRs, changelogs, or release automation without a current need
- Assuming SAMM or ISO alignment means certification
- Treating author-reported benchmark savings as guaranteed results

The supplied attachment was treated as a research lead, not authority. Some descriptions compress important distinctions: tools may support MCP but still carry significant token/context cost; agent playbooks are procedures, not proof by themselves; current repository and official documentation must be checked before adoption.

## Primary Links

- https://github.com/DietrichGebert/ponytail
- https://github.com/owaspsamm/core
- https://owaspsamm.org/model/
- https://www.iso.org/standard/78176.html
- https://github.com/zircote-plugins/sdlc-quality
- https://github.com/OWASP/secure-agent-playbook
- https://github.com/Kaademos/secure-sdlc-agents
- https://owasp.org/www-project-agentic-skills-top-10/
