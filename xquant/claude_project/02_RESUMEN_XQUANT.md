# X-QUANT — resumen para el Proyecto de Claude

Foto a fecha **2026-10-08**. Fuente: memoria del laboratorio (`research_output/memory.db`) e informes en GitHub.
Ningún dato de este archivo es estimado: todo sale de ejecuciones registradas. Lo que no se ha medido se dice.

## 1. Qué es
Laboratorio de investigación cuantitativa en Python que busca ventajas estadísticas y, sobre todo, intenta destruirlas
antes de creérselas:
- Datos: velas de Dukascopy (minuto, hora), con control de calidad, alineación point-in-time y comparación con
  fuentes externas (Fed, Banco Mundial, DXY real).
- Búsqueda: miles de hipótesis y estrategias generadas (algoritmo genético con genealogía), corrección por pruebas
  múltiples (BH-FDR, Deflated Sharpe con N acumulado por familia de datos, PBO).
- Ataque: ~20 tests adversariales (costes x2/x3, retraso de entrada, dirección aleatoria, vecinos de parámetros,
  años sueltos, cambio de temporalidad...).
- Datos divididos en TRAIN / VALIDATION / TEST / FINAL con embargo. TEST y FINAL se abren UNA vez y queda registrado.
- Hipótesis dirigidas: pre-registro (especificación con huella SHA-256 en git) antes de mirar los datos.
- Laboratorio autónomo: cola de trabajos, workers, un "Director" que decide qué investigar, alertas y panel de control.

## 2. Resultado global
- **42 ejecuciones**: 39 NO EDGE FOUND, 1 EDGE FOUND (provisional), 1 abortada a propósito, 1 fallida (corregida).
- **963 estrategias** examinadas en búsqueda exploratoria: 878 rechazadas, 85 sobreajustadas. **60.799 hipótesis**.
- Probado y descartado: EUR/USD (diario, H1, H2, H4, D1), oro (H1 a M5), Nasdaq H1 y M30, GBP/USD H1, S&P 500 H1,
  sesiones, trailing + ensemble, valor relativo oro/plata y EUR/GBP, SMT/residuo DXY, VWAP semanal, momentum intradía
  (Gao et al.), volatility-managed, TSMOM, momentum FX cross-section, ML walk-forward (gradient boosting).
- Lista completa: `03_ejecuciones.csv`.

## 3. Única ventaja provisional: `nq_orb5_v2` (variante A)
Ruptura del rango de apertura de 5 minutos en el Nasdaq 100. Especificación completa: `05_nq_orb5_v2_spec.yaml.txt`.
Informe: `04_nq_orb5_v2_informe.md`.

**Reglas**
- Vela de 09:30–09:35 (hora de Nueva York). Si su cuerpo es >= 10 % de su rango: alcista -> largo; bajista -> corto.
  Doji (cuerpo < 10 %) -> no se opera.
- Entrada a mercado a las 09:35:00. Una operación al día como máximo.
- Stop: el extremo opuesto de esa vela. Objetivo: 10R. Si no toca ninguno, cierre a las 16:00 NY.
- Riesgo 1 % del capital por operación; nocional máximo 4x; límite de pérdida diaria 2 %.
- Sin filtro de noticias (no había calendario histórico fiable).

**Resultados (costes tipo futuro NQ incluidos)**

| Periodo | Operaciones | R medio neto | Rentabilidad anual al 1 % de riesgo |
|---|---|---|---|
| 2017–2022 (TRAIN + VALIDATION) | 1.357 (~228/año) | +0,145 (IC 95 % 0,03–0,26) | 27,2 % |
| TEST 2023 – jun 2024 | 340 | +0,025 | 2,25 % |
| FINAL jul 2024 – sep 2026 | 514 | +0,113 | 12,0 % |

2017–2022: aciertos 24,8 %, profit factor 1,19, Sharpe de los retornos diarios 0,97, **caída máxima 22,8 %**, 100 % de años positivos,
supera a la dirección aleatoria (p = 0,01).

**Debilidades medidas**
- Entrar 1 minuto tarde: +0,059R (pierde ~60 % de la ventaja). Costes x2: +0,096R; x3: +0,047R.
- El 5 % mejor de las operaciones aporta el 284 % del beneficio: el otro 95 % pierde en conjunto. Rachas perdedoras largas.
- TEST muy flojo (+0,025R).
- Réplica en S&P 500 (`spx_orb5_replication_v1`, RUN-00039): NO confirma.
- Datos de minuto del Nasdaq 2023-07 -> 2026-09 ya "quemados" (TEST/FINAL abiertos): no sirven para validar cambios.

**Frente a mis objetivos**
- Meta 1–2 % diario: la estrategia da de media ~0,11–0,15 % por día operado al 1 % de riesgo: ~10 veces menos.
- Fondeo: la caída máxima histórica (22,8 % al 1 % de riesgo) es más del doble del límite de pérdida total
  del 10 % que citan reseñas de FTMO. Sin simular con las reglas exactas de una firma no se puede decir si pasa ni con qué tamaño.

## 4. Pendiente
1. **Validación independiente en MT5** (demo Dukascopy o prueba gratuita de FTMO): EA `06_EA_...mq5.txt`, instrucciones
   en `07_EA_README.md`. Comparar con el FINAL del laboratorio (jul 2024 – hoy): ~225 operaciones/año, ~25 % aciertos.
   Parámetro crítico: `InpServerMinusNY` (hora servidor − hora NY). El EA no se ha compilado aún.
2. **Simulador de challenge de fondeo**: necesita las reglas exactas de la firma y plan elegidos (objetivo, pérdida
   diaria, tipo de drawdown, días mínimos, plazo, consistencia, cuota, reparto). Comparará con dirección aleatoria.
3. Para capital propio: definir caída máxima tolerable y capital inicial.
4. Almacenamiento persistente del laboratorio (bucket de Google Cloud a medio crear, o mover el laboratorio al PC).
5. Mi estrategia discrecional (order flow NQ M5: perfil compuesto, VWAP, volume profile, delta, footprint) NO está
   testeada en el laboratorio: no hay datos de order flow (delta/footprint) históricos en el laboratorio.
