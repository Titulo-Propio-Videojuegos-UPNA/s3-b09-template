#!/usr/bin/env bash
# Sincronizador de Etiquetas de Paracaídas (s3-b09-template)
# Uso: ./scripts/sync_checkpoint.sh s3-19-start
set -euo pipefail

TAG="${1:-}"
if [[ -z "$TAG" ]]; then
  echo "Uso: ./scripts/sync_checkpoint.sh <tag> (ej. s3-19-start)"
  exit 1
fi

UPNA_TEMPLATE_REMOTE="${UPNA_TEMPLATE_REMOTE:-https://github.com/Titulo-Propio-Videojuegos-UPNA/s3-b09-template.git}"

git fetch origin --tags --force 2>/dev/null || true
git remote get-url upstream >/dev/null 2>&1 || git remote add upstream "$UPNA_TEMPLATE_REMOTE"
git fetch upstream --tags --force 2>/dev/null || true

if ! git rev-parse --verify "refs/tags/$TAG" >/dev/null 2>&1; then
  echo "[ERROR] No se encontró la etiqueta $TAG en el repositorio ni en upstream ($UPNA_TEMPLATE_REMOTE)."
  exit 2
fi

TS="$(date +%Y%m%d-%H%M%S)"
git branch "backup-before-${TAG}-${TS}" 2>/dev/null || true
git stash push -u -m "auto-stash before ${TAG} (${TS})" >/dev/null 2>&1 || true
git checkout -B "sesion-${TAG}" "tags/${TAG}"
echo "[OK] Proyecto situado en el punto de control ${TAG} (rama sesion-${TAG})."
echo "     Tu avance previo ha quedado respaldado en backup-before-${TAG}-${TS}."
