# Prisoner-Dilemma

| **Nombre**              | **Grupo** | **Github**                                     |
|-------------------------|-----------|------------------------------------------------|
| Daniel Abad Fundora     | C411      | [@DanielAbadF](https://github.com/DanielAbadF) |
| Anabel Benítez González | C411      | [@anabel02](https://github.com/anabel02)       |
| Enzo Rojas D'Toste      | C411      | [@EnzoDtoste](https://github.com/EnzoDtoste)   |           

El reporte se encuentra en el archivo [report.pdf](https://github.com/nose-cs/Prisoner-Dilemma/blob/main/docs/report.pdf).

## ¿Cómo ejecutarlo?

Para ejecutar el proyecto necesita tener instalada la versión 3.10 de python o superior. Además para instalar los
paquetes necesarios ejecute el siguiente comando:

```bash
pip install -r requirements.txt
```

Para ejecutar el proyecto ejecute el siguiente comando:

```bash
python3 main.py
```

## ¿Cómo funciona?

El proyecto consiste en un torneo todos contra todos, donde cada juego tiene la misma secuencia de rondas. 
Cada ronda se juega con una matriz de decisión, donde se especifica la puntuación que se obtiene por cada combinación de
acciones de los jugadores, cada jugador tiene una estrategia que determina qué acción tomar en cada ronda.

En `main.py` se encuentra una configuración de torneo, si lo desea, ahí puede modificar el número de rondas (
especificando las matrices con que se quiere jugar), y los jugadores que se quieren añadir al torneo. 

En `simulation.ipynb` se da una explicación detallada de cómo crear torneos.