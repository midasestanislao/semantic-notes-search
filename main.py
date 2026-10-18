"""Semantic Notes Search — proyecto completo (4 etapas).

Etapa 1  normalize    texto          -> lista de tokens limpios
Etapa 2  build_index  {id: texto}    -> indice TF-IDF
Etapa 3  search       indice + query -> top-k resultados con coseno
Etapa 4  evaluate     indice + casos -> recall@k

Diseno: cada token cuenta  -> una vez por nota (df) multiplicado por
frecuencia local (tf) y ponderado por rareza (idf). Vectores de
longitud unidad para que el coseno sea solo un producto punto.
"""

import math
import re
import unicodedata


# ──────────────────── util ───────────────────────────────────────
def _norm(texto):
    """NFC + casefold: la forma canonica del texto para comparar."""
    return unicodedata.normalize("NFC", texto).casefold()


# ──────────────────── Etapa 1: normalize ─────────────────────────
def normalize(text, aliases=None):
    """Texto -> lista de tokens limpios.

    Embudo: NFC -> casefold -> regex de palabras -> aliases (una pasada).
    Devuelve LISTA (no set) para que las repeticiones lleven frecuencia.
    """
    if text is None:
        raise ValueError("text is required")
    text = _norm(text)
    palabras = re.findall(r"\w+", text)

    if not aliases:
        return palabras

    # Normalizar TANTO claves como valores de los aliases (una sola vez)
    norm_aliases = {_norm(k): _norm(v) for k, v in aliases.items()}
    return [norm_aliases.get(p, p) for p in palabras]


# ──────────────────── Etapa 2: build_index ───────────────────────
def build_index(documents, aliases=None):
    """{doc_id: texto} -> indice TF-IDF con vectores normalizados.

    Estructura del indice:
        {
            "idf":     {termino: idf_suavizado},
            "vectors": {doc_id: {termino: peso}},
            "norms":   {doc_id: norma_unidad (debe ser 1.0)}
        }
    """
    # Validar ids no vacios
    for doc_id in documents:
        if not doc_id:
            raise ValueError("document id must be non-empty")

    # Tokenizar cada documento (usando los aliases)
    tokenizados = {
        doc_id: normalize(texto, aliases)
        for doc_id, texto in documents.items()
    }

    # df = en cuantos documentos aparece cada termino (UNA vez por doc)
    df = {}
    for tokens in tokenizados.values():
        for termino in set(tokens):
            df[termino] = df.get(termino, 0) + 1

    # idf suavizado: log((1+N)/(1+df)) + 1
    n = len(documents)
    idf = {t: math.log((1 + n) / (1 + f)) + 1 for t, f in df.items()}

    # Vectores tf*idf, normalizados a longitud 1
    vectors = {}
    norms = {}
    for doc_id, tokens in tokenizados.items():
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        vec = {t: tf[t] * idf[t] for t in tf}
        norma = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        vec = {t: w / norma for t, w in vec.items()}
        vectors[doc_id] = vec
        norms[doc_id] = norma  # 1.0 despues de normalizar

    return {"idf": idf, "vectors": vectors, "norms": norms, "aliases": aliases or {}}


# ──────────────────── Etapa 3: search ────────────────────────────
def search(index, query, k=3):
    """Busca los k mejores documentos por similitud coseno.

    Coseno entre vectores unitarios = producto punto. Solo devolvemos
    matches con score > 0. Empates se rompen por doc_id (estable).
    """
    if k <= 0:
        raise ValueError("k must be positive")

    # Vector de la consulta con el MISMO idf del indice
    aliases = index.get("aliases") or {}
    norm_aliases = {_norm(k): _norm(v) for k, v in aliases.items()}
    palabras = re.findall(r"\w+", _norm(query))
    palabras = [norm_aliases.get(p, p) for p in palabras]
    tf = {}
    for p in palabras:
        tf[p] = tf.get(p, 0) + 1
    idf = index["idf"]
    qvec = {p: tf[p] * idf[p] for p in tf if p in idf}

    # Normalizar la consulta igual que los docs
    norma = math.sqrt(sum(w * w for w in qvec.values())) or 1.0
    qvec = {p: w / norma for p, w in qvec.items()}

    # Producto punto contra cada documento
    puntajes = []
    for doc_id, dvec in index["vectors"].items():
        score = sum(qvec[t] * dvec[t] for t in qvec if t in dvec)
        if score > 0:
            matched = sorted(set(qvec) & set(dvec))
            puntajes.append((score, doc_id, matched))

    # Orden estable: score DESC, luego doc_id ASC
    puntajes.sort(key=lambda x: (-x[0], x[1]))
    top = puntajes[:k]

    return [
        {"id": doc_id, "score": round(score, 6), "matched": matched}
        for score, doc_id, matched in top
    ]


# ──────────────────── Etapa 4: evaluate ──────────────────────────
def evaluate(index, cases, k=3):
    """Evalua recall@k con casos etiquetados.

    cases: lista de {"query": str, "expected": doc_id}.
    Devuelve: {"hits": int, "total": int, "recall": float}
    """
    # Validar etiquetas contra el indice
    ids_validos = set(index["vectors"].keys())
    for caso in cases:
        if caso["expected"] not in ids_validos:
            raise ValueError(f"label {caso['expected']!r} is not in the index")

    hits = 0
    for caso in cases:
        resultados = search(index, caso["query"], k)
        ids = [r["id"] for r in resultados]
        if caso["expected"] in ids:
            hits += 1
    total = len(cases)
    recall = hits / total if total else 0.0
    return {"hits": hits, "total": total, "recall": recall}
