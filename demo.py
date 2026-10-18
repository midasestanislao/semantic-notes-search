"""Demo del proyecto Semantic Notes Search sobre notas de muestra locales.

  conda activate AIagent
  python demo.py

Usa samples/notes (notas propias de algebra lineal en español) y los
aliases de samples/aliases.json.
"""

import json
from pathlib import Path

from main import build_index, evaluate, search

RAIZ = Path(__file__).resolve().parent / "samples"
NOTAS = RAIZ / "notes"
ALIASES = json.loads((RAIZ / "aliases.json").read_text(encoding="utf-8"))


def cargar():
    return {
        str(p.relative_to(NOTAS)): p.read_text(encoding="utf-8")
        for p in sorted(NOTAS.rglob("*.md"))
    }


def main():
    documentos = cargar()
    print(f"Cargadas {len(documentos)} notas de {NOTAS}\n")

    indice = build_index(documentos, ALIASES)
    print(f"Vocabulario: {len(indice['idf'])} terminos unicos\n")

    # Busquedas de ejemplo
    for q in ["embeddings de palabras", "producto punto direccion", "transforma flecha"]:
        print(f">>> Consulta: {q!r} (con aliases)")
        filas = search(indice, q, k=2)
        if not filas:
            print("  (sin coincidencias: el token no esta en el vocabulario)")
        for r in filas:
            preview = documentos[r["id"]][:70].replace("\n", " ")
            print(f"  {r['id']:22s}  score={r['score']:.4f}  match={r['matched']}")
            print(f"  {' ' * 22}  {preview}...")
        print()

    # Evaluacion con casos etiquetados (recall@k)
    casos = [
        {"query": "flecha direccion", "expected": "similitud-coseno.md"},
        {"query": "tabla de numeros", "expected": "matriz.md"},
        {"query": "palabra perro 768", "expected": "vector.md"},
        {"query": "tema inexistente", "expected": "vector.md"},
    ]
    metricas = evaluate(indice, casos, k=1)
    print(
        f"Recall@1: {metricas['hits']}/{metricas['total']} = {metricas['recall']:.0%}"
        "  (2 fallan a proposito: 'tema inexistente' no esta en el vocabulario"
        " y 'numeros' no encuentra 'números' porque no hay plegado de tildes)"
    )


if __name__ == "__main__":
    main()
