# CoreWeave EDA Event Source Plugins

This collection includes two standalone EDA event source plugins for use
with `ansible-rulebook`. No dependency on `ansible.eda` is required.

## Prerequisites

```bash
pip install ansible-rulebook aiohttp kubernetes>=28.1.0
```

## Webhook Event Source

Listens for HTTP POST requests from CoreWeave Grafana alerts,
Prometheus Alertmanager, or custom webhooks.

### Example Rulebook

```yaml
---
- name: React to CoreWeave alerts
  hosts: all
  sources:
    - stevefulme1.coreweave.webhook:
        host: 0.0.0.0
        port: 5000
        token: "{{ webhook_secret }}"

  rules:
    - name: Handle GPU node failure alert
      condition: event.coreweave.payload.status == "firing"
      action:
        run_playbook:
          name: handle_gpu_alert.yml

    - name: Log all incoming webhooks
      condition: event.coreweave.payload is defined
      action:
        debug:
          msg: "Received webhook: {{ event.coreweave.payload }}"
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | str | `0.0.0.0` | Listen address |
| `port` | int | `5000` | Listen port |
| `token` | str | None | Bearer token for authentication (optional) |

### Configuring CoreWeave Alerts

Point your CoreWeave Grafana Alertmanager webhook to:

```
http://<your-host>:5000/alerts
```

The event payload is available as `event.coreweave.payload`.

## Kubernetes Events Watcher

Watches Kubernetes events on a CKS cluster in real time. Useful for
reacting to node scaling, pod failures, and node pool changes.

### Example Rulebook

```yaml
---
- name: Monitor CKS cluster events
  hosts: localhost
  sources:
    - stevefulme1.coreweave.k8s_events:
        kubeconfig: "~/.kube/config"
        namespace: ""
        event_types:
          - ADDED
          - MODIFIED
        label_selector: ""

  rules:
    - name: Alert on node not ready
      condition: >-
        event.coreweave.event_reason == "NodeNotReady"
      action:
        run_playbook:
          name: remediate_node.yml

    - name: Scale notification
      condition: >-
        event.coreweave.event_reason in ["CWNodePoolScaledUp", "CWNodePoolScaledDown"]
      action:
        debug:
          msg: >-
            Node pool scaling event: {{ event.coreweave.event_message }}

    - name: GPU node assigned
      condition: >-
        event.coreweave.event_reason == "CWNodeAssigned"
      action:
        debug:
          msg: >-
            New node assigned: {{ event.coreweave.involved_object.name }}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `kubeconfig` | str | None | Path to kubeconfig file |
| `context` | str | None | Kubeconfig context name |
| `namespace` | str | `""` | Namespace to watch (empty = all) |
| `event_types` | list | `["ADDED", "MODIFIED"]` | K8s watch event types |
| `label_selector` | str | `""` | Label selector filter |
| `field_selector` | str | `""` | Field selector filter |

### CoreWeave-Specific Events

CKS emits custom events with reasons such as:

- `CWNodePoolScaledUp` / `CWNodePoolScaledDown`
- `CWNodeAssigned` / `CWNodeRegistered`
- `CWNodeCordoned` / `CWNodeUncordoned`
- `CWInsufficientCapacity`
- `CWOverQuota`
- `CWNodeConfigStaged`

See the [CoreWeave Node Pool documentation](https://docs.coreweave.com/docs/products/cks/reference/node-pool)
for the complete event list.
