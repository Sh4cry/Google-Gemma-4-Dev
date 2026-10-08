# Gemma 4 Developer Agent Competition Starter Kit

This repository provides the official declarative agent structure, validation scripts, packaging automation, and prompt scaffolds for **The Gemma 4 Developer Agent Competition** on Kaggle.

---

## 📁 Repository Structure

```
d:/gemma-4-developer-agent/
  ├── agent.yaml                     # Root competition agent specification
  ├── submission.zip                 # Built submission archive ready for Kaggle upload
  ├── prompts/
  │   ├── system.md                  # Primary autonomous SWE system prompt
  │   └── reviewer.md                # Sub-agent code analyzer / reviewer prompt
  ├── configs/
  │   ├── sampling.yaml              # Model generation parameters (temp, top_p, tokens)
  │   └── eval_config.yaml           # Local evaluation timeouts and turn budgets
  ├── sub_agents/
  │   └── code_analyzer.yaml         # Optional nested sub-agent template
  ├── scripts/
  │   ├── validate_submission.py     # Validates YAML syntax, file limits, and includes
  │   └── package_submission.py      # Packages submission.zip with correct root paths
  └── notebooks/
      └── gemma4_starter_baseline.ipynb # Notebook for running/testing on Kaggle GPUs
```

---

## 🚀 Quick Start: Submitting Your Baseline

### 1. Validate the Configuration
Run the local validator to ensure all files and schema constraints are satisfied:
```powershell
python scripts\validate_submission.py
```

### 2. Package `submission.zip`
Build the ZIP archive with `agent.yaml` placed strictly at the root:
```powershell
python scripts\package_submission.py
```

### 3. Upload to Kaggle
1. Open the [Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent).
2. Click **Submit Predictions / Submit Agent**.
3. Upload `submission.zip` from `d:\gemma-4-developer-agent\submission.zip`.

---

## 🧠 Developing & Improving Your Agent

### 1. Iterating on Prompts (`prompts/system.md`)
The zero-shot performance depends heavily on the reasoning scaffold:
- **Exploration & Localization:** Instructing the model to use `search_similar_code` and `git grep` rather than reading entire files.
- **Surgical Edits:** Enforcing minimal diffs to avoid touching unrelated code.
- **Verification Loop:** Mandating test execution before invoking `submit_patch`.

### 2. LoRA Fine-Tuning (Cloud / Kaggle GPU Workflow)
*Since fine-tuning a 31B parameter model (`gemma-4-31b-it-qat-w4a16-ct`) requires an NVIDIA GPU, perform training using Kaggle's free GPU accelerators or cloud instances:*
1. Curate multi-turn SWE-bench trajectories (issue -> search -> edit -> test -> patch).
2. Format data using Gemma 4's chat tokens (`<start_of_turn>user`, `<start_of_turn>model`).
3. Train LoRA adapters using QLoRA / PEFT.
4. Save the adapter weights (`adapter_model.safetensors` + `adapter_config.json`) into an `adapters/` directory.
5. Reference the adapter in your `agent.yaml` configuration.

---

## 🛠️ Built-in Tools Available in Sandbox
- `run_command`: Execute shell commands (e.g. `pytest`, `git diff`).
- `read_file`: Inspect code file contents.
- `edit_file`: Apply structured replacements in existing files.
- `write_file`: Create new files.
- `get_status`: Inspect git status and changed files.
- `submit_patch`: Finalize and submit the solution patch.
- `get_code_neighbors`: Code graph navigation for symbol relationships.
- `search_similar_code`: Semantic code search across the repository.
- `get_code_subgraph`: Extract dependency subgraphs for targeted functions.
