# X-QUANT — PROJECT_STATE (memoria principal del proyecto)

Actualizado: 2026-10-08. Leer esto antes de explorar código. Rama `claude/ecstatic-pasteur-nyyph7`, PR #1.
El repo raíz también contiene otro proyecto independiente (`src/abogado`, `PROJECT_PLAN.md`): no se toca.

## 1. Qué es hoy (arquitectura real)

Paquete Python 3.11 (`uv`), ~8.000 líneas en `src/xquant`, 79 tests (pytest; ruff y mypy limpios). Sin servidor, sin
cola, sin agentes LLM, sin workers: todo se lanza por CLI (`xquant data|research|confirm|allocate|daytrade|ml|portfolio|dashboard|memory|sources`).
Persistencia: SQLite `research_output/memory.db` (WAL) + informes md/json + dashboard HTML estático.

| Departamento objetivo | Módulo existente | Estado |
|---|---|---|
| 01 Data Mining | `data/` (engine, cleaning, pit, schema, crosscheck, sources: Dukascopy velas BID/ASK o solo BID, datahub CSV, MT5 CSV, resample, basket/DXY) | FUNCIONA. Calidad PASS/WARN/FAIL, picos confirmados, point-in-time, cross-check vs Fed/Banco Mundial/DXY |
| 02 Market Research | `market/behavior.py`, `market/regimes.py` (GMM) | FUNCIONA (91 tests estadísticos/run, BH-FDR + réplica) |
| 03 Pattern Mining | `features/library.py` (primitivas causales, sesión, VWAP semanal, divergencias, momentum intradía), `features/discovery.py` | FUNCIONA (auditoría de causalidad por truncamiento) |
| 04 Macro | `macro/engine.py`, `macro/event_study.py` | PARCIAL: series mensuales "latest vintage"; **sin consenso → sin sorpresas** |
| 05 News | `news/engine.py` | ESQUELETO sin datos (no hay fuente de noticias con timestamps) |
| 06 Hypothesis Lab | `hypothesis/engine.py`, `research/confirm.py` (pre-registro con SHA-256, ejecución única, contaminación) | FUNCIONA |
| 07 Strategy Factory | `strategy/genome.py` (reglas), `daytrade/` (ORB por especificación de 10 puntos), `allocation/` (carteras), `ml/` (walk-forward GBM) | FUNCIONA |
| 08 Evolution | `evolution/engine.py` (GA, fitness multi-criterio, vecinos) | FUNCIONA; **sin genealogía** (solo `origin`) |
| 09 Red Team | `adversarial/engine.py` (batería v3: ~20 ataques) | FUNCIONA |
| 10 Validation | `validation/` (splits+embargo+SplitGuard, walk-forward, MC, bootstrap, DSR con N acumulado, PBO) | FUNCIONA; SplitGuard **solo por ejecución** |
| 11 Strategy HQ | estados en memoria (REJECTED/OVERFIT/PASSED/ROBUST) + `adversarial.score` + `portfolio.py` | PARCIAL: sin Hall of Fame/Cementerio como vista |
| 12 Research Director | `research/orchestrator.py` (4 líneas, presupuestos, paradas) | PARCIAL: decide **dentro** de una ejecución; nada decide **entre** ejecuciones |

Infra transversal: memoria (`memory/store.py`: runs, experiments, hypotheses, strategies, findings, trials, split_access,
preregistrations, log; DO NOT REDISCOVER; compactación + archivo gzip de rechazos), informes (`report/`), dashboard estático,
logs JSONL, EA MT5 solo-demo (`mt5/`).

## 2. "Las 212 tareas"
No existe ninguna lista de tareas en el repo. 212 = **ficheros cambiados en el PR #1** (86 commits). Lo realmente
implementado está en la tabla anterior; no hay tareas "marcadas como hechas" sin código. No hay mocks/placeholders en `src`
(grep limpio); los datos sintéticos solo existen en tests (controles positivo/negativo).

## 3. Resultados de investigación (no repetir)
39 ejecuciones. Todas NO EDGE FOUND salvo `nq_orb5_v2` (ORB 5 min Nasdaq, EDGE provisional, frágil: TEST +0,025R,
réplica S&P 500 no confirma, sensible a 1 min de retraso). 873 estrategias examinadas (789 REJECTED, 84 OVERFIT),
51.754 hipótesis. Probado y descartado: EUR/USD (Fed diario, H1/H2/H4/D1), oro (H1/H2/H4/D1/M30/M15/M5), Nasdaq H1,
≥1 op/día, sesiones, trailing+ensemble, valor relativo oro/plata y EUR/GBP, SMT/residuo DXY, VWAP semanal, momentum
intradía (Gao et al.), vol-managed, TSMOM, momentum FX cross-section, ML walk-forward. Detalle: `README.md` y `research_output/reports/`.
Datos quemados (TEST/FINAL ya abiertos): NAS100 minuto (2023-07→2026-09) por nq_orb5_v2 y spx réplica.

## 4. Riesgos y deuda (clasificación)

| # | Problema | Severidad | Decisión |
|---|---|---|---|
| R1 | Contenedor efímero: `cache/` (161 MB de datos Dukascopy, horas de descarga con rate-limit) se pierde | CRITICAL | Necesita almacenamiento persistente (decisión del usuario) |
| R2 | `memory.db` (37 MB) + informes (23 MB) en git; límite GitHub 100 MB/fichero | CRITICAL | Mismo almacenamiento que R1; mitigado con compactación |
| R3 | SplitGuard por ejecución: TEST/FINAL de un mismo dato pueden reabrirse en ejecuciones o configs distintas | CRITICAL (integridad) | HECHO 2026-10-08: tabla `protected_access` por `bars:<sha>`; un EDGE con FINAL reutilizado se etiqueta "not clean OOS" |
| R4 | N del Deflated Sharpe por símbolo de config: EURUSD_H1, _RV, _DXY comparten precios pero cuentan ensayos por separado | HIGH (integridad) | HECHO 2026-10-08: familias `FAMILY:bars:<sha>` (backfill: EUR/USD H1 = 210.973 ensayos, oro H1 = 169.293); DSR usa el mayor N |
| R5 | Sin cola/runner persistente, sin reintentos/heartbeat | HIGH | HECHO 2026-10-08: `lab/queue.py` (tablas `jobs`, `workers` en memory.db): prioridades, dependencias, dedupe, subproceso por trabajo, timeout, reintentos con back-off, recuperación de workers muertos; CLI `queue add/list/cancel`, `worker`, `lab status` (→ `research_output/lab_status.json`) |
| R6 | Sin Director entre ejecuciones | HIGH | HECHO 2026-10-08: `lab/director.py` (specs sin evaluar → huecos de cobertura por fuente de precios → seguimiento deep con evidencia → mantenimiento; nunca descarga; fallos repetidos → humano). CLI `director plan|run`, `autonomous --cycles --max-hours --max-new` |
| R7 | Sin genealogía de estrategias (padres, mutaciones) | MEDIUM | IMPROVE genome/memoria |
| R8 | Macro sin consenso, News sin fuente | MEDIUM (bloqueado por datos) | Requiere fuente externa |
| R9 | `run_orb`/GA en Python puro: lento a escala | LOW | DEFER |
| R10 | Dashboard estático, sin estado en vivo | MEDIUM | Fase 8 tras API de estado |

## 5. Infra / permisos
REQUIRED: almacenamiento persistente para datos+memoria (p. ej. bucket GCS con credenciales del usuario, o máquina
propia); red a `datafeed.dukascopy.com` y `raw.githubusercontent.com` (ya permitidas).
OPTIONAL: fuente de calendario económico con consenso y de noticias con timestamps (de pago o con licencia);
`ANTHROPIC_API_KEY` solo si se quieren agentes LLM (coste y no reproducibilidad).
NOT NEEDED: Canva, Higgsfield, Notion, Gmail, Calendar, Drive para la investigación.
Skills del proyecto: ninguna en `.claude/` (no hay duplicados que evitar).

## 6. Roadmap priorizado
- **F3 Foundation**: ~~R3~~ ~~R4~~ ~~cola + runner + estado real~~ (hechos). Pendiente: almacenamiento persistente (R1/R2, decisión del usuario: bucket GCS recomendado, variables `XQUANT_GCS_BUCKET`, `XQUANT_GCS_KEY_JSON`).
- ~~F7 Director~~ (hecho). Ledger con linaje: datos remuestreados (M30←M1) comparten la clave de sus splits protegidos.
- F5/F6 genealogía + vistas Hall of Fame / Cementerio (estados DISCOVERED…DESTROYED mapeados desde la memoria).
- F8 Control Center/Observer conectado al estado real. F4 macro/news cuando haya datos. F9 campaña EUR/USD.
- DEFER: UI 3D, agentes LLM, RL, ejecución real (prohibida).

## 7. Decisiones vigentes
- TRUTH > PROFIT; NO EDGE FOUND es un resultado válido. Sin trading real; EA solo demo.
- Hipótesis dirigidas: pre-registro antes de mirar datos (spec + SHA-256 en git). Exploración: N acumulado.
- "Agentes" = workers deterministas registrados en la cola (estado real). LLM opcional y posterior.
- Descargar solo lo necesario (solo BID cuando los costes son fijos).

## 8. Uso rápido de la cola
`xquant queue add research --asset EURUSD_H1 --max-minutes 30 --priority EXPLORATORY --reason "..."` · `xquant worker --idle-exit 600` · `xquant lab status`.
Tipos: research, confirm, allocate, daytrade, ml (`--spec`), data (`--online` para descargar), compact. Logs: `runs/jobs/`.
