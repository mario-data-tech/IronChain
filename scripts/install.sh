#!/usr/bin/env bash
# IronChain :: install.sh
# Instala Guard como git hook pre-commit en el repo actual.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[ironchain] ERROR: este directorio no es un repositorio git." >&2
  exit 1
}

HOOK_PATH="$REPO_ROOT/.git/hooks/pre-commit"

cat > "$HOOK_PATH" <<'EOF'
#!/usr/bin/env bash
# Auto-generado por IronChain. No editar a mano; correr scripts/install.sh de nuevo.
python3 modules/guard/guard.py
exit $?
EOF

chmod +x "$HOOK_PATH"

echo "[ironchain] Guard instalado como pre-commit hook en $HOOK_PATH"
echo "[ironchain] Probalo con: git commit --allow-empty -m 'test'"
