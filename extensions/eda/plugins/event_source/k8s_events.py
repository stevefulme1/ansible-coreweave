# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""CoreWeave Kubernetes events watcher for ansible-rulebook.

Watches Kubernetes events on a CKS cluster and emits them to the
rulebook engine. Useful for reacting to node scaling, pod failures,
node pool changes, and other cluster events.

Usage in a rulebook:
  sources:
    - stevefulme1.coreweave.k8s_events:
        kubeconfig: "~/.kube/config"
        namespace: ""
        event_types:
          - ADDED
          - MODIFIED
        label_selector: "topology.coreweave.cloud/node-pool=a100-pool"
"""

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from kubernetes import client, config, watch
    HAS_K8S = True
except ImportError:
    HAS_K8S = False


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Entry point for the EDA event source plugin.

    Args:
        queue: asyncio.Queue to put events onto for the rulebook engine.
        args: Configuration dict from the rulebook source definition.
    """
    if not HAS_K8S:
        logger.error("kubernetes Python library required. Install with: pip install kubernetes>=28.1.0")
        return

    kubeconfig = args.get("kubeconfig")
    context = args.get("context")
    namespace = args.get("namespace", "")
    event_types = args.get("event_types", ["ADDED", "MODIFIED"])
    label_selector = args.get("label_selector", "")
    field_selector = args.get("field_selector", "")
    resource_type = args.get("resource_type", "events")

    try:
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig, context=context)
        else:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config(context=context)
    except Exception as e:
        logger.error("Failed to load kubeconfig: %s", e)
        return

    v1 = client.CoreV1Api()
    w = watch.Watch()

    logger.info(
        "Watching K8s %s in namespace=%r label_selector=%r",
        resource_type, namespace or "(all)", label_selector or "(none)",
    )

    watch_kwargs: dict[str, Any] = {"timeout_seconds": 0}
    if label_selector:
        watch_kwargs["label_selector"] = label_selector
    if field_selector:
        watch_kwargs["field_selector"] = field_selector

    try:
        while True:
            try:
                if namespace:
                    stream = w.stream(v1.list_namespaced_event, namespace, **watch_kwargs)
                else:
                    stream = w.stream(v1.list_event_for_all_namespaces, **watch_kwargs)

                for k8s_event in stream:
                    if k8s_event["type"] not in event_types:
                        continue

                    obj = k8s_event["object"]
                    event = {
                        "coreweave": {
                            "type": k8s_event["type"],
                            "event_reason": getattr(obj, "reason", None),
                            "event_message": getattr(obj, "message", None),
                            "event_type": getattr(obj, "type", None),
                            "involved_object": {
                                "kind": getattr(obj.involved_object, "kind", None) if obj.involved_object else None,
                                "name": getattr(obj.involved_object, "name", None) if obj.involved_object else None,
                                "namespace": getattr(obj.involved_object, "namespace", None) if obj.involved_object else None,
                            } if hasattr(obj, "involved_object") else {},
                            "source_component": getattr(obj.source, "component", None) if hasattr(obj, "source") and obj.source else None,
                            "first_timestamp": str(obj.first_timestamp) if hasattr(obj, "first_timestamp") else None,
                            "last_timestamp": str(obj.last_timestamp) if hasattr(obj, "last_timestamp") else None,
                            "count": getattr(obj, "count", None),
                        }
                    }
                    await queue.put(event)

            except Exception as e:
                logger.warning("Watch stream interrupted: %s. Reconnecting in 5s...", e)
                await asyncio.sleep(5)

    except asyncio.CancelledError:
        logger.info("K8s event watcher shutting down")
        w.stop()
