---
marp: true
theme: default
paginate: true
lang: es
---

# El SRE que nunca duerme
### Agentes de IA sobre tu stack de observabilidad open source en Kubernetes

Andrés Zeballos · KCD Lima 2026

<!-- Notas: Me presento en 20 segundos. Todo lo que voy a mostrar está en un repo público; el QR va al final. -->

---

## Casi nadie lo tiene en producción

- 66% de las organizaciones corre GenAI sobre Kubernetes.
- 7% lo opera en producción todos los días.
- El resto sigue atascado en pilotos de día uno.

Y en LATAM pagamos SaaS de observabilidad caro sin saber que el stack abierto ya aguanta producción.

<!-- Notas: Ese hueco entre el 66 y el 7 es de lo que trata la charla. No vengo a mostrarles que la IA "funciona"; eso ya lo vieron mil veces. Vengo a mostrar cómo se cruza ese hueco sin que el agente haga una tontería en tu cluster. -->

---

## La idea en tres movimientos

1. Constrúyelo abierto.
2. Dale un cerebro.
3. Mantenlo con correa.

<!-- Notas: Abierto: Prometheus, Grafana, Fluent Bit, todo CNCF, con OpenTofu y Argo CD. Cerebro: K8sGPT y Kagent. Correa: guardrails y un humano que aprueba. El tercer punto es el que separa esta charla de una de puro hype. -->

---

## El stack abierto

- Métricas: Prometheus 3, que ya recibe OTLP nativo.
- Dashboards y alertas: Grafana 12.
- Logs: Fluent Bit 4, que ahora también habla OpenTelemetry.
- El pegamento: OpenTelemetry, graduado en CNCF en mayo de 2026.

IaC con OpenTofu. GitOps con Argo CD. Reproducible.

<!-- Notas: Presentar este stack sin nombrar OpenTelemetry en 2026 se nota. OTel es el estándar por el que entra la telemetría, y Prometheus 3 lo recibe directo. Y ojo con OpenTofu: ya no es "el fork de Terraform", trae cosas que Terraform no tiene, como cifrado de estado. -->

---

## [CLIP] De cero a stack corriendo

`tofu apply`, y Argo CD sincroniza el resto solo.

<!-- Notas: Clip corto: OpenTofu levanta la base y Argo CD pone el stack en verde sin que yo toque nada. No lo corro en vivo por tiempo; el repo lo hace igual en tu máquina. -->

---

## K8sGPT: los ojos

Escanea el cluster y te explica los errores en lenguaje humano, en español.

- Proyecto CNCF Sandbox.
- 13+ backends de modelo, incluidos Bedrock y Anthropic.
- Diagnostica. No remedia.

<!-- Notas: Ese último punto importa. K8sGPT te dice qué pasa y por qué, pero no toca el cluster. Para actuar necesitas otra pieza, y ahí entra Kagent. -->

---

## [DEMO EN VIVO] Rompo un pod, K8sGPT lo explica

```
kubectl run roto --image=nginx:noexiste
k8sgpt analyze --explain
```

<!-- Notas: Este es el único momento en vivo, y corre local con Qwen en Ollama, offline, así que el WiFi de la conferencia no me lo puede arruinar. Rompo el pod y en segundos K8sGPT me dice que la imagen no existe, con la causa y el arreglo, en español. -->

---

## Kagent: las manos

Agentes como recursos nativos de Kubernetes.

- CRDs en `kagent.dev/v1alpha2`: defines el agente en YAML.
- Herramientas por MCP: kubectl, Prometheus, Argo CD.
- CNCF Sandbox, donado por Solo.io, el equipo detrás de Istio.

<!-- Notas: Es uno de los proyectos agénticos que más rápido crece en CNCF. No digo "el más activo", porque eso no se sostiene y este público lo sabe. Compárenlo con HolmesGPT, kubectl-ai o Grafana Assistant: cada uno tiene su lugar; lo mío es el stack completo abierto con acción gobernada. -->

---

## [CLIP] El agente lee el cluster y las métricas

"¿Por qué falla el pod roto y qué dice Prometheus del CPU?"

El agente junta el estado del cluster con las métricas y propone una acción.

<!-- Notas: Le pregunto en lenguaje natural y él decide qué herramientas usar: consulta kubectl y Prometheus por MCP, y responde con causa y propuesta. Ya no estoy leyendo un dashboard; alguien lo lee por mí. -->

---

## El cerebro es intercambiable

Cambias un campo del `ModelConfig` y el mismo agente usa otro modelo.

| Cerebro | Costo por millón de tokens (in / out) |
|---|---|
| Qwen local (Ollama) | 0 |
| Claude Sonnet 4.6 (Bedrock) | 3 / 15 |
| Claude Opus 4.8 (Bedrock) | 5 / 25 |

<!-- Notas: [CLIP del swap] Cambio el provider de Ollama a Bedrock y vuelvo a aplicar. Mismo Agent, mismo prompt. Local para experimentar sin gastar; Claude cuando necesitas razonamiento de verdad. El stack no cambia; tú eliges la cuenta. -->

---

## Día 2: la parte honesta

- K8sGPT no remedia solo. La remediación autónoma sigue siendo aspiración.
- Guardrails de Kagent: aprobación humana antes de actuar.
- Permisos mínimos con RBAC, solo lectura por defecto.

El SRE que nunca duerme todavía necesita que alguien despierto lo supervise.

<!-- Notas: Si les vendo clusters que se auto-reparan solos, les estoy mintiendo. Lo honesto en 2026 es: el agente ve, explica y propone; el humano aprueba. Eso sí se puede llevar a producción hoy. -->

---

## Lo que todavía no está resuelto

La identidad y la autorización de los agentes.

- MCP pasó a la Linux Foundation en diciembre de 2025.
- Ya existe un OWASP MCP Top 10.
- Identidad de agente con SPIFFE/SPIRE (kagenti), políticas con agentgateway.

Decir "esta capa todavía no existe del todo" es la respuesta correcta hoy.

<!-- Notas: Esta es la frontera abierta, y es donde conviene estar mirando. Nadie tiene resuelto quién es un agente, qué puede hacer y cómo se audita lo que hizo. Si alguien les dice que sí lo tiene resuelto, desconfíen. -->

---

## Replícalo hoy

Todo está en el repo, con las dos rutas: local con kind, o EKS con Bedrock.

> (QR al repositorio)

Gracias. ¿Preguntas?

<!-- Notas: El repo trae el guion de comandos, los manifests ya verificados contra los docs actuales, y el OpenTofu del camino cloud. Lo pueden levantar esta misma tarde. -->
