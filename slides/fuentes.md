# Fuentes verificadas — El SRE que Nunca Duerme (KCD Lima 2026)

> Verificadas 2026-07-15 vía fetch directo o búsqueda con URL confirmada (nunca memoria de entrenamiento).
> Formato: **dato citable** → fuente, fecha, URL, caveat.

---

## 1. El gap de producción (hook central)

- **82% de usuarios de contenedores corre Kubernetes en producción** (vs 66% en 2023).
- **66% de las orgs que hostean GenAI usan Kubernetes** para sus inference workloads.
- **Solo 7% despliega modelos a diario; 47% ocasionalmente.** 44% aún no corre AI/ML en K8s.
- Fuente: CNCF Annual Cloud Native Survey 2025 (anuncio 2026-01-20).
  https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/
- ⚠️ Wording oficial: "deploy occasionally" — NO decir "atascados en pilotos día-1" como cita; usarlo solo como interpretación propia.

## 2. Cuánto cuesta dormir (downtime)

- **$600 mil millones/año** le cuesta el downtime no planeado a la Global 2000 (**+50% en 2 años**); **$15,000/minuto** (~$900k/hora); $95M/año de revenue perdido por org.
  — Splunk (Cisco) / Oxford Economics, *The Hidden Costs of Downtime* 2ª ed., 2026-05-19. Encuesta a 2,000 ejecutivos, 20 países, **incluye LATAM**.
  https://www.prnewswire.com/news-releases/the-600-billion-wake-up-call-new-splunk-research-reveals-downtime-is-a-systemic-business-crisis-302774919.html
- **Outage de alto impacto: mediana $2M/hora**; con observabilidad full-stack baja a $1M/hora. Detección media: 28 min con full-stack (7 min más rápido que sin).
  — New Relic *Observability Forecast 2025* (2025-09-17). https://newrelic.com/press-release/20250917
- **>90% de empresas medianas/grandes: 1 hora de downtime ≥ $300,000; 41% dice $1–5M+.**
  — ITIC Hourly Cost of Downtime Survey 2024. https://itic-corp.com/itic-2024-hourly-cost-of-downtime-report/

## 3. El dolor humano (toil / alertas / on-call)

- **Toil mediano: 34% del tiempo (2026) ← 30% (2025) ← 25% (2024).** Tres años subiendo.
  — Catchpoint/LogicMonitor, *The SRE Report 2026* (n=418) y *2025* (n=301).
  https://www.logicmonitor.com/press/the-sre-report-2026-reliability-is-being-redefined
  https://www.catchpoint.com/press-releases/the-sre-report-2025-highlighting-critical-trends-in-site-reliability-engineering
- **Google SRE: meta explícita de mantener el toil <50% del tiempo de cada SRE.**
  — *Site Reliability Engineering*, cap. "Eliminating Toil". https://sre.google/sre-book/eliminating-toil/
- **78% tuvo al menos un incidente donde NINGUNA alerta disparó; 44% tuvo un outage ligado a alertas suprimidas/ignoradas; 93% necesita 3+ ingenieros por incidente.**
  — NeuBird, *2026 State of Production Reliability* (n=1,039, abr-2026). ⚠️ NeuBird vende un AI SRE — atribuir claramente.
  https://www.businesswire.com/news/home/20260406439955/en/New-Study-Finds-Alert-Fatigue-Has-Become-a-Production-Reliability-Risk-and-Incident-Response-Alone-Is-No-Longer-Enough
- **30% cita alert fatigue como su obstáculo #1 en respuesta a incidentes.**
  — Grafana Labs, 4ª Observability Survey (2026-03-18, n=1,300+, 76 países).
  https://grafana.com/press/2026/03/18/grafana-labs-4th-annual-observability-survey-reveals-a-field-at-a-crossroads-ai-economics-complexity-and-the-enduring-power-of-open-source/

## 4. El costo de observar (ángulo LATAM / OSS)

- **La factura Datadog de ~$65M**: revelada en earnings call Q1-2023 ("large upfront bill"), ~$65M calculado por analista de JP Morgan, CFO confirmó "a crypto company", Pragmatic Engineer confirmó que era **Coinbase** — que luego **migró a stack propio Grafana + Prometheus + ClickHouse**.
  — Gergely Orosz, The Pragmatic Engineer, 2023. https://blog.pragmaticengineer.com/datadog-65m-year-customer-mystery/
  ⚠️ $65M es estimación de analista (no cifra oficial de Datadog); la factura cubría uso 2021.
- **Observabilidad = 17% promedio del gasto total de infraestructura de cómputo** (mediana 10%; algunos 50%+). Costo = criterio #1 de selección de herramienta por 3er año (65%).
  — Grafana Labs Observability Survey 2025 (n=1,255). https://grafana.com/blog/observability-survey-takeaways/
- **77% dice que open source / estándares abiertos son importantes en observabilidad; 65% invierte en Prometheus Y OpenTelemetry a la vez.**
  — Grafana Survey 2026 (URL de prensa arriba).

## 5. Estado del arte: agentes LLM como SRE (contexto del benchmark propio)

- **ITBench (IBM Research, ICML 2025): los agentes con modelos SOTA resuelven solo 11.4–13.8% de escenarios SRE** (94–102 escenarios; 13.8% en arXiv v1, 11.4% en camera-ready ICML).
  https://arxiv.org/abs/2502.05352 · https://proceedings.mlr.press/v267/jha25a.html · https://github.com/itbench-hub/ITBench
- **ITBench-AA leaderboard (Artificial Analysis, 2026-05-27, 59 tareas SRE K8s): al lanzamiento TODOS los modelos frontier <50%** (Claude Opus 4.7: 47%, GPT-5.5: 46%).
  https://artificialanalysis.ai/evaluations/itbench-aa
  ⚠️ Leaderboard vivo (hoy el top va en 56.2%) — citar "menos de 50% al lanzamiento, mayo 2026".
- **AIOpsLab (Microsoft Research, dic-2024, 48 problemas en microservicios K8s): detección 100%, pero root-cause ≤45.5% y mitigación ≤54.5%.** "Mitigation proved the most challenging."
  https://www.microsoft.com/en-us/research/blog/aiopslab-building-ai-agents-for-autonomous-clouds/ · https://arxiv.org/abs/2501.06706
- **OpenRCA (ICLR 2025): el mejor modelo resolvió solo 11.34% de 335 fallas reales** (68+ GB de telemetría).
  https://github.com/microsoft/OpenRCA
- **Cloud-OpsBench (arXiv 2026-02-28, 452 casos, full-stack K8s): RCA top-1 entre 21% y 73%.**
  https://arxiv.org/abs/2603.00468 ⚠️ preprint fresco, sin peer review.
- **Microsoft ICSE 2023 (40,000+ incidentes, 1,759 servicios): >70% de los dueños de incidentes puntuó ≥3/5 las recomendaciones del LLM.**
  https://arxiv.org/abs/2301.03797
- **RCACopilot (EuroSys 2024): accuracy hasta 76.6% en incidentes reales de Microsoft; componente en producción 4+ años.**
  https://arxiv.org/abs/2305.15778
- **Datadog Bits AI SRE**: "90% faster", probado en 2,000+ ambientes. ⚠️ Marketing, sin metodología ni % de accuracy público. Usar solo como "la industria ya lo vende".
  https://www.datadoghq.com/product/ai/bits-ai-sre/

## 6. La parte honesta (Gartner)

- **"Para 2028, 33% del software empresarial incluirá agentic AI (desde <1% en 2024)"** — Gartner, 2024-10-21.
  https://www.gartner.com/en/newsroom/press-releases/2024-10-21-gartner-identifies-the-top-10-strategic-technology-trends-for-2025
- **"Más del 40% de los proyectos de agentic AI serán cancelados para fin de 2027"** (costos, valor difuso, controles de riesgo). Bonus: de miles de vendors "agentic", solo ~130 son reales ("agent washing").
  — Gartner, 2025-06-25. https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027
- **$234B de gasto en software empresarial "en riesgo" por agentic AI** — Gartner, 2026-07-01.
  https://www.gartner.com/en/newsroom/press-releases/2026-07-01-gartner-says-us-dollars-234-billion-in-enterprise-application-software-spend-is-at-risk-from-agentic-artificial-intelligence
- ⚠️ gartner.com bloquea fetch directo (403); wording verificado vía múltiples fuentes secundarias consistentes. URLs/títulos/fechas oficiales.

## 7. Proyectos del stack (slide de créditos / exactitud)

- **OpenTelemetry graduado CNCF: 2026-05-21.** 12,000+ contributors, 2,800+ empresas; 2ª mayor velocity tras Kubernetes.
  https://www.cncf.io/announcements/2026/05/21/cloud-native-computing-foundation-announces-opentelemetrys-graduation-solidifying-status-as-the-de-facto-observability-standard/
- **K8sGPT**: CNCF Sandbox, **v0.4.36** (2026-07-10), ~8,000 stars. "Diagnostica y sugiere, no aplica cambios."
  https://github.com/k8sgpt-ai/k8sgpt
- **Kagent**: CNCF Sandbox, donado por Solo.io, API **v1alpha2**, **3,312 stars / ~160 contributors** (GitHub API 2026-07-15; re-chequear antes de la charla).
  https://github.com/kagent-dev/kagent
- **MCP → Agentic AI Foundation (Linux Foundation): 2025-12-09.** Co-fundada por Anthropic, Block y OpenAI. ⚠️ Precisión: donado a la AAIF bajo la LF, no "a la LF" a secas.
  https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
- **OWASP MCP Top 10: existe, en beta** (MCP01:2025–MCP10:2025). https://owasp.org/www-project-mcp-top-10/
- **Prometheus 3: receptor OTLP nativo** (`--web.enable-otlp-receiver`). https://prometheus.io/docs/guides/opentelemetry/

## 8. Números propios (benchmark `demo/bench/`, 2026-07-15)

**6 incidentes × 7 cerebros = 42 corridas**, todo medido del wire A2A de kagent. Auto-scored (pendiente pase de veredictos humano).

| Cerebro | Aciertos | Pasos prom | Seg prom | Costo 6 diag |
|---|---|---|---|---|
| Qwen 3.5 4B (local) | 3/6 | 1.8 | 175 | $0 |
| GLM 5.2 | 6/6 | 3.0 | 10 | $0.080 |
| MiniMax M3 | 5/6 | 13.2 (39k tok) | 49 | $0.079 |
| Kimi K2.7-code | 6/6 | 2.5 | 7 | $0.083 |
| Sonnet 4.6 | 6/6 | 2.3 | 14 | $0.182 |
| Sonnet 5 | 6/6 | 1.5 | 11 | $0.235 |
| Opus 4.8 | 6/6 | 2.0 | 16 | $0.459 |

- Headlines: OSS hosteado (GLM/Kimi) = accuracy de Claude a **~1.3¢/diagnóstico** (2–6× más barato). El 4B local gratis resuelve la mitad. **Las 18 corridas de Claude juntas: $0.88.**
- ⚠️ Caveats a decir en voz alta: auto-scored, n=6 incidentes estándar, Kimi es code-tuned.

## 9. OSS alcanza al frontier (la lección "no llames al SOTA")

- **Los open weights van ~3–4 meses detrás del frontier cerrado** (Epoch Capabilities Index, ventana ene–may 2026; medición previa oct-2025: ~3 meses).
  https://epoch.ai/data-insights/open-closed-eci-gap · https://epoch.ai/data-insights/open-weights-vs-closed-weights-models
- **9 de los 13 modelos en la frontera de Pareto inteligencia-vs-precio son open weights**; "inteligencia comparable a los propietarios líderes a entre ½ y ⅙ del precio". Salto en un año: mejor open weight de 22 → 54 puntos de Intelligence Index.
  — Artificial Analysis, "Recent open weights model launches", 2026-04-30. https://artificialanalysis.ai/articles/recent-open-weights-model-launches
  ⚠️ El gap residual es agéntico: TerminalBench Hard, open 43–46% vs 61% del mejor cerrado — decirlo, es la parte honesta.
- **A capacidad constante, el costo de inferencia cae ~10× por año** ("LLMflation": GPT-3-quality pasó de $60/Mtok en 2021 a $0.06 en 2024 = 1,000× en 3 años).
  — a16z (Appenzeller), 2024-11-12. https://a16z.com/llmflation-llm-inference-cost/
- **AI Index (Stanford HAI)**: inferencia a nivel GPT-3.5 cayó **280×** entre nov-2022 y oct-2024 (ed. 2025). Gap open vs closed: 8% → 1.7% (2024) → **re-abrió a ~3.3% (2025, ed. 2026)** — citar el arco completo, no solo el 1.7%.
  https://hai.stanford.edu/ai-index/2025-ai-index-report · https://hai.stanford.edu/ai-index/2026-ai-index-report
- **GLM-5.2** (MIT license, jun-2026): SWE-bench Pro **62.1%** vs GPT-5.5 58.6% y Gemini 3.1 Pro 54.2%; Terminal-Bench 2.1: 81.0 vs 85.0 de Claude Opus 4.8. API $1.40/$4.40 por Mtok.
  https://www.datacamp.com/blog/glm-5-2 ⚠️ Writeup de números oficiales del vendor; Z.ai mismo reportó tendencia a reward hacking en evals.

## 10. Citas célebres y clásicos (verificados contra fuente primaria, 2026-07-17)

- **"Hope is not a strategy."** — epígrafe ("Traditional SRE saying"), Google SRE book cap. 1. https://sre.google/sre-book/introduction/
- **"Everything fails, all the time."** — Werner Vogels (CTO Amazon), keynote re:Invent; liveblog oficial AWS 2020. https://aws.amazon.com/blogs/aws/reinvent-2020-liveblog-werner-vogels-keynote/
- **"For SRE, automation is a 'force multiplier,' not a panacea."** — Google SRE book cap. 7. https://sre.google/sre-book/automation-at-google/
- **"Toil tends to expand if left unchecked and can quickly fill 100% of everyone's time."** — cap. 5. https://sre.google/sre-book/eliminating-toil/
- **"Roughly 70% of outages are due to changes in a live system."** — Google SRE book cap. 1 (⚠️ libro de 2016, no stat actual). https://sre.google/sre-book/introduction/
- **Uptime Institute, Annual Outage Analysis 2025**: ~40% de las **organizaciones** sufrió un outage mayor por error humano en 3 años; 85% de esos por procedimientos no seguidos o defectuosos. ⚠️ NO citar como "40% de los outages". Extra: la frecuencia/severidad de outages baja por 4º año consecutivo. https://uptimeinstitute.com/about-ui/press-releases/uptime-announces-annual-outage-analysis-report-2025

## ❌ Descartados (circulan en internet pero NO verificables)

- "~70% de SREs dice que el on-call impactó burnout/attrition" atribuido a Catchpoint SRE Report 2025 → **NO está en el PDF** (verificado con extracción de texto).
- "2,000 alertas/semana, solo 3% accionables" atribuido a PagerDuty → **sin fuente primaria**. Usar los números de NeuBird 2026 en su lugar.
