# EA de MetaTrader 5 — `nq_orb5_v2` (variante A) — SOLO DEMO / PROBADOR

`NQ_ORB5_v2_DemoOnly.mq5` implementa la estrategia pre-registrada `configs/strategies/nq_orb5_v2.yaml`
(variante A, sin filtro de contexto). **Se niega a arrancar en una cuenta real**: solo funciona en el
Probador de Estrategias o en cuentas demo. Es código de investigación, no una recomendación de inversión.

## Para qué sirve

1. **Validación independiente**: el backtest del laboratorio usa datos CFD de Dukascopy (solo BID). Pasar el
   EA por el Probador con los datos de tu broker es una segunda fuente de datos.
2. **Paper trading** en demo, con un diario CSV (`MQL5/Files/NQ_ORB5_journal.csv`) que registra cada decisión
   (entrada, no-trade y motivo, salida), para compararlo después con el backtest.

## Instalación

1. Copia el `.mq5` a `MQL5/Experts/` (MetaTrader: Archivo → Abrir carpeta de datos).
2. Ábrelo en MetaEditor y compílalo (F7). **Este archivo no se ha podido compilar en el entorno del
   laboratorio** (no hay MetaEditor): si da errores, pásamelos tal cual.
3. Adjúntalo a un gráfico del símbolo del Nasdaq 100 de tu broker (US100, USTEC, NAS100, NQ…).

## Parámetro crítico: `InpServerMinusNY`

El EA calcula la hora de Nueva York como *hora del servidor − InpServerMinusNY horas*. El valor por defecto (7)
es el de los brokers "NY close" (servidor GMT+2 en invierno / GMT+3 en verano, siguiendo el horario de EE. UU.).
Si tu broker usa otra convención, la diferencia puede no ser constante todo el año (p. ej. servidor con horario
de verano europeo: 6 h durante 2–3 semanas al año). Al arrancar en demo, el EA imprime la hora del servidor, la
hora NY calculada y la hora GMT: **comprueba que la hora NY es correcta antes de confiar en el EA**.

## Probador de Estrategias

- Modelo: **"Cada tick basado en ticks reales"** (la entrada depende del precio exacto de las 09:35:00).
- Periodo de las velas del gráfico: cualquiera (el EA lee velas M1).
- Compara con el laboratorio: R medio por operación, % de aciertos (~25 %), número de operaciones por año
  (~225) y reparto de salidas (stop / objetivo / 16:00).

## Diferencias conocidas con el backtest del laboratorio

- El EA entra con el precio real (ask en largos, bid en cortos) y sale por stop/TP del servidor: el
  deslizamiento real sustituye al coste fijo modelado (~0,87 pb ida y vuelta).
- Si no puede enviar la orden en los primeros `InpMaxEntryDelaySec` segundos tras las 09:35:00, no opera ese día
  (el backtest mostró que retrasar la entrada 1 minuto le quita ~60 % de la ventaja).
- Días de cierre anticipado: se saltan el 24-dic, el 3-jul y el viernes posterior a Acción de Gracias.
  El backtest saltaba los días sin vela de las 16:00.
- Sin filtro de noticias (igual que el backtest).
