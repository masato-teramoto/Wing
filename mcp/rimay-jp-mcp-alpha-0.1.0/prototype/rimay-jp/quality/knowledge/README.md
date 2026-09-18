# Knowledge Asset (data, not code)

This tree is the customizable knowledge asset the engine consumes (FR-031). Edit these files to
tune the asset; you do not need to touch `src/reqsmell/` for source-supported smells.

```
knowledge/
├── layer1/
│   └── structure.yaml         # Layer 1 requirement structure (validated by schemas/layer1-structure.schema.json)
└── layer2/
    ├── catalog.yaml           # index of the nine smells -> rule files (exhaustive — FR-008)
    ├── severity-scale.yaml    # {high,medium,low} + per-smell default & justification (FR-013)
    ├── glossaries/
    │   ├── vague-verbs.en.yaml
    │   └── vague-verbs.ja.yaml
    └── rules/                 # one self-contained rule per smell × language (validated by schemas/rule.schema.json)
        └── <smell>.<lang>.yaml
```

Each rule embeds its own positive/negative example requirements, which serve as its tests
(Constitution V). To add or change a rule, see [../docs/adding-rules.md](../docs/adding-rules.md).
Every rule must carry a source `citation`; Japanese rules must also carry a `detection_basis`.
