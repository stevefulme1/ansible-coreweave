# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type


"""Kubernetes helper utilities for CoreWeave CRD modules.

Wraps the kubernetes Python client to provide CRUD operations on
Kubernetes custom resources (VirtualServer, InferenceService, PVC).
"""


try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    from kubernetes.dynamic import DynamicClient

    HAS_K8S = True
except ImportError:
    HAS_K8S = False


def get_api_client(module):
    """Build a Kubernetes API client from module params.

    Args:
        module: AnsibleModule instance with kubeconfig/context params.

    Returns:
        kubernetes.client.ApiClient instance.

    Raises:
        module.fail_json on configuration errors.
    """
    if not HAS_K8S:
        module.fail_json(
            msg="This module requires the kubernetes Python library. Install it with: pip install kubernetes>=28.1.0")

    kubeconfig = module.params.get("kubeconfig")
    context = module.params.get("context")

    try:
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig, context=context)
        else:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config(context=context)
    except Exception as e:
        module.fail_json(msg=f"Failed to load Kubernetes configuration: {str(e)}")

    return client.ApiClient()


def get_dynamic_client(module):
    """Build a Kubernetes DynamicClient from module params.

    Args:
        module: AnsibleModule instance.

    Returns:
        kubernetes.dynamic.DynamicClient instance.
    """
    api_client = get_api_client(module)
    return DynamicClient(api_client)


def get_resource(module, api_version, kind):
    """Get a dynamic resource handle for a given apiVersion and kind.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.

    Returns:
        Resource object from the dynamic client.
    """
    dyn_client = get_dynamic_client(module)
    try:
        return dyn_client.resources.get(api_version=api_version, kind=kind)
    except Exception as e:
        module.fail_json(msg=f"Failed to find resource {api_version}/{kind}: {str(e)}")


def get_existing_resource(module, api_version, kind, name, namespace):
    """Fetch an existing resource by name and namespace.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.
        name: Resource name.
        namespace: Kubernetes namespace.

    Returns:
        Resource dict if found, None otherwise.
    """
    resource = get_resource(module, api_version, kind)
    try:
        existing = resource.get(name=name, namespace=namespace)
        return existing.to_dict()
    except ApiException as e:
        if e.status == 404:
            return None
        module.fail_json(msg=f"Failed to get {kind} '{name}': {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Failed to get {kind} '{name}': {str(e)}")


def create_resource(module, api_version, kind, manifest, namespace):
    """Create a Kubernetes resource from a manifest.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.
        manifest: Full resource manifest dict.
        namespace: Kubernetes namespace.

    Returns:
        Created resource dict.
    """
    resource = get_resource(module, api_version, kind)
    try:
        result = resource.create(body=manifest, namespace=namespace)
        return result.to_dict()
    except ApiException as e:
        module.fail_json(msg=f"Failed to create {kind}: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Failed to create {kind}: {str(e)}")


def update_resource(module, api_version, kind, manifest, namespace):
    """Update (patch) a Kubernetes resource.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.
        manifest: Full resource manifest dict.
        namespace: Kubernetes namespace.

    Returns:
        Updated resource dict.
    """
    resource = get_resource(module, api_version, kind)
    name = manifest["metadata"]["name"]
    try:
        result = resource.patch(body=manifest, name=name, namespace=namespace,
                                content_type="application/merge-patch+json")
        return result.to_dict()
    except ApiException as e:
        module.fail_json(msg=f"Failed to update {kind} '{name}': {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Failed to update {kind} '{name}': {str(e)}")


def delete_resource(module, api_version, kind, name, namespace):
    """Delete a Kubernetes resource.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.
        name: Resource name.
        namespace: Kubernetes namespace.

    Returns:
        Deletion result dict.
    """
    resource = get_resource(module, api_version, kind)
    try:
        result = resource.delete(name=name, namespace=namespace)
        return result.to_dict() if hasattr(result, "to_dict") else {"status": "deleted"}
    except ApiException as e:
        if e.status == 404:
            return None
        module.fail_json(msg=f"Failed to delete {kind} '{name}': {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Failed to delete {kind} '{name}': {str(e)}")


def list_resources(module, api_version, kind, namespace, label_selector=None, field_selector=None):
    """List Kubernetes resources in a namespace.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.
        namespace: Kubernetes namespace.
        label_selector: Optional label selector string.
        field_selector: Optional field selector string.

    Returns:
        List of resource dicts.
    """
    resource = get_resource(module, api_version, kind)
    kwargs = {"namespace": namespace}
    if label_selector:
        kwargs["label_selector"] = label_selector
    if field_selector:
        kwargs["field_selector"] = field_selector
    try:
        result = resource.get(**kwargs)
        items = result.to_dict().get("items", [])
        return items
    except ApiException as e:
        module.fail_json(msg=f"Failed to list {kind}: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Failed to list {kind}: {str(e)}")


def apply_resource(module, api_version, kind, manifest, namespace, state="present"):
    """Apply a Kubernetes resource (create, update, or delete).

    Provides idempotent create-or-update semantics with check mode support.

    Args:
        module: AnsibleModule instance.
        api_version: Kubernetes API version string.
        kind: Kubernetes resource kind string.
        manifest: Full resource manifest dict.
        namespace: Kubernetes namespace.
        state: Desired state - 'present' or 'absent'.

    Returns:
        dict with 'changed', 'result', and optionally 'diff' keys.
    """
    name = manifest["metadata"]["name"]
    existing = get_existing_resource(module, api_version, kind, name, namespace)

    if state == "absent":
        if existing is None:
            return {"changed": False, "result": {}}
        if module.check_mode:
            return {"changed": True, "result": {}}
        delete_resource(module, api_version, kind, name, namespace)
        return {"changed": True, "result": {}}

    # state == 'present'
    if existing is None:
        if module.check_mode:
            return {"changed": True, "result": manifest}
        result = create_resource(module, api_version, kind, manifest, namespace)
        return {"changed": True, "result": result}

    # Compare specs to determine if update is needed
    existing_spec = existing.get("spec", {})
    desired_spec = manifest.get("spec", {})
    if _specs_match(existing_spec, desired_spec):
        return {"changed": False, "result": existing}

    if module.check_mode:
        return {"changed": True, "result": manifest}
    result = update_resource(module, api_version, kind, manifest, namespace)
    return {"changed": True, "result": result}


def _specs_match(existing, desired):
    """Compare existing and desired specs recursively.

    Only checks keys present in the desired spec (server-added fields
    are ignored).

    Args:
        existing: Existing resource spec dict.
        desired: Desired resource spec dict.

    Returns:
        True if all desired keys match existing values.
    """
    if isinstance(desired, dict):
        if not isinstance(existing, dict):
            return False
        for key, value in desired.items():
            if key not in existing:
                return False
            if not _specs_match(existing[key], value):
                return False
        return True
    if isinstance(desired, list):
        if not isinstance(existing, list):
            return False
        if len(desired) != len(existing):
            return False
        return all(_specs_match(e, d) for e, d in zip(existing, desired))
    return existing == desired
