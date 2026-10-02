# PROJECT_PLAN — Abogado personal IA

Estado: **Fase 0 completada (auditoría + plan + estructura inicial).** Pendiente de aprobación antes de la Fase 1.

Principio rector: el sistema optimiza para *una respuesta jurídicamente útil, verificable y honesta sobre su nivel de certeza*, no para responder rápido. Ninguna afirmación jurídica sale al usuario sin pasar por el sistema de verificación (§7).

---

## 1. Auditoría del entorno (Fase 0)

| Elemento | Resultado | Consecuencia |
|---|---|---|
| Repositorio | Vacío, sin commits. Rama `claude/modest-einstein-aj41v6` | Se parte de cero |
| SO / runtime | Ubuntu 24.04, Python 3.11.15, Node 22, `uv`, `poetry`, Docker | Stack Python con `uv` |
| Librerías ya presentes | `pydantic` 2.13, `cryptography` 49, `httpx` 0.28, SQLite 3.45 | Base suficiente sin dependencias exóticas |
| Herramientas de documentos | `pdftotext` disponible; **sin** `tesseract` (OCR) | Imágenes/escaneos → visión de Claude, no OCR local |
| API de Claude | Accesible por red. **No hay `ANTHROPIC_API_KEY` propia** del proyecto | El usuario necesita una API key (ver §12) |
| Fuentes oficiales | `boe.es`, `eur-lex.europa.eu`, `poderjudicial.es` (CENDOJ), `dogc.gencat.cat`, `tribunalconstitucional.es` → **bloqueadas (403) por la política de red de este contenedor de desarrollo** | Ver §1.1 |
| Disco / memoria | 30 GB libres, 15 GB RAM | Sin limitaciones |

### 1.1 Bloqueo de red: qué significa

El bloqueo afecta **solo a este contenedor de desarrollo en la nube**, no al producto:

- El sistema final se ejecutará en el ordenador del usuario, con acceso normal a Internet.
- Además, la búsqueda/lectura web de Claude (`web_search` / `web_fetch`) se ejecuta en los servidores de Anthropic, no en la máquina local.
- Mientras se desarrolla aquí, los conectores de fuentes se prueban con **respuestas grabadas (fixtures)** y los tests en vivo se marcan como opcionales.
- **No he podido verificar desde aquí la forma exacta de los endpoints de la API de datos abiertos del BOE.** Se confirmará en la Fase 4 desde una red con acceso; hasta entonces no se escribe código que dependa de supuestos sobre su formato.

Para permitir esos dominios en este entorno, el usuario puede editar *Network access* del entorno (añadir los dominios a *Allowed domains*): https://code.claude.com/docs/en/cloud-environments#network-access

---

## 2. Decisiones técnicas

| Decisión | Elección | Por qué | Qué se pierde / riesgo |
|---|---|---|---|
| Lenguaje | Python 3.11 | Mejor ecosistema para PDF/DOCX, SDK oficial de Anthropic, ya instalado | — |
| Gestor | `uv` + `pyproject.toml` | Reproducible y rápido | — |
| Interfaz v1 | **CLI** (`typer` + `rich`) | Lo más rápido para tener un núcleo sólido y testeable | Menos cómodo que una web. Se añade **web local** (FastAPI) en una fase posterior sin tocar el núcleo |
| LLM | Claude vía SDK oficial `anthropic`, modelo `claude-opus-5-5` | El más adecuado para razonamiento jurídico largo | Coste por consulta. Se mide antes de pensar en modelos más baratos |
| Salidas del LLM | **Salidas estructuradas** (esquemas `pydantic`), nunca texto libre que haya que parsear | Permite verificar cada afirmación de forma individual | Prompts algo más rígidos |
| Búsqueda jurídica | (a) Conectores directos a fuentes oficiales (BOE, EUR-Lex, DOGC) + (b) `web_search`/`web_fetch` de Claude **restringidos a dominios oficiales** (`allowed_domains`) | Fuente primaria siempre que exista; búsqueda web solo para descubrir | CENDOJ no ofrece API pública documentada (ver §11) |
| Almacenamiento | **SQLite local** + documentos en disco, **cifrados** (AES-GCM, clave derivada de contraseña con scrypt) | Privado, sin servidor, un solo archivo, fácil de borrar | Si el usuario pierde la contraseña, pierde los datos (por diseño) |
| Cálculo de plazos | **Motor determinista en Python**, nunca el LLM | Las fechas no pueden depender de un modelo probabilístico | Requiere calendarios de festivos como datos verificados (§8) |
| Documentos | `pypdf`/`pdftotext` (PDF con texto), `python-docx` (DOCX), visión de Claude (imágenes, escaneos) | Extracción local cuando se puede | Las imágenes salen del equipo hacia la API |

---

## 3. Arquitectura

Pipeline modular. Cada etapa es un módulo con entrada y salida tipadas; ninguna depende de "un prompt gigante".

```
ENTRADA DEL USUARIO (texto / documento / comando)
   │
   ▼
[router]        → detecta intención/comando (§10) y caso activo
   │
   ▼
[intake]        → hechos, opiniones, fechas, partes, cantidades (separados)
   │
   ▼
[clasificación] → área jurídica + jurisdicción candidata (estatal / Cataluña / UE / municipal)
   │              + preguntas que faltan (solo las que cambian el análisis)
   ▼
[investigación] → conectores de fuentes oficiales + búsqueda restringida
   │              → registro de fuentes (texto, URL, fecha de consulta, hash, vigencia)
   ▼
[análisis]      → aplica normas a hechos; cada afirmación = Claim con fuentes y confianza
   │
   ▼
[plazos]        → motor determinista (fecha inicio explícita, cómputo, calendario)
   │
   ▼
[riesgo]        → nivel de riesgo, detección de asuntos de alto riesgo (§9)
   │
   ▼
[verificación]  → 8 checks (§7). Lo que falla se corrige o se marca "no verificado"
   │
   ▼
[respuesta]     → plantilla según modo (Abogado, Investigador, Segunda opinión, Abogado del diablo…)
   │
   ▼
[memoria]       → guarda en el expediente del caso (separado del conocimiento jurídico)
```

### 3.1 Estructura de módulos

```
src/abogado/
  config.py            configuración y rutas (sin secretos en código)
  domain/              modelos de datos (pydantic): Case, Fact, Document, Source, Claim, Deadline…
  llm/                 cliente de Claude, esquemas de salida, prompts por etapa
  pipeline/            etapas: router, intake, classify, research, analyze, risk, respond
  sources/             conectores: boe, eurlex, dogc, web (restringido), registro de fuentes
  verification/        los 8 checks + políticas de corrección
  deadlines/           motor de plazos + calendarios (datos con fuente)
  documents/           extracción PDF/DOCX/imagen, análisis de contratos y notificaciones
  drafting/            generación de borradores (HECHOS / FUNDAMENTOS / SOLICITUD / DOCUMENTACIÓN)
  storage/             SQLite, cifrado, registro de accesos
  cli/                 interfaz de línea de comandos
tests/
  unit/  verification/  hallucination/  deadlines/  jurisdiction/  documents/  fixtures/
```

### 3.2 Separación memoria del caso / conocimiento jurídico

Dos almacenes distintos, sin claves compartidas:

- **Expedientes** (`cases`, `facts`, `documents`, `communications`, `actions`, `deadlines`, `case_claims`): todo cifrado y con `case_id`. Una consulta solo puede leer el caso activo.
- **Conocimiento jurídico** (`sources`, `source_versions`): textos oficiales cacheados, sin ningún dato personal. Un caso *referencia* fuentes por id; una fuente nunca referencia un caso.

---

## 4. Modelo de datos (resumen)

- **Case**: id `#001…`, título, descripción, jurisdicción(es), área, estado (`Nuevo`, `Recopilando información`, `Investigando`, `Pendiente de documentación`, `Pendiente de actuación`, `En curso`, `Resuelto`, `Archivado`), timestamps.
- **Party**: nombre/rol (usuario, contraparte, organismo), relación.
- **Fact**: texto, tipo (`hecho_confirmado` | `afirmación_del_usuario` | `opinión` | `extraído_de_documento`), fecha, origen (mensaje o documento + página).
- **Document**: tipo detectado, hash SHA-256, ruta cifrada, texto extraído, fechas, partes, autenticidad = `no verificada` por defecto.
- **Source**: tipo (norma, resolución, sentencia, web oficial), identificador oficial, artículo, URL, fecha de publicación, fecha de consulta, hash del texto, estado de vigencia y fecha de comprobación.
- **Claim**: texto, categoría (`hecho` | `norma` | `interpretación` | `plazo` | `recomendación`), `source_ids`, confianza (`ALTA`/`MEDIA`/`BAJA`) + motivo, resultado de verificación.
- **Deadline**: evento de inicio, fecha de inicio (o alternativas), regla aplicada (+ fuente), tipo de cómputo, calendario usado, fecha límite, incertidumbre.
- **Action / Communication**: registro cronológico.
- **AuditLog**: solo-añadir; quién/qué/cuándo se accedió o modificó.

---

## 5. Cómo se usa Claude

- SDK oficial `anthropic` (Python), modelo `claude-opus-5-5`, *adaptive thinking*, esfuerzo `high` para análisis.
- Cada etapa tiene su propio prompt de sistema corto y un **esquema de salida estructurada**.
- **Fallback** del lado del servidor activado por defecto (si el modelo rechaza una petición, el servidor reintenta con otro modelo). Se puede desactivar.
- `web_search` / `web_fetch` con `allowed_domains` limitado a la lista blanca de §6.
- El contenido de documentos y páginas web se pasa siempre **como datos**, nunca como instrucciones (defensa contra *prompt injection* en documentos subidos).
- *Prompt caching* para las partes fijas (prompts de sistema, esquemas).
- Coste: se registra por caso el uso de tokens para poder medirlo.

---

## 6. Fuentes

Lista blanca inicial (ampliable, revisada por el usuario):

| Ámbito | Dominio | Uso |
|---|---|---|
| Estatal | `boe.es` | Legislación consolidada, BOE diario |
| Cataluña | `dogc.gencat.cat`, `portaljuridic.gencat.cat`, `gencat.cat` | DOGC, normativa catalana |
| UE | `eur-lex.europa.eu` | Reglamentos, directivas, jurisprudencia TJUE |
| Jurisprudencia | `poderjudicial.es` (CENDOJ), `tribunalconstitucional.es`, `curia.europa.eu` | Sentencias |
| Administración | `agenciatributaria.gob.es`, `sede.dgt.gob.es`, `*.gob.es` (lista concreta por definir) | Procedimientos, sedes electrónicas |
| Municipal | sedes y boletines provinciales concretos (p. ej. BOP) | Ordenanzas — se añaden caso a caso |

Reglas:
1. Toda afirmación de categoría `norma`, `plazo` o `jurisprudencia` necesita al menos una **Source** de un dominio de la lista blanca.
2. Fuentes secundarias (blogs, despachos) solo como contexto, etiquetadas como tales, y nunca como única base de una conclusión.
3. Formato de cita mostrado al usuario: **Fuente · Norma/resolución · Artículo · Fecha · Enlace**.

---

## 7. Sistema de verificación

Los 8 checks del encargo, convertidos en comprobaciones concretas:

| # | Check | Implementación | Tipo |
|---|---|---|---|
| 1 | ¿Requiere fuente? | Toda Claim de categoría `norma`/`plazo`/`jurisprudencia` → sí | Determinista |
| 2 | ¿Tengo fuente? | `source_ids` no vacío y la Source existe en el registro (se ha descargado de verdad, no la ha "recordado" el modelo) | Determinista |
| 3 | ¿Es fiable? | Dominio en lista blanca; fuente secundaria nunca basta sola | Determinista |
| 4 | ¿Está vigente? | Estado de vigencia y fecha de comprobación ≤ N días; si no se pudo comprobar → confianza máx. `MEDIA` | Determinista + conector |
| 5 | ¿Jurisdicción correcta? | La jurisdicción de la fuente es compatible con el perfil del caso (p. ej. caso en Cataluña con norma estatal → se exige haber comprobado si hay norma catalana) | Determinista + regla |
| 6 | ¿Fecha correcta? | Los plazos solo pueden venir del motor de plazos; cualquier fecha en texto del LLM se contrasta | Determinista |
| 7 | ¿Interpretación vs obligación? | Segunda pasada del LLM que clasifica la afirmación; si dice "debe/obligatorio" sin cita literal de la norma → se reescribe como interpretación | LLM + regla |
| 8 | ¿Inventado? | El artículo citado debe aparecer en el **texto descargado** de la fuente (coincidencia normalizada). Si no aparece, la cita se rechaza | Determinista |

Política ante fallo: se corrige (se rebaja la confianza, se reformula o se elimina la afirmación) y, si no se puede corregir, se muestra explícitamente como **"No puedo confirmar este punto con suficiente seguridad."** Nunca se muestra sin marcar.

---

## 8. Plazos

- Motor determinista: entra *evento de inicio + fecha + regla de cómputo + calendario*, sale *fecha límite + explicación paso a paso*.
- Las **reglas de cómputo** (días hábiles/naturales, exclusiones, meses, etc.) se guardan como datos, **cada una con su fuente oficial y estado `verificada`/`pendiente`**. Una regla `pendiente` no produce fechas exactas.
- Los **calendarios de festivos** (estatal, Cataluña, municipal) se cargan como datos con su fuente oficial por año. Si falta el calendario de un año/municipio → el motor devuelve un **rango** y lo dice.
- Si la fecha de inicio es dudosa (p. ej. notificación), el motor calcula todas las alternativas: "El plazo podría empezar a contar desde X o Y dependiendo de…".
- No se escribe ninguna regla de plazo "de memoria": se incorporan en la Fase 4/5 tras verificarlas en BOE/DOGC.

---

## 9. Riesgo y avisos

- Detector de asuntos de alto riesgo (detención, penal, violencia, extranjería/expulsión, menores, despidos, órdenes judiciales, accidentes graves, grandes cantidades, plazos inminentes) → nivel de riesgo visible, plazo destacado, recomendación de abogado colegiado.
- Aviso legal **contextual**, no en cada respuesta: siempre en alto riesgo, plazos próximos o procedimientos judiciales.
- Nunca "vas a ganar".

---

## 10. Comandos / intenciones

Analiza mi caso · Investiga esto · Busca la ley · Busca jurisprudencia · Revisa este documento · Busca errores · ¿Qué riesgos tengo? · ¿Qué puede alegar la otra parte? · ¿Qué plazo tengo? · ¿Qué debería hacer ahora? · Prepara una reclamación · Prepara un recurso · Explícamelo sencillo · Dame una segunda opinión · Busca argumentos en mi contra · Actualiza este caso · Resume mi expediente.

El router acepta lenguaje natural ("me han echado del trabajo") y lo asigna a un modo; los comandos explícitos son un atajo, no un requisito.

---

## 11. Riesgos del proyecto

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Alucinación de normas/artículos | Crítico | Checks 2, 3 y 8: sin texto oficial descargado no hay cita |
| Error en plazos | Crítico | Motor determinista, reglas y calendarios con fuente, rangos si hay duda |
| Aplicar derecho estatal donde rige el catalán | Alto | Check 5 + tests de jurisdicción |
| Texto consolidado desactualizado | Alto | Fecha de consulta y de vigencia en cada fuente; caducidad de caché |
| CENDOJ sin API pública documentada; condiciones de uso | Medio | Se revisan sus condiciones antes de automatizar nada; alternativa: búsqueda restringida + enlace para consulta manual |
| *Prompt injection* desde documentos o webs | Alto | Contenido externo siempre como datos; la etapa de análisis no ejecuta instrucciones del documento; tests específicos |
| Privacidad: los documentos se envían a la API de Anthropic | Alto | Explícito para el usuario; minimizar lo enviado; datos locales cifrados; ver §12 |
| Pérdida de la contraseña de cifrado | Medio | Por diseño no hay recuperación; se avisa al configurar |
| Coste de API | Medio | Registro de tokens por caso; caché de prompts y de fuentes |
| Responsabilidad: no es un abogado | Alto | Avisos contextuales; nivel de confianza; nunca garantías |
| Red bloqueada en el entorno de desarrollo | Bajo | Fixtures; tests en vivo opcionales; permitir dominios en el entorno |

---

## 12. Decisiones que necesito del usuario

1. **API key de Anthropic.** El sistema necesita una (la suscripción de Claude no incluye la API). Se guarda en variable de entorno o en el llavero del sistema, nunca en el repositorio.
2. **Dónde se ejecutará** (Windows / Mac / Linux). Afecta a la instalación y al llavero de secretos.
3. **Interfaz:** CLI primero y web local después (recomendado), o web local desde el principio.
4. **Privacidad:** aceptar que el texto de los casos y documentos se envía a la API de Anthropic para su análisis (los datos locales sí quedan cifrados).

---

## 13. Fases

Cada fase termina con: tests en verde, revisión de seguridad y de errores, y resumen al usuario.

| Fase | Contenido | Criterio de aceptación |
|---|---|---|
| **0** | Auditoría, este plan, estructura inicial | ✅ Hecho |
| **1 — Núcleo** | Modelos de dominio, configuración, cliente de Claude con salidas estructuradas, router + intake + clasificación (jurisdicción y área), CLI mínima | "Mi casero no me devuelve la fianza" → hechos separados de opiniones, jurisdicción candidata, preguntas que faltan. Sin afirmaciones normativas todavía |
| **2 — Casos y memoria** | SQLite, CRUD de casos, estados, cronología, separación expediente/conocimiento, "¿qué pasó con lo del alquiler?" | Recupera el caso correcto; nunca mezcla datos entre casos (test) |
| **3 — Documentos** | Extracción PDF/DOCX/imagen, análisis de contratos (🔴🟠🟡🟢), multas y notificaciones | No inventa campos ausentes; maneja archivos corruptos; marca autenticidad como no verificada |
| **4 — Investigación** | Conectores BOE / EUR-Lex / DOGC, búsqueda restringida, registro de fuentes, comprobación de vigencia, reglas de plazos verificadas | Toda cita tiene texto oficial descargado y fecha de consulta |
| **5 — Verificación** | Los 8 checks, motor de plazos completo, niveles de confianza | Suite anti-alucinación en verde |
| **6 — Documentos generados** | Reclamaciones, recursos, requerimientos, burofaxes… con `[DATO PENDIENTE]` | Ningún dato inventado en los borradores (test) |
| **7 — Seguridad y privacidad** | Cifrado, contraseña, borrado de casos, registro de accesos, minimización | Revisión de seguridad sin hallazgos altos |
| **8 — Tests** | Suites completas + evaluaciones en vivo opcionales | Cobertura de los casos de §14 |
| **9 — Auditoría completa** | Revisión de punta a punta, segunda opinión y abogado del diablo | Informe de auditoría |

---

## 14. Tests

- **Unitarios** por módulo.
- **Alucinaciones jurídicas:** artículo inexistente pedido por el usuario → el sistema dice que no puede confirmarlo; cita sin fuente → rechazada; fuente fuera de lista blanca → rechazada; artículo que no aparece en el texto descargado → rechazado.
- **Fechas:** cálculo de plazos con fixtures; inicio dudoso → alternativas; calendario ausente → rango, no fecha exacta.
- **Jurisdicción:** caso localizado en Cataluña → no aplica solo normativa estatal sin comprobar la catalana.
- **Documentos:** campos ausentes no se rellenan; PDF corrupto → error claro; instrucciones ocultas en un documento → ignoradas.
- **Entradas maliciosas / incompletas / contradictorias.**
- **Evaluaciones en vivo** (con la API real): opcionales y con coste, se ejecutan solo con aprobación.
