#!/usr/bin/env python3
"""
Atualiza as seções auto-geradas de docs/architecture.md:
  - Data Model: diagrama de classes Mermaid extraído das entidades JPA
  - API Endpoints: tabela de endpoints extraída dos controllers Spring
  - Timestamp de última atualização
"""

import re
import os
import glob
from datetime import datetime, timezone

DOCS_FILE = "docs/architecture.md"
SRC_DIR = "src/main/java"


def find_java_files(subpath_pattern):
    return glob.glob(f"{SRC_DIR}/{subpath_pattern}", recursive=True)


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

def parse_entity_fields(filepath):
    """Extrai pares (tipo, nome) dos campos privados de uma entidade JPA."""
    fields = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Apenas linhas com campo privado simples: private Type name;
    pattern = re.compile(r"^\s*private\s+([\w<>\[\], ]+?)\s+(\w+)\s*;", re.MULTILINE)
    for match in pattern.finditer(content):
        field_type = match.group(1).strip()
        field_name = match.group(2).strip()
        fields.append((field_type, field_name))

    return fields


def build_class_diagram():
    entity_files = find_java_files("**/entity/*.java")
    if not entity_files:
        return None

    lines = ["classDiagram"]
    for filepath in sorted(entity_files):
        class_name = os.path.basename(filepath).replace(".java", "")
        fields = parse_entity_fields(filepath)
        lines.append(f"    class {class_name} {{")
        for ftype, fname in fields:
            lines.append(f"        {ftype} {fname}")
        lines.append("    }")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

def parse_controller_endpoints(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Caminho base da classe (@RequestMapping("/courses"))
    base_match = re.search(
        r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']', content
    )
    base_path = base_match.group(1) if base_match else ""

    # Mapeamentos de método (@GetMapping, @PostMapping, etc.)
    mapping_re = re.compile(
        r'@(Get|Post|Put|Patch|Delete)Mapping'
        r'(?:\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\'])?'
    )
    endpoints = []
    for match in mapping_re.finditer(content):
        method = match.group(1).upper()
        suffix = match.group(2) or ""
        endpoints.append((method, base_path + suffix))

    return endpoints


def build_endpoint_table():
    controller_files = find_java_files("**/*Controller.java")
    if not controller_files:
        return None

    rows = []
    for filepath in sorted(controller_files):
        rows.extend(parse_controller_endpoints(filepath))

    if not rows:
        return None

    lines = [
        "| Method | Path |",
        "|--------|------|",
    ]
    for method, path in rows:
        lines.append(f"| `{method}` | `{path}` |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers de escrita
# ---------------------------------------------------------------------------

def replace_section(content, start_marker, end_marker, new_body):
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{new_body}\n{end_marker}"
    updated = pattern.sub(replacement, content)
    if updated == content:
        print(f"[WARN] Marker '{start_marker}' not found in {DOCS_FILE}")
    return updated


def update_timestamp(content):
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return re.sub(
        r"> \*\*Last updated:\*\*.*",
        f"> **Last updated:** {date_str} by GitHub Actions",
        content,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(DOCS_FILE):
        print(f"[ERROR] {DOCS_FILE} not found. Run from the project root.")
        raise SystemExit(1)

    with open(DOCS_FILE, encoding="utf-8") as f:
        content = f.read()

    content = update_timestamp(content)

    class_diagram = build_class_diagram()
    if class_diagram:
        mermaid_block = f"```mermaid\n{class_diagram}\n```"
        content = replace_section(
            content,
            "<!-- AUTO_GENERATED_START -->",
            "<!-- AUTO_GENERATED_END -->",
            mermaid_block,
        )

    endpoint_table = build_endpoint_table()
    if endpoint_table:
        content = replace_section(
            content,
            "<!-- ENDPOINTS_START -->",
            "<!-- ENDPOINTS_END -->",
            endpoint_table,
        )

    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {DOCS_FILE} updated successfully.")


if __name__ == "__main__":
    main()