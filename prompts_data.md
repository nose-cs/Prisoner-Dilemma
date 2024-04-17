### Prompts

Necesito llevar las secciones ### Matrix n a una lista en formato json, cada elemento tiene la forma
{"title": ..., "matrix": ..., "actions": ..., "story": ...},
donde actions es una lista de strings con las acciones disponibles, matrix es una lista de lista de lista de 2
elementos de tipo int que representa la matriz, y story es el cuento, además necesito un título que describa el cuento
y guardarlo en title. Necesito que el titulo sea único para cada matriz.

Cuando le pasé el contenido de ``src/llm/processed_response`` deliro un poco y me dio un "solucion en python" y otra vez
una explicacion filosofica de como debia hacerlo. Lo pique en 8 y funciono, luego 8 mas.

Para los ultimos 4 utilice el siguiente prompt:

Necesito llevar las secciones ### Matrix n a una lista en formato json, cada elemento tiene la forma
{"title": ..., "matrix": ..., "actions": ..., "story": ...},
donde actions es una lista de strings con las acciones disponibles, matrix es una lista de lista de lista de 2
elementos de tipo int que representa la matriz, y story es el cuento, además necesito un título que describa el cuento
y guardarlo en title. Necesito que el titulo sea único para cada matriz. Debes cambiar los
D1, ..., Dn, por sus respectivos textos en actions. Debes cambiar Estrategia A, Estrategia B, ... por sus respectivos
textos en actions.