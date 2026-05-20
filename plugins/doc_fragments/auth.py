# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    """Documentation fragment for CoreWeave Kubernetes authentication."""

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
  - python >= 3.11
notes:
  - This module requires a valid Kubernetes configuration for a CoreWeave cluster.
  - Authentication is handled through standard kubeconfig mechanisms.
  - Requires the C(kubernetes.core) Ansible collection to be installed.
"""
