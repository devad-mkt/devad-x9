# Workflow: GitHub / Developer Doc

Handles: READMEs, API references, CLI tutorials, SDK guides, code repository docs, developer-facing documentation.

Load `SKILL.md` first. This file provides developer-doc-specific structure and linguistic rules.

---

## Structural Model

```
1. Title & Architecture Overview
   └─ 1 Subject-Verb-Object sentence: what the module/library does

2. Prerequisites & Installation
   ├─ Exact versions, OS limits, dependency requirements
   └─ Clean copy-paste CLI commands

3. Quickstart / Minimal Working Example
   └─ Working code block with inline comments explaining key parameters

4. API / Parameter Reference Table
   └─ | Parameter | Type | Required? | Default | Description & Constraints |

5. Usage Examples
   └─ 3–5 progressive examples from basic to advanced

6. Troubleshooting & Error Matrix
   └─ | Error Code / Symptom | Root Cause | Exact Resolution Command |

7. Configuration Reference (if applicable)
   └─ Environment variables, config file format, defaults

8. Contributing / License (if applicable)
```

---

## Title & Overview Rules

### One-Sentence Summary
The first line of the README must be one SVO sentence stating what the project does.

- **Wrong:** "A powerful tool for managing your data pipelines with ease."
- **Right:** "Dataflow parses CSV and JSON inputs, validates schemas, and routes records to PostgreSQL or BigQuery."

### Badges (Optional)
If badges are used, keep them factual:
- Version number, license, build status, coverage percentage.
- No "made with love" or "awesome" badges.

---

## Prerequisites & Installation

### Version Precision
State exact version requirements:

- **Wrong:** "Requires Node.js and npm."
- **Right:** "Requires Node.js 18+ and npm 9+."

### CLI Commands
Provide copy-paste ready commands. No placeholders unless clearly marked:

```bash
# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev
```

Rules:
- Prefix each command with a comment explaining what it does.
- Include the expected output or success indicator when helpful.
- Specify the working directory if commands must run from a subfolder.

---

## Quickstart Example

### Working Code Block
Provide a minimal working example that runs without modification:

```python
from dataflow import Pipeline

# Configure the pipeline with schema validation
pipe = Pipeline(
    source="data/customers.csv",
    schema={"name": "str", "email": "str", "age": "int"},
    target="postgresql://localhost:5432/mydb"
)

# Run the pipeline and print record count
result = pipe.run()
print(f"Processed {result.record_count} records")
```

Rules:
- Every code block must be syntactically correct and runnable.
- Include inline comments for non-obvious parameters.
- Show expected output when deterministic.
- Use realistic variable names, not `foo`, `bar`, `temp`.

---

## API / Parameter Reference Table

### Table Format

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | `str` | Yes | — | Path to input file. Supports CSV, JSON, and Parquet formats. |
| `schema` | `dict` | No | `None` | Validation schema. Keys are field names, values are type strings. |
| `target` | `str` | Yes | — | Connection string for the output database. |
| `batch_size` | `int` | No | `1000` | Number of records per insert batch. Must be between 100 and 10000. |
| `dry_run` | `bool` | No | `False` | When `True`, validates input without writing to the target. |

Rules:
- Every parameter from the source code must appear in the table.
- Type must match the code type exactly (`str`, `int`, `bool`, `float`, `dict`, `list`).
- Required column must say `Yes` or `No` — never `Optional` (redundant with `No`).
- Default column must show the actual default. Use `—` when no default exists.
- Description must state constraints, valid values, and behavior.

---

## Troubleshooting & Error Matrix

| Error / Symptom | Root Cause | Resolution |
|-----------------|------------|------------|
| `SchemaValidationError: field 'age' expected int, got str` | CSV contains non-numeric values in the `age` column | Clean the source data or add `age: "str"` to the schema |
| `ConnectionRefused: postgresql://localhost:5432` | PostgreSQL server not running or wrong port | Start the server: `sudo systemctl start postgresql` |
| `FileNotFoundError: data/customers.csv` | Wrong working directory or missing file | Run from the project root or provide absolute path |

Rules:
- Every error must show the exact error message or symptom.
- Root cause must be specific, not generic ("check your input").
- Resolution must be a copy-paste command or exact configuration change.
- Cover the top 5–10 most common errors from issue trackers, tests, or code inspection.

---

## Linguistic Guardrails for Developer Docs

### 100% Imperative Verbs
All instruction sentences use imperative mood:

- **Wrong:** "You should configure the database connection before running the pipeline."
- **Right:** "Configure the database connection before running the pipeline."

Verb catalog: Run, Configure, Pass, Export, Import, Install, Clone, Build, Test, Set, Create, Add, Remove, Update, Check, Verify, Specify, Define, Replace.

### Zero Conversational Filler
These phrases are forbidden:
- "First, let's...", "Now we need to...", "Simply...", "Just...", "It's easy to..."
- "In this section, we will...", "Here, you can...", "As you can see..."

### Code-First Explanation
Explain through code and parameters, not prose:

- **Wrong:** "The pipeline is really flexible and can handle many different types of data sources, which makes it great for complex data workflows."
- **Right:** "The pipeline accepts CSV, JSON, and Parquet inputs. Configure the `source` parameter with a file path or glob pattern."

---

## Developer Doc QA Additions

In addition to the master scorecard:

- [ ] **Code correctness:** Every code block is syntactically valid and runnable.
- [ ] **Parameter coverage:** Every parameter from source code appears in the reference table.
- [ ] **Version precision:** All version requirements are exact numbers.
- [ ] **Error coverage:** At least 5 common errors with exact resolution commands.
- [ ] **Imperative mood:** All instruction sentences use imperative verbs.
- [ ] **No filler:** Zero conversational phrases or marketing language.
