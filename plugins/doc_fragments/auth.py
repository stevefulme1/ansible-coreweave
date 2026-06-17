# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

__metaclass__ = type


class ModuleDocFragment:
    """Documentation fragments for CoreWeave authentication."""

    # Kubernetes CRD-based modules (VirtualServer, InferenceService, PVC)
    DOCUMENTATION = r"""
options:
  kubeconfig:
    description:
      - Path to an existing Kubernetes config file.
      - If not provided, the default location C(~/.kube/config) is used.
    type: path
    aliases:
      - kubeconfig_path
  context:
    description:
      - The name of a context found in the Kubernetes config file.
    type: str
  namespace:
    description:
      - The Kubernetes namespace to operate in.
      - Defaults to C(default) if not specified.
    type: str
    default: default
requirements:
  - kubernetes >= 28.1.0
  - python >= 3.12
notes:
  - This module requires a valid Kubernetes configuration for a CoreWeave cluster.
  - Authentication is handled through standard kubeconfig mechanisms.
  - Requires the C(kubernetes.core) Ansible collection to be installed.
"""

    # REST API modules (CKS clusters, VPCs, Object Storage)
    REST = r"""
options:
  api_token:
    description:
      - CoreWeave API access token for authentication.
      - Tokens can be generated in the CoreWeave Cloud dashboard.
      - Can also be set via the E(COREWEAVE_API_TOKEN) environment variable.
    type: str
    required: true
  api_url:
    description:
      - CoreWeave API base URL.
      - Override only for non-standard environments.
    type: str
    default: https://api.coreweave.com
  validate_certs:
    description:
      - Whether to validate SSL certificates.
    type: bool
    default: true
  timeout:
    description:
      - API request timeout in seconds.
    type: int
    default: 60
requirements:
  - python >= 3.12
notes:
  - This module communicates with the CoreWeave REST API at C(api.coreweave.com).
  - Authentication uses Bearer token authorization.
  - The C(api_token) can be set via the E(COREWEAVE_API_TOKEN) environment variable
    to avoid passing it in playbooks.
"""
