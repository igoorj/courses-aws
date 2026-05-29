#!/usr/bin/env python3
"""
Atualiza as seções auto-geradas de docs/architecture.md:
  - API Flows   : sequence diagrams gerados a partir dos controllers Spring
  - Data Model  : classDiagram extraído das entidades JPA
  - API Endpoints: tabela extraída dos controllers Spring
  - Timestamp   : data/hora UTC da última atualização
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
# Controllers — parsing compartilhado
# ---------------------------------------------------------------------------

def parse_controller_methods(filepath):
    """
    Varre o arquivo linha a linha e retorna uma lista de dicts:
      http_method, path, service_method, returns_created, returns_no_content
    """
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    content = "".join(lines)

    base_match = re.search(
        r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']', content
    )
    base_path = base_match.group(1) if base_match else ""

    results = []
    for i, line in enumerate(lines):
        m = re.search(
            r'@(Get|Post|Put|Patch|Delete)Mapping'
            r'(?:\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\'])?',
            line,
        )
        if not m:
            continue

        http_method = m.group(1).upper()
        path_suffix = m.group(2) or ""

        service_method = None
        returns_created = False
        returns_no_content = False

        # Varre as próximas 20 linhas para extrair info do corpo do método
        for body_line in lines[i : i + 20]:
            if not service_method:
                svc = re.search(r'\w+[Ss]ervice\.(\w+)\(', body_line)
                if svc:
                    service_method = svc.group(1)
            if "ResponseEntity.created" in body_line or "HttpStatus.CREATED" in body_line:
                returns_created = True
            if "noContent" in body_line or "NO_CONTENT" in body_line:
                returns_no_content = True

        results.append(
            {
                "http_method": http_method,
                "path": base_path + path_suffix,
                "service_method": service_method,  # None = controller responde direto, sem service
                "returns_created": returns_created,
                "returns_no_content": returns_no_content,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Sequence Diagrams
# ---------------------------------------------------------------------------

def _participants(ctrl, svc, repo):
    return (
        f"    autonumber\n"
        f"    participant C as Client\n"
        f"    participant Ctrl as {ctrl}\n"
        f"    participant Svc as {svc}\n"
        f"    participant Repo as {repo}\n"
        f"    participant DB as PostgreSQL"
    )


def _diagram(participants, body):
    return f"sequenceDiagram\n{participants}\n\n{body}"


def _simple_diagram(ctrl, http, path, returns_no_content):
    response = "204 No Content" if returns_no_content else "200 OK"
    return (
        f"sequenceDiagram\n"
        f"    autonumber\n"
        f"    participant C as Client\n"
        f"    participant Ctrl as {ctrl}\n\n"
        f"    C->>Ctrl: {http} {path}\n"
        f"    Ctrl-->>C: {response}"
    )


def generate_sequence_diagram(ep, ctrl, svc, repo, entity, table):
    http = ep["http_method"]
    path = ep["path"]
    svc_method = ep["service_method"]
    has_id = "{id}" in path

    # Método sem chamada de service → diagrama simplificado
    if svc_method is None:
        return _simple_diagram(ctrl, http, path, ep["returns_no_content"])

    p = _participants(ctrl, svc, repo)

    if http == "GET" and not has_id:
        body = (
            f"    C->>Ctrl: GET {path}\n"
            f"    Ctrl->>Svc: {svc_method}()\n"
            f"    Svc->>Repo: findAll()\n"
            f"    Repo->>DB: SELECT * FROM {table}\n"
            f"    DB-->>Repo: result set\n"
            f"    Repo-->>Svc: List<{entity}>\n"
            f"    Svc-->>Ctrl: List<{entity}>\n"
            f"    Ctrl-->>C: 200 OK · JSON array"
        )

    elif http == "GET" and has_id:
        body = (
            f"    C->>Ctrl: GET {path}\n"
            f"    Ctrl->>Svc: {svc_method}(id)\n"
            f"    Svc->>Repo: findById(id)\n"
            f"    Repo->>DB: SELECT * FROM {table} WHERE id = ?\n"
            f"    DB-->>Repo: result\n\n"
            f"    alt {entity.lower()} encontrado\n"
            f"        Repo-->>Svc: Optional[{entity}]\n"
            f"        Svc-->>Ctrl: {entity}\n"
            f"        Ctrl-->>C: 200 OK · {entity} JSON\n"
            f"    else não encontrado\n"
            f"        Repo-->>Svc: Optional.empty()\n"
            f"        Svc-->>Ctrl: ResponseStatusException(404)\n"
            f"        Ctrl-->>C: 404 Not Found\n"
            f"    end"
        )

    elif http == "POST":
        body = (
            f"    C->>Ctrl: POST {path} {{...}}\n"
            f"    Ctrl->>Svc: {svc_method}(request)\n"
            f"    Svc->>Svc: instancia {entity}\n"
            f"    Svc->>Repo: save({entity.lower()})\n"
            f"    Repo->>DB: INSERT INTO {table}\n"
            f"    DB-->>Repo: linha persistida com id gerado\n"
            f"    Repo-->>Svc: {entity}\n"
            f"    Svc-->>Ctrl: {entity}\n"
            f"    Ctrl-->>C: 201 Created · Location: {path}/{{id}}"
        )

    elif http in ("PUT", "PATCH") and has_id:
        body = (
            f"    C->>Ctrl: {http} {path} {{...}}\n"
            f"    Ctrl->>Svc: {svc_method}(id, request)\n"
            f"    Svc->>Repo: findById(id)\n"
            f"    Repo->>DB: SELECT * FROM {table} WHERE id = ?\n"
            f"    DB-->>Repo: result\n\n"
            f"    alt {entity.lower()} encontrado\n"
            f"        Repo-->>Svc: Optional[{entity}]\n"
            f"        Svc->>Svc: aplica alterações\n"
            f"        Svc->>Repo: save({entity.lower()})\n"
            f"        Repo->>DB: UPDATE {table} SET ...\n"
            f"        DB-->>Repo: linha atualizada\n"
            f"        Repo-->>Svc: {entity}\n"
            f"        Svc-->>Ctrl: {entity}\n"
            f"        Ctrl-->>C: 200 OK · {entity} JSON atualizado\n"
            f"    else não encontrado\n"
            f"        Repo-->>Svc: Optional.empty()\n"
            f"        Svc-->>Ctrl: ResponseStatusException(404)\n"
            f"        Ctrl-->>C: 404 Not Found\n"
            f"    end"
        )

    elif http == "DELETE" and has_id:
        body = (
            f"    C->>Ctrl: DELETE {path}\n"
            f"    Ctrl->>Svc: {svc_method}(id)\n"
            f"    Svc->>Repo: findById(id)\n"
            f"    Repo->>DB: SELECT * FROM {table} WHERE id = ?\n"
            f"    DB-->>Repo: result\n\n"
            f"    alt {entity.lower()} encontrado\n"
            f"        Repo-->>Svc: Optional[{entity}]\n"
            f"        Svc->>Repo: deleteById(id)\n"
            f"        Repo->>DB: DELETE FROM {table} WHERE id = ?\n"
            f"        DB-->>Repo: ok\n"
            f"        Svc-->>Ctrl: void\n"
            f"        Ctrl-->>C: 204 No Content\n"
            f"    else não encontrado\n"
            f"        Repo-->>Svc: Optional.empty()\n"
            f"        Svc-->>Ctrl: ResponseStatusException(404)\n"
            f"        Ctrl-->>C: 404 Not Found\n"
            f"    end"
        )

    else:
        return None

    return _diagram(p, body)


def build_sequence_diagrams():
    controller_files = find_java_files("**/*Controller.java")
    if not controller_files:
        return None

    sections = []
    for filepath in sorted(controller_files):
        entity = os.path.basename(filepath).replace(".java", "").replace("Controller", "")
        ctrl = os.path.basename(filepath).replace(".java", "")
        svc = f"{entity}Service"
        repo = f"{entity}Repository"
        table = entity.lower() + "s"

        for ep in parse_controller_methods(filepath):
            diagram = generate_sequence_diagram(ep, ctrl, svc, repo, entity, table)
            if diagram:
                label = f"### {ep['http_method']} {ep['path']}"
                sections.append(f"{label}\n\n```mermaid\n{diagram}\n```")

    return "\n\n".join(sections) if sections else None


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

def parse_entity_fields(filepath):
    fields = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(r"^\s*private\s+([\w<>\[\], ]+?)\s+(\w+)\s*;", re.MULTILINE)
    for match in pattern.finditer(content):
        fields.append((match.group(1).strip(), match.group(2).strip()))
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
# Endpoint Table
# ---------------------------------------------------------------------------

def build_endpoint_table():
    controller_files = find_java_files("**/*Controller.java")
    if not controller_files:
        return None
    rows = []
    for filepath in sorted(controller_files):
        for ep in parse_controller_methods(filepath):
            rows.append((ep["http_method"], ep["path"]))
    if not rows:
        return None
    lines = ["| Method | Path |", "|--------|------|"]
    for method, path in rows:
        lines.append(f"| `{method}` | `{path}` |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
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

    flows = build_sequence_diagrams()
    if flows:
        content = replace_section(content, "<!-- FLOWS_START -->", "<!-- FLOWS_END -->", flows)

    class_diagram = build_class_diagram()
    if class_diagram:
        content = replace_section(
            content,
            "<!-- AUTO_GENERATED_START -->",
            "<!-- AUTO_GENERATED_END -->",
            f"```mermaid\n{class_diagram}\n```",
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