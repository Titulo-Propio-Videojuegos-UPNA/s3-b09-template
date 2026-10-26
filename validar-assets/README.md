# Validador del kit de assets (3.4.2 y pendiente 17)

`validate_assets.py` es un script de Python que solo usa la biblioteca estándar. Se ejecuta en la **CI de cada repo** y aplica las reglas de licencia y de calidad del kit (ver [`planes/2026-10-15_P3_pendiente-17_kit-assets-licencias.md`](../../../planes/2026-10-15_P3_pendiente-17_kit-assets-licencias.md)). **Complementa**, sin sustituirlo, al validador dentro de Unreal de 3.4.2 (Python del editor, «Asset Validation» en el curso de Kowalczyk).

| Regla | Qué comprueba | Nivel |
|---|---|---|
| L1 | Cada pack de `assets/` está declarado en `assets/manifest.json` (fuente, licencia, redistribuible) | error |
| L2 | Los packs **no redistribuibles** (por ejemplo, Quaternius QAL) están en `assets/third_party/`, y esa ruta está en `.gitignore` | error |
| L3 | Los packs declarados redistribuibles incluyen un fichero de licencia | error |
| N1 | Nombres de fichero en ASCII y sin espacios | aviso |
| T1 | PNG con lado ≤ `--max-texture` (error); lado potencia de dos (aviso, o error con `--strict-pot`) | error / aviso |
| M1 | OBJ con triángulos ≤ `--max-tris` | error |

```text
python validate_assets.py <raíz_del_repo> [--max-texture 2048] [--max-tris 20000] [--strict-pot]
```

Formato de `assets/manifest.json`:

```json
{"packs": [
  {"path": "physics", "source": "https://kenney.nl/assets/physics-assets", "license": "CC0", "redistributable": true},
  {"path": "third_party/personaje_qal", "source": "https://quaternius.com", "license": "Quaternius Asset License v1.0", "redistributable": false}
]}
```

## Probado el 15-oct-2026

Repo de prueba con dos packs reales de Kenney (`physics-assets` y `pixel-shmup`; su `License.txt` dice CC0) y un pack ficticio en `third_party/`.

| Caso | Resultado |
|---|---|
| `third_party/` sin `.gitignore` | `ERROR L2`, salida 1 |
| Con `.gitignore` | 0 errores, salida 0 (495 PNG revisados) |
| Pack nuevo sin declarar | `ERROR L1`, salida 1 |
| Pack declarado redistribuible sin licencia | `ERROR L3`, salida 1 |
| `--strict-pot` | 336 errores |

**Hallazgo para el kit 2D:** los sprites sueltos de Kenney **no tienen lado potencia de dos** (por ejemplo, 70×70). En raylib (S1) no importa; para Unreal y GPU (S2–S3) conviene usar **hojas de sprites o atlas** (los packs traen la carpeta `Spritesheet`) y activar `--strict-pot` solo en los packs 3D. Los nombres con espacios de Kenney (`Tilesheet (Ships).txt`) salen como avisos N1: se renombran al preparar el lote.
