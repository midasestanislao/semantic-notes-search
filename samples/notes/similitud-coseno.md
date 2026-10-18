# Similitud coseno

La similitud coseno compara la dirección de dos flechas ignorando su
tamaño. Va de -1 a 1: uno significa misma dirección, cero significa
perpendiculares, menos uno significa direcciones opuestas.

La fórmula es el producto punto dividido por el producto de las normas.
En IA se usa para comparar embeddings: lo que importa es el tema
(dirección), no la longitud del texto.
