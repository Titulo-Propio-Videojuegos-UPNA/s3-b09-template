#!/usr/bin/env python3
"""Validador del kit de assets (Plan Definitivo 2026-10-25: B09.1; legado P4: B08.1). Pensado para ejecutarse en la CI de cada repo.

Comprueba:
  L1  cada pack de assets/ esta declarado en assets/manifest.json (fuente, licencia, redistribuible)
  L2  los packs NO redistribuibles estan bajo assets/third_party/ (que debe estar en .gitignore)
  L3  cada pack declarado redistribuible incluye un fichero de licencia
  N1  nombres de fichero: ASCII, sin espacios
  T1  texturas PNG: lado <= max_texture (error) y potencia de dos (aviso, o error con --strict-pot)
  M1  mallas OBJ: triangulos <= max_tris
Uso: python validate_assets.py <raiz_del_repo> [--max-texture 2048] [--max-tris 20000] [--strict-pot]
Salida: informe en texto y codigo 0 (sin errores) o 1 (errores). Solo usa la biblioteca estandar;
si Pillow esta instalado lo usa, si no lee la cabecera PNG a mano.
"""
import argparse
import json
import struct
import sys
from pathlib import Path

LICENSE_NAMES = {"license.txt", "license.md", "license", "licence.txt", "copying"}


def png_size(path: Path):
    with path.open("rb") as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def obj_triangles(path: Path) -> int:
    tris = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("f "):
                n = len(line.split()) - 1
                tris += max(0, n - 2)  # un poligono de n vertices = n-2 triangulos
    return tris


def is_pot(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--max-texture", type=int, default=2048)
    ap.add_argument("--max-tris", type=int, default=20000)
    ap.add_argument("--strict-pot", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    assets = root / "assets"
    errors, warnings = [], []

    manifest_path = assets / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR L1: falta {manifest_path}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared = {p["path"]: p for p in manifest["packs"]}

    # L1: cada carpeta de primer nivel (y cada una dentro de third_party) debe estar declarada
    packs = [d for d in assets.iterdir() if d.is_dir() and d.name != "third_party"]
    tp = assets / "third_party"
    if tp.exists():
        packs += [d for d in tp.iterdir() if d.is_dir()]
    for d in packs:
        rel = d.relative_to(assets).as_posix()
        if rel not in declared:
            errors.append(f"L1 pack sin declarar en manifest.json: {rel}")
            continue
        info = declared[rel]
        # L2: no redistribuible -> solo en third_party
        if not info.get("redistributable", False) and not rel.startswith("third_party/"):
            errors.append(f"L2 '{rel}' ({info.get('license')}) no es redistribuible y no esta en assets/third_party/")
        # L3: redistribuible -> licencia incluida
        if info.get("redistributable", False):
            if not any(p.name.lower() in LICENSE_NAMES for p in d.rglob("*") if p.is_file()):
                errors.append(f"L3 '{rel}' declarado redistribuible pero sin fichero de licencia")
    if tp.exists():
        gi = (root / ".gitignore").read_text(encoding="utf-8") if (root / ".gitignore").exists() else ""
        if "assets/third_party" not in gi:
            errors.append("L2 assets/third_party/ existe pero no esta en .gitignore")

    n_png = n_obj = 0
    for p in assets.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if " " in p.name or not p.name.isascii():
            warnings.append(f"N1 nombre con espacios o no ASCII: {rel}")
        if p.suffix.lower() == ".png":
            n_png += 1
            size = png_size(p)
            if size is None:
                errors.append(f"T1 PNG ilegible: {rel}")
                continue
            w, h = size
            if max(w, h) > a.max_texture:
                errors.append(f"T1 textura {w}x{h} > {a.max_texture}: {rel}")
            if not (is_pot(w) and is_pot(h)):
                (errors if a.strict_pot else warnings).append(f"T1 textura no potencia de dos {w}x{h}: {rel}")
        elif p.suffix.lower() == ".obj":
            n_obj += 1
            t = obj_triangles(p)
            if t > a.max_tris:
                errors.append(f"M1 malla con {t} triangulos > {a.max_tris}: {rel}")

    print(f"packs={len(packs)} png={n_png} obj={n_obj} errores={len(errors)} avisos={len(warnings)}")
    for e in errors:
        print("ERROR", e)
    for w in warnings[:20]:
        print("AVISO", w)
    if len(warnings) > 20:
        print(f"AVISO ... y {len(warnings) - 20} avisos mas")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
