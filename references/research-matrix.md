# Gateway Research Matrix

## Contents

1. Date window
2. Topic buckets
3. Event and source coverage
4. Candidate schema
5. Verification and selection

## Date Window

Resolve the current date from the system clock in `Asia/Shanghai`. For run date D:

- start: D-2 at `00:00:00+08:00`;
- end: D-1 at `23:59:59+08:00`.

Use the original publication or event time. Search crawl time, repost time, newsletter delivery time, and aggregator timestamps do not qualify. An older source may support background but must use `source_role: background` and cannot be the two-day event.

## Topic Buckets

Run at least one focused Chinese query and one focused English query for every bucket. Combine the exact date range with release, incident, security, paper, benchmark, standard, or engineering-analysis terms.

1. **Gateway architecture**: 网关架构, gateway architecture, traffic governance, control plane, data plane.
2. **L4 and accelerated networking**: 四层网关, load balancer, DPDK, eBPF, XDP, SmartNIC, DPU.
3. **L7 and API gateway**: 七层网关, API Gateway, Ingress, Service Mesh, Envoy, NGINX, HAProxy, Kong, APISIX, Higress, Traefik, Istio, Kubernetes Gateway API.
4. **AI and LLM gateway**: AI Gateway, LLM Gateway, model routing, semantic cache, rate limits, cost, audit, prompt security.
5. **Inference gateway and engines**: 推理网关, inference routing, scheduling, continuous batching, KV cache, heterogeneous compute, Kubernetes Inference Gateway, vLLM, SGLang, TensorRT-LLM.
6. **Agent and MCP gateway**: Agent Gateway, MCP Gateway, A2A, tool permissions, workload identity, policy, governance.
7. **P4 programmable data plane**: P4, P4Runtime, Tofino, programmable switch, programmable gateway.
8. **NPL programmable networking**: NPL gateway, NPL data plane, network programming language. Exclude unrelated natural-language-processing results.

## Event and Source Coverage

Search product releases, open-source changes, outages, security incidents, CVEs, papers, performance studies, standards, industry reports, acquisitions, partnerships, and substantial engineering articles.

Prefer sources in this order:

1. Official release, repository, paper, standard, CVE/NVD record, or status page.
2. Named engineering team or author with reproducible technical evidence.
3. Reputable technical or industry publication linking to the primary source.
4. Aggregator or repost only for discovery; replace it with the canonical source.

Do not browse only vendor release notes. Use available live search skills and direct official/GitHub pages. For Chinese discovery, include high-quality technical media and WeChat article search when available, then trace claims to primary material.

## Candidate Schema

Write `RUN_DIR/sources.json` as UTF-8 JSON, where `RUN_DIR` is the absolute article directory under `/Users/tom/Desktop/substack`:

```json
{
  "window": {
    "timezone": "Asia/Shanghai",
    "start": "2026-07-13T00:00:00+08:00",
    "end": "2026-07-14T23:59:59+08:00"
  },
  "selected_topic": "Kubernetes Inference Gateway routing update",
  "candidates": [
    {
      "title": "Inference Gateway project update",
      "url": "https://gateway-api-inference-extension.sigs.k8s.io/",
      "published_at": "2026-07-14T09:00:00+08:00",
      "source_class": "primary",
      "source_role": "event",
      "topic_bucket": "inference-gateway",
      "claim": "The project published a routing update in the selected window.",
      "verification_urls": [
        "https://github.com/kubernetes-sigs/gateway-api-inference-extension"
      ],
      "verification_status": "verified",
      "risk_notes": ""
    }
  ]
}
```

Use `verification_status` values `verified`, `partial`, or `unverified`. Only `verified` sources count toward the publication gate. Include at least two verified sources, at least one verified primary source, and at least one verified event source whose original publication time is inside the two-day window.

## Verification and Selection

- Merge reposts of one event into one candidate.
- Verify dates, versions, CVEs, benchmark conditions, performance values, financing, market figures, and strong causal statements.
- Delete unsupported numbers or weaken the wording. Do not substitute model inference for evidence.
- Limit one vendor, project, or event to two leading candidates.
- Rank internally by time relevance, source credibility, technical information gain, industry impact, Chinese practitioner value, mechanism depth, and illustration value.
- Select exactly one topic. Do not expose a mechanical score in the article.
- In `candidates.md`, record the search window, bucket coverage, selected topic, selection rationale, leading rejected topics, and information gaps.
- If no candidate supports a useful focused article, preserve research artifacts and stop.
