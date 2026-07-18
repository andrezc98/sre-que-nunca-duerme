# Guion de referencia — El SRE que Nunca Duerme
**KCD Lima Perú 2026 · sábado 18-jul · 25 min + 5 Q&A**

> Tres partes: (1) mapa de tiempos, (2) guion hablado slide por slide con su número y fuente,
> (3) banco de datos por fuente — cifras extra para improvisar o para Q&A.
> Fuentes completas con URLs y caveats: `fuentes.md`.

---

## 1. Mapa de tiempos

| Min | Slides | Bloque |
|---|---|---|
| 0:00–0:30 | 1 | Portada + quién soy |
| 0:30–4:30 | 2–6 | Cold open con fuentes al frente (~50-55 s por slide de número) |
| 4:30–6:00 | 7–8 | Tesis + elenco (elenco COMPRIMIDO a ~50 s) |
| 6:00–7:00 | 9 | Prólogo: la escena montada (1 min, no más) |
| 7:00–9:30 | 10–12 | 7:31 p.m. — el incidente y los ojos |
| 9:30–11:30 | 13–14 | Las manos: el agente investiga |
| 11:30–17:00 | 15–19 | El versus + benchmark (el corazón) |
| 17:00–19:30 | 20–21 | La lección + el estado del arte |
| 19:30–21:30 | 22–23 | El freno + la frontera |
| 21:30–23:30 | 24 | DEMO EN VIVO |
| 23:30–25:00 | 25–26 | Cierre + gracias |
| Q&A | 27 | Fuentes proyectadas |

**Regla de pánico**: si a min 17 no llegaste a la slide 20 → salta la S18–19 (MiniMax) y comprime S21. La demo en vivo NO se sacrifica; el clip de respaldo está a un click.

---

## 2. Guion hablado (por slide)

### S1 — Portada [0:00]
"Soy Andrés Zeballos, arquitecto de soluciones. Todo lo que van a ver corre en un repo público — el QR va al final. Y una advertencia: esta charla tiene más números que texto. Todos con fuente. Incluidos los míos."

### S2 — 7:04 p.m. [0:30]
"Viernes, 7:04 de la tarde. Cierras la laptop. Terminaste por hoy. Pero el celular se queda en la mesa de noche con volumen — por si acaso. Todos aquí saben qué significa ese 'por si acaso'. Esta charla es esa noche, contada hora por hora. Primero: ¿qué está en juego mientras no miras?"

### S3 — $15,000/minuto [1:00 — ~55 s, con fuente al frente]
"Según 'The Hidden Costs of Downtime' — un estudio de Oxford Economics con Splunk, 2,000 ejecutivos encuestados en 20 países, Latinoamérica incluida — un minuto de sistema caído le cuesta a una empresa grande **quince mil dólares**. Por minuto. Al año, solo entre las 2,000 empresas más grandes del mundo: **600 mil millones**. Y el mismo estudio dice dos cosas más que duelen: subió **50% en solo dos años** — la edición 2024 medía 400 mil millones — y cada empresa pierde en promedio **95 millones al año** solo en ingresos que no vuelven. New Relic lo mide por incidente: la mediana de un outage grave es **2 millones de dólares por hora** — y baja a la mitad cuando tienes observabilidad completa. Cada minuto que tardas en entender qué pasa, tiene precio."
(Opcional, aterrizaje local: "diez minutos de downtime = un departamento en Lima.")
→ Splunk/Oxford 2026 + New Relic 2025

### S4 — 34% toil [1:55 — ~55 s]
"El SRE Report de Catchpoint — la encuesta anual del gremio — viene midiendo lo mismo tres años seguidos: el toil, la chamba manual y repetitiva que no construye nada, era 25% de tu semana en 2024, 30 en 2025, **34 este año**. La tendencia es lo grave. El libro de SRE de Google le puso la línea roja en 50%, y tiene una frase que me encanta: *'el toil, si lo dejas, se expande hasta llenar el 100% del tiempo de todos'*. ¿Y las alertas que se supone nos protegen? Una encuesta de este año a más de mil SREs encontró que **78% tuvo incidentes donde NINGUNA alerta disparó** — y 44% tuvo un outage por alertas que sí llegaron y fueron ignoradas o suprimidas. No nos falta telemetría. Nos falta quien la lea."
→ Catchpoint 2024–26 · Google SRE cap. 5 · NeuBird 2026 (n=1,039; si preguntan la fuente: NeuBird, vendor de AI SRE — decirlo)

### S5 — 7% [2:50 — ~50 s]
"La encuesta anual de la CNCF — la fundación detrás de Kubernetes, publicada en enero — cuenta la paradoja en tres números. **82%** de las empresas con contenedores ya corre Kubernetes en producción — era 66% hace dos años: eso está ganado. **66%** de las que usan IA generativa la corren sobre Kubernetes — la IA ya vive aquí. Pero solo **7%** despliega modelos a diario; 47% dice 'ocasionalmente' y 44% ni siquiera ha empezado. La misma encuesta lo llama 'etapa temprana de madurez productiva de la IA'. Entre ese 66 y ese 7 está el hueco de esta charla: la IA llegó a Kubernetes — pero no llegó a operar."
→ CNCF Annual Survey 2025

### S6 — $65,000,000 [3:40 — ~55 s]
"Y lo que cuesta mirar: 2023, llamada de resultados de Datadog. El CFO menciona 'una factura grande que no se repitió'. Un analista de JP Morgan hace la cuenta: **65 millones de dólares** — un solo cliente, un solo año. El CFO confirma: 'una empresa cripto'. The Pragmatic Engineer lo confirmó después con ingenieros de adentro: era Coinbase. Ojo: es estimación de analista, no cifra oficial — lo digo con esa etiqueta. ¿El final de la historia? Coinbase migró a stack propio: Grafana, Prometheus, ClickHouse. El mismo tipo de stack de esta charla. Y no es caso aislado: según la encuesta de Grafana Labs, la observabilidad ya se come **17% del gasto de infraestructura** promedio — hay quien reporta 50 — y el costo es el criterio número uno al elegir herramienta por tercer año consecutivo. En LATAM, con presupuestos en soles, ese porcentaje duele doble. Fin de los números. Ahora, la historia."
→ Pragmatic Engineer 2023 · Grafana Surveys 2025/26

### S7 — Tesis [3:00]
"Esta charla es esa noche, de las 7 de la tarde a las 3 de la mañana. Y la vamos a pasar con tres cosas que esa vez no teníamos: un stack open source que lo ve todo, un cerebro que investiga por ti, y control humano para que no haga tonterías. Lo tercero es lo que separa esta charla del hype."

### S8 — Elenco [3:45]
Recorrer la tabla en ~60 s, una línea por pieza. Cierre: "Todo esto es open source o estándar abierto — menos el modelo, que es intercambiable. Y eso es justo el punto."

### S9 — La escena montada [5:00]
"Nada de esto se instaló la noche del incidente. Dos comandos, semanas antes: tofu apply, y Argo CD sincroniza el resto. Cero dólares en licencias. Y no estamos solos: 77% de la industria ya considera clave el open source en observabilidad."
→ **$0 licencias · 77% OSS** (Grafana 2026)

### S10 — 7:31 p.m. [6:30]
"Siete y treinta y uno. Suena el celular. Ni llegaste a la cena. Todos conocemos la noche que se viene: kubectl, grep, dashboards, hasta las 2 o 3 de la mañana. Esa noche es esta charla. Pero hoy hay una diferencia: alguien más ya estaba mirando."

### S11 — K8sGPT [7:00]
"K8sGPT: lee los errores del cluster y los explica en español. Proyecto de la CNCF — la misma fundación detrás de Kubernetes. Funciona con más de 13 modelos, locales o en la nube. Y el punto clave: diagnostica y sugiere. NO aplica cambios."

### S12 — 7:33 p.m., diagnóstico solo [8:00]
"Dos minutos después del page, esto ya estaba en pantalla: 'la imagen no existe; así se arregla'. Antes de que encuentres tus lentes. Este pantallazo es real, de mi cluster — y no me lo crean: al final de la charla lo rompemos en vivo."

### S13 — kagent [9:30]
"Saber qué pasó es la mitad. Alguien tiene que investigar el resto — y no tienes que ser tú. kagent: agentes de IA que viven dentro del cluster. Los defines en YAML como cualquier recurso, y usan herramientas de verdad — kubectl, Prometheus, Argo CD — por un protocolo estándar que se llama MCP. Proyecto CNCF, creado por Solo.io, el equipo detrás de Istio."
(Una frase, si hay tiempo: "Existen vecinos: HolmesGPT, kubectl-ai, Grafana Assistant. Cada uno tiene su lugar; lo mío es el stack completo abierto con control humano.")

### S14 — El agente investiga [10:30]
"Le pregunté en español: ¿por qué falla el pod y qué dice Prometheus del CPU? Él decidió qué herramientas usar, consultó kubectl y Prometheus por su cuenta, y respondió: causa raíz y propuesta. Ya no leo dashboards a las 3 de la mañana — alguien los lee por mí."

### S15 — El versus [11:30]
"Y aquí la pelea de fondo del 2026: ¿necesitas pagarle al modelo más caro del mundo para un pod roto? ¿O el open source ya alcanza? Cambiar de cerebro es un campo en un YAML: mismo agente, mismas herramientas, solo cambia quién piensa. No opinemos. Midámoslo: 42 rounds."

### S16 — Divider benchmark [12:15]
"Seis incidentes clásicos de Kubernetes — imagen rota, CrashLoop, OOM, config fantasma, probe rota, pod imposible de programar — por siete modelos, del 4B gratis en mi laptop hasta Claude Opus. Todo medido del tráfico real del agente: tokens, latencia, herramientas, costo a precio oficial de API."

### S17 — Resultados [13:00 — DETENERSE AQUÍ, es LA slide]
"Tres lecturas. Uno: el modelo local, gratis, resuelve la mitad — para triage nocturno no es poco. Dos: los open source hosteados — GLM, Kimi — igualan a Claude en estos incidentes: 6 de 6, por un centavo y medio por diagnóstico. Un quinto del precio. Tres: los Claude no ganan aquí en aciertos — ganan en disciplina: Sonnet 5 resuelve en un paso y medio, sin dar vueltas. Y el dato que más me gustó: TODAS las corridas de Claude juntas costaron 88 centavos."
→ Caveats EN VOZ ALTA: "6 incidentes estándar, puntaje revisado por mí, y Kimi es un modelo para código."

### S18 — MiniMax [15:00]
"Mención especial: MiniMax. Acertó 5 de 6… pero mírenlo: hasta 18 pasos y 39 mil tokens en un solo diagnóstico. Llegó a la respuesta. Nadie sabe cómo." (pausa para el meme) "¿Qué significa esto? Siguiente slide."

### S19 — ¿Qué le pasó a MiniMax? [15:30]
"En agentes no pagas por respuesta: pagas precio por token POR pasos. Cada vuelta extra son tokens. MiniMax es 3–4 veces más barato por token que GLM — y terminó costando casi lo mismo por diagnóstico. Un modelo barato pero caótico te sale igual que uno caro y directo. La disciplina importa tanto como el precio."

### S20 — La lección [16:30]
"La lección grande: no llames al SOTA para cada incidente. Los modelos open source van 3 o 4 meses detrás de los mejores — Epoch AI. De los 13 modelos con mejor relación precio-inteligencia, 9 son open source: lo mismo, a entre la mitad y un sexto del precio — Artificial Analysis. Y a capacidad constante, la inferencia se abarata 10 veces por año. El propietario top, para lo que nadie ha visto antes. El open source, para el turno de noche."

### S21 — ¿Ya resolvió la IA el on-call? No. [18:00]
"Y para que no me acusen de vender humo: no, la IA no resolvió SRE. Cuando IBM pone agentes contra incidentes reales, complejos, abiertos — resuelven uno de cada ocho. Los mejores modelos del mundo no llegan ni a la mitad diagnosticando Kubernetes. Lo que yo mostré son los fallos de manual — esos sí ya se diagnostican solos, y por centavos. La frontera sigue lejos. El piso ya es útil."
→ **~1 de cada 8** (ITBench) · **<50%** (ITBench-AA 2026) · **mitigación ≤54.5%** (AIOpsLab)

### S22 — 1:58 a.m., ¿lo dejamos actuar? [19:30]
"Una cincuenta y ocho. El fix está listo. ¿Lo dejamos aplicarlo solo? Todavía no — y quien les diga lo contrario, les está vendiendo algo. Gartner le pone número: más del 40% de los proyectos de agentes de IA van a ser cancelados antes de 2028. El freno que sí funciona hoy: un humano aprueba antes de tocar el cluster, y permisos de solo lectura por defecto. kagent trae esa aprobación integrada."
(Si preguntan por qué 1:58 si el diagnóstico llegó a las 7:33: "porque un incidente real no es un pod roto — hubo hipótesis, pruebas, un rollback. La diferencia es qué hice yo esas horas: decidir, no grepear.")

### S23 — Tres preguntas sin respuesta [20:30]
"La frontera abierta de 2026: ¿quién ES este agente? ¿Qué puede tocar? ¿Quién audita lo que hizo a las 3 de la mañana? Con humanos esto está resuelto hace años: usuarios, RBAC, audit log. Con agentes, no existe todavía. Hay gente trabajando: MCP ya está en la Linux Foundation, existe un OWASP Top 10 de MCP — en beta — y SPIFFE para identidad. Decir 'esta capa no existe del todo' es la respuesta correcta hoy. Si alguien les dice que ya la resolvió: desconfíen."

### S24 — DEMO EN VIVO [21:30]
"No me crean nada de lo que vieron. Rompámoslo juntos, aquí, sin internet." → `kubectl run roto --image=nginx:noexiste` → `k8sgpt analyze --explain --filter Pod --namespace default --language spanish`. Mientras responde: "Esto corre 100% en mi laptop, con un modelo de 4 mil millones de parámetros, gratis. El WiFi de la conferencia no me puede arruinar la demo."
[Si falla: clip de respaldo, sin drama: "por eso los SRE tenemos backups".]

### S25 — 2:47 a.m. [23:30]
"Dos cuarenta y siete de la mañana. Fix aprobado, cluster en verde. Ahora sí: a dormir. Así termina la noche — y las horas del medio las pasaste decidiendo, no grepeando. Esa es la versión honesta de 'el SRE que nunca duerme': el que no duerme es el agente. Tú sí. Todo está en el repo: las dos rutas — laptop gratis y AWS —, el benchmark completo, el guion de comandos, y la fuente de cada número que vieron. Una tarde y lo tienen corriendo."

### S26–27 — Gracias + fuentes [24:30]
"Gracias. ¿Preguntas?" → dejar S27 (fuentes con links) proyectada durante el Q&A.

---

## 3. Banco de datos por fuente (para improvisar y para Q&A)

### CNCF Annual Cloud Native Survey 2025 (ene-2026)
- 82% de usuarios de contenedores corre K8s en producción (66% en 2023).
- 66% de orgs con GenAI la corren sobre K8s · solo 7% despliega a diario · 47% "ocasionalmente".
- 44% aún NO corre AI/ML sobre K8s ("early stage of AI production maturity").
- 98% de las orgs encuestadas ya adoptó técnicas cloud native; 59% dice que "casi todo" su dev+deploy ya es cloud native.

### Splunk / Oxford Economics — Hidden Costs of Downtime (2ª ed., may-2026)
- $600B/año Global 2000 · $15,000/minuto (~$900k/hora) · $95M/año de revenue perdido por org.
- vs 1ª ed. (jun-2024): $400B · $9,000/min · 9% de las utilidades · 75 días para recuperar el revenue. **El delta $400B→$600B en 2 años es citable por sí solo.**

### New Relic — Observability Forecast 2025 (sep-2025)
- Outage de alto impacto: mediana **$2M/hora** (~$33k/minuto); mediana anual $76M.
- Con observabilidad full-stack: baja a $1M/hora; detección media 28 min (7 min más rápido); 23% vs 40% sufren outages de alto impacto semanales.
- 41% de los líderes se entera de los outages por "medios ineficientes" (chequeos manuales, quejas de usuarios).

### ITIC 2024
- >90% de empresas medianas/grandes: 1 hora de downtime ≥ $300,000. 41%: $1–5M+.

### Catchpoint — The SRE Report (2024/2025/2026)
- Toil mediano: 25% → 30% → 34% (tres años subiendo).
- 2026: solo 26% mide si sus mejoras de performance afectan revenue/NPS; 49% dice que la IA ya redujo su toil.

### NeuBird — State of Production Reliability 2026 (n=1,039; ⚠️ vendor de AI SRE)
- 78% tuvo ≥1 incidente donde NINGUNA alerta disparó.
- 44% tuvo un outage ligado a alertas suprimidas o ignoradas.
- 93% necesita 3+ ingenieros por incidente con impacto de negocio; la mayoría gasta 40%+ del tiempo en incidentes.

### Grafana Labs — Observability Surveys (2025, 2026)
- Observabilidad = 17% promedio del gasto de infraestructura (mediana y moda: 10%; hay casos de 50%+).
- Costo = criterio #1 de selección por 3er año (65%); 37% "costos muy altos", 29% "impredecibles".
- 77% valora open source/estándares abiertos; 65% invierte en Prometheus Y OpenTelemetry a la vez.
- 30% cita alert fatigue como obstáculo #1 en respuesta a incidentes.

### La factura Datadog / Coinbase (Pragmatic Engineer, 2023)
- Cadena: earnings call Q1-2023 ("large upfront bill que no se repitió") → analista JPM calcula ~$65M → CFO confirma "a crypto company" → Pragmatic Engineer confirma Coinbase con sus ingenieros.
- Final: Coinbase montó stack propio Grafana + Prometheus + ClickHouse.
- ⚠️ Decir siempre: estimación de analista, cubría uso de 2021.

### PagerDuty — State of Digital Operations 2025
- 88% de ejecutivos anticipa un incidente mayor de TI en los próximos 12 meses; 37% reporta pérdidas directas de revenue por incidentes.

### ITBench (IBM Research, ICML 2025) + ITBench-AA (Artificial Analysis, may-2026)
- Agentes con modelos SOTA: **11.4%** de escenarios SRE resueltos (ICML, 102 escenarios; 13.8% en el arXiv v1).
- ITBench-AA (59 tareas SRE K8s): al lanzamiento TODOS los frontier <50% — Claude Opus 4.7: 47%, GPT-5.5: 46%. (Leaderboard vivo: ya va en ~56%.)
- Dato fino: más vueltas ≠ mejor — GPT-5.5 promedió 31 turnos con 46% vs Gemini 3.1 Pro 83 turnos con 30%. **Mismo patrón que MiniMax en mi benchmark.**

### AIOpsLab (Microsoft Research, dic-2024)
- 48 problemas cloud-ops sobre microservicios K8s: mejor agente 59.3% global; detección 100%, RCA ≤45.5%, mitigación ≤54.5%. "Mitigation proved the most challenging."

### OpenRCA (ICLR 2025) y Cloud-OpsBench (feb-2026)
- OpenRCA: 335 fallas reales, 68 GB de telemetría — el mejor (Claude 3.5 con agente RCA dedicado): 11.34%.
- Cloud-OpsBench: 452 casos full-stack K8s — RCA top-1 entre 21% y 73%; el mejor fue **DeepSeek-V3.2 (open source)**. ⚠️ preprint sin peer review.

### Microsoft en producción (ICSE 2023, EuroSys 2024)
- 40,000+ incidentes de 1,759 servicios: >70% de los dueños de incidentes puntuó ≥3/5 las recomendaciones del LLM.
- RCACopilot: accuracy hasta 76.6% en incidentes reales; componente en producción en Microsoft 4+ años. **Útil para "esto no es teoría: Microsoft lo opera hace años".**

### Gartner (2024–2026)
- Para 2028: 33% del software empresarial con agentic AI (<1% en 2024); 15% de decisiones diarias tomadas de forma autónoma.
- >40% de proyectos agentic AI cancelados para fin de 2027 (costos, valor difuso, riesgo). "Agent washing": de miles de vendors, ~130 reales.
- $234B de gasto en software empresarial "en riesgo" por agentic AI (jul-2026).
- 40% de las apps empresariales tendrán agentes task-specific a fin de 2026 (<5% en 2025).

### El gap open vs closed (Epoch, Artificial Analysis, a16z, AI Index)
- Epoch AI: open weights a ~3–4 meses del frontier cerrado (ene–may 2026; medición previa: ~3 meses).
- Artificial Analysis (abr-2026): 9 de 13 modelos en la frontera Pareto precio-inteligencia son open weights; "inteligencia comparable a ½–⅙ del precio"; el mejor open pasó de 22 → 54 puntos de su índice en UN año.
- Gap residual agéntico: TerminalBench Hard, open 43–46% vs 61% del mejor cerrado.
- a16z "LLMflation": a capacidad constante, el costo cae ~10×/año; calidad GPT-3: $60/Mtok (2021) → $0.06 (2024) = 1,000× en 3 años.
- Stanford AI Index: inferencia nivel GPT-3.5 cayó 280× (nov-22→oct-24). Gap open-closed en arena: 8% → 1.7% (2024) → re-abrió a ~3.3% (2025). **Citar el arco completo.**

### GLM-5.2 (jun-2026, licencia MIT)
- SWE-bench Pro: 62.1% vs GPT-5.5 58.6% y Gemini 3.1 Pro 54.2%. Terminal-Bench 2.1: 81.0 vs 85.0 de Claude Opus 4.8. API: $1.40/$4.40 por Mtok.
- ⚠️ El propio Z.ai reportó tendencia a reward hacking en evals. **Es el mismo modelo que sacó 6/6 en mi benchmark.**

### Benchmark propio (demo/bench/, 42 corridas, jul-2026)
| Modelo | Aciertos | Pasos | Seg | $/diag correcto |
|---|---|---|---|---|
| Qwen 3.5 4B local | 3/6 | 1.8 | 175 | $0 |
| GLM 5.2 | 6/6 | 3.0 | 10 | ~1.3¢ |
| MiniMax M3 | 5/6 | 13.2 | 49 | ~1.6¢ |
| Kimi K2.7-code | 6/6 | 2.5 | **7** | ~1.4¢ |
| Sonnet 4.6 | 6/6 | 2.3 | 14 | ~3¢ |
| Sonnet 5 | 6/6 | **1.5** | 11 | ~4¢ |
| Opus 4.8 | 6/6 | 2.0 | 16 | ~7.7¢ |
- Todas las corridas de Claude juntas: **$0.88**. MiniMax: hasta 39k tokens/diagnóstico (los directos ~5k).
- Anécdota de guerra para Q&A: la primera matriz completa se envenenó porque un port-forward compartido apuntaba al cluster equivocado — 36 de 42 corridas preguntaban al agente incorrecto. Moraleja: el benchmark ahora crea sus propios túneles. (Y es un gran ejemplo de por qué "medir" > "confiar".)

### Proyectos (estado verificado jul-2026)
- OpenTelemetry: graduado CNCF 21-may-2026; 12,000+ contributors de 2,800+ empresas; 2ª velocity de CNCF tras Kubernetes.
- K8sGPT: CNCF Sandbox, v0.4.36, ~8,000 stars. Tagline real: "scanning, diagnosing and triaging issues in simple English".
- kagent: CNCF Sandbox, donado por Solo.io, API v1alpha2, 3,300+ stars, ~160 contributors.
- MCP: donado por Anthropic a la Agentic AI Foundation (Linux Foundation) el 9-dic-2025; co-fundada por Anthropic, Block y OpenAI.
- OWASP MCP Top 10: existe, en beta (MCP01–MCP10:2025).
- Prometheus 3: receptor OTLP nativo (`--web.enable-otlp-receiver`).

### Citas célebres (verificadas contra fuente primaria)
- **"Hope is not a strategy."** — dicho tradicional SRE; epígrafe del cap. 1 del libro de Google SRE (sre.google/sre-book/introduction). *Dónde usarla: al abrir la parte honesta (S22) o como remate del cierre.*
- **"Everything fails, all the time."** — Werner Vogels, CTO de Amazon (keynote re:Invent; liveblog oficial de AWS 2020). *Dónde: S10, cuando suena el celular — "no es mala suerte: es la regla".*
- **"For SRE, automation is a 'force multiplier,' not a panacea."** — Google SRE book, cap. 7 ("The Evolution of Automation at Google"). *Dónde: S22 — el agente multiplica la fuerza; la puntería sigue siendo tuya.*
- **"Toil tends to expand if left unchecked and can quickly fill 100% of everyone's time."** y "si el trabajo escala linealmente con el tamaño del servicio, probablemente es toil" — cap. 5 "Eliminating Toil". *Dónde: S4, para rematar el 34%.*
- **"Roughly 70% of outages are due to changes in a live system."** — Google SRE book, cap. 1. ⚠️ Es del libro (2016), no un stat 2025 — citarlo como "el libro de Google ya decía".
- **Uptime Institute 2025**: cerca del **40% de las organizaciones** sufrió un outage mayor por error humano en los últimos 3 años; de esos, **85%** se debe a no seguir procedimientos o a fallas del proceso mismo. ⚠️ Ojo al fraseo: es "40% de las organizaciones", NO "40% de los outages". *Dónde: refuerza el caso de automatizar el diagnóstico y frenar la acción.*

---

## 4. Q&A — respuestas preparadas

- **"¿No es peligroso darle kubectl a un LLM?"** → Por eso el agente corre read-only por defecto, con aprobación humana antes de cualquier acción (kagent HITL). Y por eso dediqué una slide a la frontera de identidad/authz: es EL problema abierto (OWASP MCP Top 10, SPIFFE).
- **"¿Tu benchmark no es muy chico?"** → Sí: 6 incidentes canónicos, n=1 por celda, puntaje revisado por mí. Para escenarios abiertos está ITBench (11%). El punto no es "la IA resuelve todo": es que la franja de manual ya se diagnostica por centavos. Todo es reproducible: `demo/bench/bench.py`.
- **"¿Y los datos sensibles del cluster que le mandas al modelo?"** → Ruta local: Ollama en tu laptop, nada sale. Ruta nube: eliges proveedor y región (Bedrock = tu cuenta AWS). Y es exactamente el tipo de riesgo que cataloga el OWASP MCP Top 10.
- **"¿Por qué no usar el AI SRE de Datadog/vendor X?"** → Claims tipo "90% faster" sin metodología pública. Este stack es verificable de punta a punta — y les acabo de mostrar el costo real por diagnóstico.
- **"¿Costo en producción?"** → El costo escala con incidentes, no con el tamaño del cluster: centavos por diagnóstico (mi benchmark). El modelo caro guárdalo para el incidente raro.
- **"¿Qwen/GLM/Kimi alucinan?"** → En mis 42 corridas el 4B falló 3 de 6 (por eso gratis ≠ gratis); los hosteados no fallaron en estos escenarios, pero Z.ai mismo reporta reward hacking en GLM. Por eso: control humano SIEMPRE.
- **"¿Por qué OpenTofu y no Terraform?"** → Licencia (Terraform es BSL/IBM), y features propias: state encryption, OCI registry. Ya divergieron de verdad.
- **"¿K8sGPT y kagent se integran entre sí?"** → De fábrica no se llaman: corren en paralelo (ojos y manos). Tres puntos de contacto: (1) K8sGPT expone su análisis como servidor MCP (`k8sgpt serve --mcp`, 12 tools incl. `analyze`) y kagent lo consume registrándolo con el CRD `RemoteMCPServer` — los ojos se vuelven herramienta de las manos; (2) el operator de K8sGPT escribe CRs `Result` que cualquier agente lee con kubectl — el cluster como bus de datos; (3) comparten backend LLM. kagent NO trae tool k8sgpt integrada (catálogo: argo, cilium, helm, istio, k8s, kubescape, prometheus, utils).
- **"¿Puedo usar mi agente LangGraph/CrewAI con kagent?"** → Sí: `Agent` CRD con `spec.type: BYO` — tu agente empaquetado como contenedor que hable A2A (`spec.byo.deployment.image`), y kagent lo expone en `/api/a2a/{ns}/{nombre}/`. El runtime nativo es el ADK de Google (Python; hay variante Go nueva). A2A es el mismo protocolo con el que mi panel y mi benchmark instrumentaron al agente.
