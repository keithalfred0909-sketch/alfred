# X-QUANT — Autonomous Market & Macro Strategy Discovery System

Laboratorio de investigación cuantitativa. Estudia el comportamiento histórico de un activo, genera
hipótesis estadísticas, construye estrategias a partir de ellas, intenta destruirlas y conserva solo las
que sobreviven. **Puede concluir — y lo hace a menudo — `NO EDGE FOUND`.**

> Solo investigación, backtest y análisis. No ejecuta órdenes, no conecta brokers. Nada de lo que produce
> es recomendación de inversión.

## Uso rápido

```bash
cd xquant
uv sync
uv run xquant data validate --asset EURUSD --offline       # carga + informe de calidad
uv run xquant research --asset EURUSD --mode standard --offline
uv run xquant dashboard --serve                            # http://127.0.0.1:8765 (auto-refresh)
uv run xquant memory strategies --limit 10
uv run pytest -q                                           # ~70 s (incluye controles end-to-end)
```

Modos (`configs/default.yaml` → `budgets`): `quick` (minutos), `standard` (≤90 min), `deep` (≤12 h,
poblaciones y generaciones grandes, paciencia alta). Todos los límites son configurables:
`max_experiments`, `max_generations`, `population`, `max_compute_minutes`, `max_strategies`,
`max_complexity`, `max_features`, `max_hypotheses`, `patience`, `max_line_failures`.

`--offline` fija los datos a los snapshots de `datasets/` (con hash y procedencia en `*.meta.json`) para
que una investigación sea exactamente reproducible. Sin `--offline` se descargan de nuevo y, si cambian,
cambia la versión del dataset (y la memoria reabre las hipótesis afectadas).

## Datos intradía (EUR/USD H1)

```bash
uv run xquant data validate --asset EURUSD_H1     # descarga Dukascopy + validación cruzada vs Fed
uv run xquant research --asset EURUSD_H1 --mode standard
```

- **Fuente:** velas horarias BID y ASK de Dukascopy (un fichero por mes, descarga en paralelo, caché en
  `cache/`). Barras a precio medio, sellado al cierre, spread observado por barra y volumen de ticks.
  Requiere `datafeed.dukascopy.com` en los dominios permitidos del entorno.
- **Comprobaciones antes de investigar:** consistencia OHLC (detecta un orden de campos mal interpretado),
  escala de precio, `ask >= bid`, y **validación cruzada contra el fixing de la Fed**: la vela que cierra a
  las 12:00 de Nueva York debe coincidir con el fixing (mediana ≤ 10 bps, correlación de retornos ≥ 0,9) y
  ningún reloj desplazado ±1 h puede encajar mejor. Si algo falla, la investigación no arranca.
- **Costes:** por cada fill se cobra el mayor entre el spread configurado y el observado en la barra.
- **Alternativa con tu broker:** exporta las barras H1 desde MetaTrader 5 (Ver → Símbolos → Barras →
  Exportar) a `datasets/eurusd_mt5_h1.csv` y usa `--asset EURUSD_MT5_H1`. Ajusta `server_tz` a la hora
  del servidor (`nyclose` = UTC+2 invierno / UTC+3 verano es lo habitual); la validación cruzada detecta
  si está mal.

## Cambiar de activo

Solo hace falta un fichero en `configs/assets/`. El núcleo no cambia:

```bash
uv run xquant research --asset BTCUSD     # plantilla: OHLCV en CSV (datasets/btcusd_1h.csv)
uv run xquant research --asset XAUUSD     # plantilla: Dukascopy (requiere red hacia datafeed.dukascopy.com)
```

## Arquitectura

```
src/xquant/
  data/            DATA ENGINE: fuentes (HTTP CSV, CSV, Dukascopy bi5, FRED, calendario, noticias),
                   limpieza auditada, esquema canónico, alineación point-in-time
  market/          MARKET BEHAVIOR ENGINE + descubrimiento de regímenes (GMM + BIC, solo TRAIN)
  macro/           MACRO INTELLIGENCE (estado macro, event studies) + EXPECTATION ENGINE (sorpresas PIT)
  news/            NEWS INTELLIGENCE (clasificador enchufable + event study)
  features/        FEATURE DISCOVERY (primitivas causales, gramática, IC + FDR + holdout interno)
  hypothesis/      HYPOTHESIS ENGINE (DISCOVERED→TESTING→VALIDATION→ROBUST | REJECTED | OVERFIT | DEAD)
  strategy/        STRATEGY GENERATOR (genoma, umbrales re-ajustables, contexto de evaluación)
  evolution/       EVOLUTION ENGINE (GA con fitness multi-criterio y penalización de sensibilidad)
  backtest/        BACKTEST ENGINE + métricas
  validation/      splits protegidos, WALK-FORWARD, MONTE CARLO, ROBUSTNESS, OVERFITTING DETECTOR
  adversarial/     ADVERSARIAL ENGINE + ranking compuesto
  probability/     PROBABILITY ENGINE (escenarios con IC, baseline y test)
  memory/          RESEARCH MEMORY + EXPERIMENT TRACKER (SQLite)
  research/        orquestador / AUTONOMOUS RESEARCH MODE
  report/          X-QUANT RESEARCH REPORT (Markdown + JSON)
  dashboard/       USER DASHBOARD (HTML autocontenido; modo servidor con auto-refresh)
```

## Garantías científicas (y cómo se verifican)

| Garantía | Mecanismo | Verificación |
|---|---|---|
| Sin información futura en features | Primitivas causales; test de truncamiento | `test_all_primitives_and_random_expressions_are_causal`; auditoría sobre datos reales en cada run |
| Sin información futura en macro | `available_at` = fin de periodo + retraso de publicación conservador | `test_point_in_time_alignment_never_uses_future_values` |
| Sin ejecución optimista | Señal al cierre de t, fill en t+1 (+latencia), costes por fill, stop antes que take si ambos tocan | `test_backtest.py` |
| TEST/FINAL no se usan para optimizar | `SplitGuard`: optimizar solo en TRAIN; TEST congela la optimización; FINAL una vez | `test_splits_and_guard`; registro en `split_access` |
| Control de comparaciones múltiples | BH-FDR por lote, replicación en holdout, Deflated Sharpe con N acumulado, PBO | `test_bh_fdr_matches_reference`, `test_deflated_sharpe_penalises_many_trials` |
| No fabrica descubrimientos en ruido | Pipeline completo sobre paseo aleatorio y GARCH | `test_negative_control_random_walk_gives_no_edge` (+ 6 semillas GARCH: 6/6 NO EDGE) |
| Detecta ventajas reales | Pipeline completo con efecto inyectado | `test_positive_control_injected_edge_is_found_and_survives` |
| No redescubre | Firma de hipótesis/estrategia + versión de dataset | segunda ejecución en el control negativo |

### Splits

`TRAIN | embargo | VALIDATION | embargo | TEST | embargo | FINAL`. Dentro de TRAIN, features e hipótesis
usan un holdout interno (70/30). VALIDATION solo se usa como puerta (evaluar, nunca ajustar). TEST se
abre una vez por finalista ya congelado. FINAL se abre una vez, para el #1.

### Ataques adversariales por estrategia

Validación fuera de muestra · nº de trades · timing vs entradas aleatorias · walk-forward · ±25 % en
parámetros · costes ×2 (×3 informativo) · latencia +1 · entradas desplazadas ±1 · ejecución aleatorizada ·
años · dependencia de pocas operaciones · sin el mejor mes · regímenes · día de la semana · ruido en
precios · muestreo 2× (informativo) · Monte Carlo de pérdidas · Deflated Sharpe · PBO.
Fallar uno de tipo *reject* → `REJECTED`; de tipo *overfit* → `OVERFIT`.

## Datos disponibles en este entorno (2026-10-03)

La política de red del contenedor de desarrollo solo permite `raw.githubusercontent.com` y PyPI.

| Serie | Fuente | Notas |
|---|---|---|
| EUR/USD diario | Fed H.10 (noon buying rate NY) vía datahub.io | Solo cierre; **viene invertido** (EUR por USD) — se detecta con un ancla (1999-01-04 = 1,1812) y se corrige |
| CPI EE.UU. (YoY) | BLS vía datahub.io | Retraso de disponibilidad 35 días tras fin de mes |
| Yield 10Y EE.UU. | Fed H.15 mensual vía datahub.io | Media mensual, disponible a fin de mes |
| VIX | CBOE vía datahub.io | Cierre posterior al fixing de NY → usable desde la barra siguiente |
| Brent | EIA vía datahub.io | Usable desde la barra siguiente |

**No disponibles** (bloqueados o inexistentes en abierto): intradía/tick (Dukascopy, conector listo: ver
"Datos intradía"), FRED/ECB directos,
calendario económico con consenso, noticias. Los conectores existen; los motores que los necesitan
informan `INSUFFICIENT DATA`.

Formatos para conectar más datos:

- Calendario (`econ_calendar_csv`): `timestamp,event,country,currency,importance,previous,consensus,actual`
- Noticias (`news_csv`): `timestamp,source,headline[,body,url,asset,country]`
- OHLCV (`csv_file`): `timestamp,open,high,low,close[,volume,spread]`
- MetaTrader 5 (`mt5_csv`): export estándar `<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>`

## Resultados de la investigación sobre EUR/USD (2026-10-03/04)

| Run | Dataset | Modo | Estrategias examinadas | Veredicto |
|---|---|---|---|---|
| RUN-00001 | Fed H.10 diario (solo cierre), 1999–2026 | standard | 30 | NO EDGE FOUND |
| RUN-00002 | Fed H.10 diario (solo cierre), 1999–2026 | deep | 80 | NO EDGE FOUND |
| RUN-00003 | Dukascopy H1 | standard | — | ABORTED (la limpieza borraba picos reales de NFP; corregido) |
| RUN-00004 | Dukascopy H1, 2005–2026 | standard | 30 | NO EDGE FOUND (batería v1) |
| RUN-00005 | Dukascopy D1 OHLC (sesiones 17:00 NY) | standard | 30 | NO EDGE FOUND (batería v1) |
| RUN-00006 | Dukascopy H1, 2005–2026 | standard | 30 | NO EDGE FOUND |
| RUN-00007 | Dukascopy D1 OHLC | standard | 30 | NO EDGE FOUND |
| RUN-00008 | Dukascopy D1 OHLC | deep | 80 | NO EDGE FOUND |
| RUN-00009 | Dukascopy H1, 2005–2026 | deep | 80 | NO EDGE FOUND |

En total: 355 estrategias examinadas (312 REJECTED, 43 OVERFIT, ninguna superó la selección),
~438.000 backtests contados como ensayos y 8.200 hipótesis. TEST y FINAL nunca se abrieron.

Lo que sí es real (replicado fuera de muestra) pero no es explotable direccionalmente: agrupamiento de
volatilidad, reversión de la volatilidad alta, agrupamiento de movimientos grandes y efectos por hora del día
en H1 (p. ej. 05–06 h NY negativos, 21 h NY positivos). Estos últimos sobreviven a FDR y al holdout interno,
pero su tamaño (0,06–0,11 desviaciones típicas, ~1 bp) queda por debajo de los costes (~2 bps ida y vuelta).
Los mejores candidatos superan la mayoría de ataques (validación OOS, walk-forward, entradas aleatorias, costes)
y caen por el Deflated Sharpe (N muy alto) y el PBO del proceso de búsqueda, y a menudo por depender de
pocas operaciones: es la firma de la selección entre muchas variantes, no de una ventaja.

Datos validados: H1 de Dukascopy frente al fixing de la Fed (mediana 0,67 bps, correlación de retornos 0,998;
un reloj desplazado ±1 h da 5–7 bps).

## Resultados posteriores: oro, temporalidades, frecuencia, Nasdaq, valor relativo y DXY (2026-10-04)

| Run | Dataset | Qué se probó | Veredicto |
|---|---|---|---|
| RUN-00010/12 | XAU/USD H1 2008–2026 | standard / deep | NO EDGE FOUND |
| RUN-00011/13/14 | XAU/USD D1, H4, H2 | otras temporalidades | NO EDGE FOUND |
| RUN-00015/16 | EUR/USD H4, H2 | otras temporalidades | NO EDGE FOUND |
| RUN-00017/18 | XAU/USD H1, EUR/USD H1 | exigir ≥1 operación/día | NO EDGE FOUND (ningún genoma positivo ni en TRAIN) |
| RUN-00019/20/24 | XAU/USD M30, M15, M5 (2022–2026) | ≥1 operación/día | NO EDGE FOUND (ningún genoma positivo ni en TRAIN) |
| RUN-00021/22 | XAU/USD H1, EUR/USD H1 | variables de sesión (rango del día previo, overnight, apertura NY) | NO EDGE FOUND |
| RUN-00023 | Nasdaq 100 H1 2013–2026 | standard | NO EDGE FOUND |
| RUN-00025/26 | XAU/USD H1, EUR/USD H1 | trailing stop + voto combinado de hipótesis | NO EDGE FOUND |
| RUN-00027 | XAU/USD H1 + plata | valor relativo, divergencia residual y SMT | NO EDGE FOUND |
| RUN-00028 | EUR/USD H1 + GBP/USD | valor relativo, divergencia residual y SMT | NO EDGE FOUND |
| RUN-00029 | EUR/USD H1 + DXY sintético | **confirmatorio pre-registrado**: SMT con el DXY, 12 variantes, N=12 | NO EDGE FOUND (las 12 con Sharpe negativo en TRAIN y VALIDATION) |
| RUN-00030 | EUR/USD H1 + DXY + dólar ex-EUR | exploratorio con divergencias | NO EDGE FOUND |

Mejores candidatos encontrados (todos rechazados): largos en oro H1 con ~4 % anual en TRAIN y ~10 % en
VALIDATION (STR-000363), que caen porque sin su 5 % de mejores operaciones pierden dinero y porque su Sharpe
no supera el Deflated Sharpe; buena parte es probablemente la deriva alcista del oro 2008–2020.

Pista más interesante (no confirmada): "momentum del residual del euro" - cuando EUR/USD ha caído más de lo
que explica el dólar frente al resto de divisas (residual a 20 h en el decil inferior), sigue cayendo
2–10 bps en las 3–24 h siguientes. Aparece frente a GBP/USD (RUN-00028) y frente a la cesta ex-EUR
(RUN-00030, q de descubrimiento 0,00015) pero falla la confirmación en el holdout interno en ambos casos
(OVERFIT). TEST/FINAL siguen sin abrir.

DXY sintético (fórmula ICE sobre 6 pares de Dukascopy, desde 2005) validado contra el índice de Dukascopy
(2017–2026): correlación de retornos horarios 0,978 sin desfase, error de seguimiento 1,9 bps/h
(`research_output/validation/dxy_synthetic_validation.md`).

### Modo confirmatorio

`uv run xquant confirm --spec configs/preregistered/<nombre>.yaml --offline` evalúa una hipótesis escrita
antes de ver resultados (≤20 variantes fijas). Guarda el SHA-256 de la especificación y rechaza ediciones o
repeticiones; el Deflated Sharpe usa N = variantes registradas para el activo, salvo que alguna variable ya se
haya usado en investigación exploratoria (entonces N = todos los ensayos). `uv run xquant portfolio` combina
solo estrategias validadas (ROBUST) y mide la frecuencia de operaciones a nivel de cartera.

## Limitaciones conocidas

- Con datos diarios de solo cierre: sin OHLC, sin volumen, stops evaluados al cierre, ejecución al
  siguiente fixing. Preguntas intradía (hora, sesión, apertura) → `INSUFFICIENT DATA`.
- Series macro con valores revisados (última vintage), no primera publicación.
- La búsqueda está acotada por la gramática de features y el presupuesto: `NO EDGE FOUND` significa
  "no encontrado en este espacio y con estos datos", no "no existe".
