# 🔍 Semantic Notes Search

**Buscador semántico de notas en Markdown construido desde cero** — sin
frameworks, sin servicios externos, sin modelos hospedados. Solo Python
estándar y matemáticas explicables.

> Proyecto del curso [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch).

**Español** | [English](README.en.md)

## ¿Qué hace?

Le das una carpeta de notas `.md` y una pregunta en lenguaje natural, y te
devuelve **qué nota responde mejor y por qué**:

```bash
python cli.py samples/notes "producto punto direccion" --aliases samples/aliases.json
```

```json
{
  "query": "producto punto direccion",
  "documents": 3,
  "matches": [
    {"id": "similitud-coseno.md", "score": 0.5123, "matched": ["producto", "punto", "direccion"], "preview": "..."}
  ]
}
```

Cada resultado es **explicable**: ves los tokens que coincidieron y el score
exacto. No hay caja negra.

## El motor en 4 piezas

| Función | Qué hace | Concepto de fondo |
|---|---|---|
| `normalize()` | texto → tokens limpios | NFC Unicode, case folding, regex `\w+`, expansión de sinónimos controlada |
| `build_index()` | tokens → índice TF-IDF | IDF suavizado `log((1+N)/(1+df)) + 1`, vectores normalizados a longitud 1 |
| `search()` | consulta → ranking top-k | **similitud coseno** (= producto punto entre vectores unitarios), desempate estable por id |
| `evaluate()` | ranking → métrica | recall@k sobre casos etiquetados |

```
notas .md ──normalize──► tokens ──build_index──► vectores TF-IDF
                                                      │
consulta ──normalize──► vector ──────search (coseno)──► top-k con explicación
                                                      │
casos etiquetados ────────────────evaluate (recall@k)─┘
```

## Decisiones de diseño (lo interesante)

- **NFC antes del regex.** La tilde combinante `\u0301` no es `\w`: si
  tokenizas antes de normalizar, `"café"` escrito en NFD pierde la tilde
  para siempre. El orden importa.
- **Aliases en una sola pasada, sin ciclos.** `{a: b, b: a}` no entra en
  bucle porque cada token se sustituye una vez.
- **df cuenta documentos, no repeticiones.** Repetir "orchard" diez veces
  en una nota no la hace aparecer en diez documentos.
- **Vectores de longitud 1.** Así el coseno se reduce a un producto punto
  y una nota larga no gana por repetir palabras.
- **La consulta usa el IDF del índice, nunca el suyo propio.** Recalcular
  pesos por consulta cambiaría el sistema de coordenadas y rompería la
  comparación coseno.
- **Lista vacía antes que ruido.** Score ≤ 0 no se devuelve: es más honesto
  decir "no encontré nada" que rellenar con coincidencias cero.
- **Ranking determinista.** Empates por score se rompen por `id`
  alfabético → tests y demos reproducibles.

## Correr el proyecto

```bash
# Requisitos: Python 3.10+ (solo stdlib)
python demo.py                      # recorrido completo con notas de muestra
python -m unittest discover tests   # suite de tests incluida
python cli.py <carpeta> "<consulta>" --k 3 --aliases samples/aliases.json
```

## Qué NO es (honestidad técnica)

- **No es un modelo de embeddings.** Es un baseline léxico TF-IDF con
  sinónimos explícitos: `replicas` no encuentra `replica` (no hay stemming),
  `numeros` no encuentra `números` (no hay plegado de tildes), y
  "el despliegue" no encuentra "release" a menos que lo declares en el
  archivo de aliases.
- **Un recall perfecto en el fixture no prueba calidad general.** Antes de
  saltar a embeddings, lo correcto es medir este baseline contra 30-50
  consultas reales etiquetadas.

## Créditos

Estructura del proyecto, etapas y tests originales de
[rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch)
(MIT License, © 2026 Rohit Ghumare). La implementación de `main.py`, las
notas de muestra y este README son trabajo propio del alumno.
