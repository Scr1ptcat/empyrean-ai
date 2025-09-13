# Model Matrix

| Key                | Family         | Context | Notes |
|--------------------|----------------|---------|-------|
| devstral:24b       | code           | 128k    | Fast debugger/code nav |
| qwen3-coder:30b    | code           | 128k    | Strong codegen/review |
| qwen3:30b          | general_long   | 128k    | General QA, long ctx |
| gemma3:27b         | general        | 128k    | Planning/explanation |
| gemma3:27b-it-qat  | general_creative | 128k  | Creative/story |
| nemotron:70b       | heavy_reasoner | 64k     | Deep design analysis |
| gpt-oss:20b        | general        | 16k     | Docs/explanations |
| gpt-oss:120b       | general_heavy  | 32–64k  | Final escalation |

Set `gpu_layers` in Modelfiles for 70B/120B to fit 24 GB VRAM; expect CPU offload.
