#!/usr/bin/env python3
"""
IronChain :: Guard
-------------------
Módulo de control de alcance y archivos para agentes de desarrollo IA.

Qué hace:
  1. Lee las políticas desde `ironchain.yaml` (protected_paths, secret_files).
  2. Obtiene la lista de archivos modificados (staged + unstaged) vía git.
  3. Compara cada archivo contra las políticas usando glob matching.
  4. Si hay una violación, imprime un reporte claro y sale con código != 0,
     bloqueando el commit / el paso de "finalizar cambios" del agente.

Diseño:
  - Sin dependencias pesadas: solo PyYAML (único requirement externo).
  - Falla "cerrado": si ironchain.yaml no existe o está mal formado, Guard
    bloquea por defecto en vez de dejar pasar silenciosamente.
  - Pensado para engancharse como:
      a) git hook (pre-commit)
      b) paso explícito en el flujo del agente antes de "done"
      c) step de CI/CD (ver .github/workflows/ironchain-guard.yml)

Uso:
  python modules/guard/guard.py
  python modules/guard/guard.py --config ironchain.yaml
  python modules/guard/guard.py --base-ref origin/main   # compara contra otra rama
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    print(
        "[ironchain:guard] ERROR: falta la dependencia 'pyyaml'.\n"
        "Instalala con: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_CONFIG_ERROR = 2


@dataclass
class GuardPolicy:
    protected_paths: list[str] = field(default_factory=list)
    secret_files: list[str] = field(default_factory=list)
    allow_override_env: str | None = None


def load_policy(config_path: str) -> GuardPolicy:
    if not os.path.isfile(config_path):
        print(
            f"[ironchain:guard] ERROR: no se encontró '{config_path}'.\n"
            "Guard falla 'cerrado' por seguridad: sin política, no hay pase.",
            file=sys.stderr,
        )
        sys.exit(EXIT_CONFIG_ERROR)

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            raw = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"[ironchain:guard] ERROR: ironchain.yaml inválido: {e}", file=sys.stderr)
            sys.exit(EXIT_CONFIG_ERROR)

    guard_cfg = raw.get("guard", {}) or {}
    return GuardPolicy(
        protected_paths=guard_cfg.get("protected_paths", []) or [],
        secret_files=guard_cfg.get("secret_files", []) or [],
        allow_override_env=guard_cfg.get("allow_override_env"),
    )


def get_changed_files(base_ref: str | None) -> list[str]:
    """Devuelve la lista de archivos modificados (staged + unstaged + untracked)."""
    cmds = []
    if base_ref:
        cmds.append(["git", "diff", "--name-only", base_ref])
    else:
        cmds.append(["git", "diff", "--name-only", "HEAD"])
        cmds.append(["git", "diff", "--name-only", "--cached"])
        cmds.append(["git", "ls-files", "--others", "--exclude-standard"])

    files: set[str] = set()
    for cmd in cmds:
        try:
            out = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            ).stdout
        except subprocess.CalledProcessError as e:
            print(f"[ironchain:guard] WARN: no se pudo ejecutar {' '.join(cmd)}: {e}", file=sys.stderr)
            continue
        for line in out.splitlines():
            line = line.strip()
            if line:
                files.add(line)
    return sorted(files)


def match_any(path: str, patterns: list[str]) -> str | None:
    """Devuelve el patrón que hizo match, o None."""
    normalized = path.replace(os.sep, "/")
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return pattern
        # soporte simple para "**": también probamos matcheo por segmento final
        if fnmatch.fnmatch(os.path.basename(normalized), pattern):
            return pattern
    return None


def evaluate(files: list[str], policy: GuardPolicy) -> list[tuple[str, str, str]]:
    """Retorna violaciones como (archivo, categoría, patrón)."""
    violations = []
    for file in files:
        secret_match = match_any(file, policy.secret_files)
        if secret_match:
            violations.append((file, "SECRET_FILE", secret_match))
            continue  # un archivo secreto no necesita chequeo adicional

        protected_match = match_any(file, policy.protected_paths)
        if protected_match:
            violations.append((file, "PROTECTED_PATH", protected_match))

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="IronChain Guard: control de alcance para agentes IA.")
    parser.add_argument("--config", default="ironchain.yaml", help="Ruta al archivo de política.")
    parser.add_argument("--base-ref", default=None, help="Ref de git contra el cual comparar (ej: origin/main).")
    args = parser.parse_args()

    policy = load_policy(args.config)
    changed_files = get_changed_files(args.base_ref)

    if not changed_files:
        print("[ironchain:guard] OK — no hay cambios para evaluar.")
        return EXIT_OK

    violations = evaluate(changed_files, policy)

    override_active = bool(
        policy.allow_override_env and os.environ.get(policy.allow_override_env)
    )

    if not violations:
        print(f"[ironchain:guard] OK — {len(changed_files)} archivo(s) evaluados, sin violaciones.")
        return EXIT_OK

    print("\n[ironchain:guard] ⛔ VIOLACIONES DE POLÍTICA DETECTADAS\n")
    for file, category, pattern in violations:
        print(f"  - [{category}] {file}  (regla: '{pattern}')")

    if override_active:
        print(
            f"\n[ironchain:guard] ⚠️  Override humano activo vía "
            f"${policy.allow_override_env}. Se permite el paso, pero queda auditado."
        )
        return EXIT_OK

    print(
        "\n[ironchain:guard] El agente no puede finalizar cambios sobre estos archivos.\n"
        "Si esto es intencional, un humano debe revisar y, de ser necesario,\n"
        f"exportar {policy.allow_override_env}=1 antes de reintentar.\n"
    )
    return EXIT_VIOLATION


if __name__ == "__main__":
    sys.exit(main())
