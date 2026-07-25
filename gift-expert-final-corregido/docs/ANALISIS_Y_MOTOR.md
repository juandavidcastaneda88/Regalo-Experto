# Análisis del problema y motor de inferencia

## Problema
Escoger un regalo puede ser difícil porque deben combinarse gustos, edad, relación, ocasión, personalidad, presupuesto, plazo y restricciones. Gift Expert convierte estos datos en hechos y los compara con una base de conocimiento.

## Variables de entrada
- Edad.
- Relación con la persona.
- Ocasión.
- Urgencia o plazo.
- Intereses.
- Personalidad.
- Tipo de regalo preferido.
- Presupuesto máximo.
- Restricciones.

## Hechos
Los hechos son las respuestas validadas y normalizadas por `modelos.py`.

## Base de conocimiento
- `regalos.json`: alternativas y atributos.
- `reglas.json`: reglas, operadores y pesos.
- `ocasiones.json`: ocasiones disponibles.
- `intereses.json`: intereses disponibles.
- `configuracion.json`: relaciones, personalidades, tipos, restricciones y límites.

## Método de razonamiento
Encadenamiento hacia adelante:
1. Recibe hechos.
2. Descarta incompatibilidades duras.
3. Evalúa todas las reglas para cada regalo.
4. Suma puntos ponderados.
5. Convierte el resultado en porcentaje.
6. Resuelve conflictos y ordena las alternativas.
7. Explica las reglas activadas.

## Resolución de conflictos
1. Mayor porcentaje de afinidad.
2. Mayor cantidad de coincidencias.
3. Mejor cercanía a un uso razonable del presupuesto.
4. Menor precio.
5. Orden alfabético como último desempate estable.

## Modelo de puntuación
Los pesos se encuentran en `reglas.json` y pueden editarse sin tocar Python. La coincidencia de intereses es proporcional al número de intereses comunes. El presupuesto y la urgencia también aportan puntos. Un regalo que excede el presupuesto o contradice una restricción es descartado antes de puntuar.

## Ética
El sistema no solicita ni almacena género. Ninguna regla incluye género, por lo que las recomendaciones se basan únicamente en preferencias y contexto relevante.
