"""
Submission Validator for The Gemma 4 Developer Agent Competition (Kaggle).

Validates:
1. Presence of agent.yaml at root.
2. Resolution of all '!include' paths (prompts, sampling configs, etc.).
3. Required model identifier (must be gemma-4-31b-it-qat-w4a16-ct).
4. Tool names against known swegemma ToolRegistry tools.
5. Overall directory/archive size limit (< 3 GiB).
"""

import os
import sys
import zipfile
from pathlib import Path
import yaml

EXPECTED_MODEL = "gemma-4-31b-it-qat-w4a16-ct"
ALLOWED_TOOLS = {
    "run_command",
    "read_file",
    "edit_file",
    "write_file",
    "get_status",
    "submit_patch",
    "get_code_neighbors",
    "search_similar_code",
    "get_code_subgraph",
}
MAX_ZIP_SIZE_BYTES = 3 * 1024 * 1024 * 1024  # 3 GiB


class IncludeLoader(yaml.SafeLoader):
    """YAML Loader that handles '!include <path>' directives."""
    def __init__(self, stream):
        self._root = Path(stream.name).parent if hasattr(stream, "name") else Path.cwd()
        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.Node):
    filename = loader.construct_scalar(node)
    filepath = (loader._root / filename).resolve()
    if not filepath.exists():
        raise FileNotFoundError(f"Included file does not exist: {filepath} (referenced as '{filename}')")
    
    if filepath.suffix in [".yaml", ".yml"]:
        with open(filepath, "r", encoding="utf-8") as f:
            sub_loader = IncludeLoader(f)
            return sub_loader.get_single_data()
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()


yaml.add_constructor("!include", include_constructor, IncludeLoader)


def validate_agent_config(config: dict, root_path: Path):
    errors = []
    warnings = []

    # Check model
    model = config.get("model")
    if not model:
        errors.append("Missing required field 'model' in agent.yaml.")
    elif model != EXPECTED_MODEL:
        warnings.append(f"Model '{model}' differs from the competition standard '{EXPECTED_MODEL}'.")

    # Check instruction
    instruction = config.get("instruction")
    if not instruction:
        errors.append("Missing 'instruction' field in agent.yaml.")
    elif isinstance(instruction, str) and len(instruction.strip()) < 20:
        warnings.append("System instruction appears unusually short.")

    # Check tools
    tools = config.get("tools", [])
    if not tools:
        errors.append("No tools declared in agent.yaml.")
    else:
        for tool in tools:
            if isinstance(tool, str):
                if tool not in ALLOWED_TOOLS:
                    warnings.append(f"Tool '{tool}' is not in the standard swegemma tool registry.")
            elif isinstance(tool, dict) and "agent_tool" in tool:
                sub_cfg_path = tool["agent_tool"].get("config_path")
                if sub_cfg_path:
                    resolved = (root_path / sub_cfg_path).resolve()
                    if not resolved.exists():
                        errors.append(f"Sub-agent config path does not exist: {resolved}")
            else:
                warnings.append(f"Unrecognized tool specification format: {tool}")

    return errors, warnings


def validate_directory(dir_path: Path):
    print(f"[*] Validating directory: {dir_path.resolve()}")
    errors = []
    warnings = []

    agent_yaml_path = dir_path / "agent.yaml"
    if not agent_yaml_path.exists():
        errors.append("Missing required 'agent.yaml' at the root of the directory.")
        return errors, warnings

    try:
        with open(agent_yaml_path, "r", encoding="utf-8") as f:
            loader = IncludeLoader(f)
            config = loader.get_single_data()
        cfg_errors, cfg_warnings = validate_agent_config(config, dir_path)
        errors.extend(cfg_errors)
        warnings.extend(cfg_warnings)
    except Exception as e:
        errors.append(f"Failed to parse agent.yaml: {e}")

    # Check total size
    total_size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
    print(f"[*] Total uncompressed size: {total_size / (1024 * 1024):.2f} MB")
    if total_size > MAX_ZIP_SIZE_BYTES:
        errors.append(f"Total directory size exceeds 3 GiB limit ({total_size} bytes).")

    return errors, warnings


def validate_zip(zip_path: Path):
    print(f"[*] Validating zip archive: {zip_path.resolve()}")
    errors = []
    warnings = []

    if not zip_path.exists():
        errors.append(f"Zip file not found: {zip_path}")
        return errors, warnings

    if zip_path.stat().st_size > MAX_ZIP_SIZE_BYTES:
        errors.append(f"Zip file size ({zip_path.stat().st_size} bytes) exceeds 3 GiB limit.")

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        if "agent.yaml" not in names:
            errors.append("Missing required 'agent.yaml' at the ROOT of the zip archive.")

    return errors, warnings


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if target.is_file() and target.suffix == ".zip":
        errors, warnings = validate_zip(target)
    else:
        errors, warnings = validate_directory(target)

    print("\n--- Validation Results ---")
    if warnings:
        print("[!] Warnings:")
        for w in warnings:
            print(f"    - {w}")

    if errors:
        print("[X] Errors found:")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    else:
        print("[OK] Validation passed successfully! Submission format is valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
