# Getting Started with stevefulme1.coreweave

Ansible collection for managing CoreWeave cloud infrastructure

## Installation

```bash
ansible-galaxy collection install stevefulme1.coreweave
```

## Requirements

- Ansible >= 2.16
- Python >= 3.12

## Authentication

Most modules require authentication credentials. Set these as variables
in your playbook, inventory, or Ansible Vault:

```yaml
vars:
  api_url: "https://your-service.example.com"
  api_token: "{{ vault_api_token }}"
  validate_certs: true
```

Store sensitive credentials in Ansible Vault:

```bash
ansible-vault encrypt_string 'your-token-here' --name 'vault_api_token'
```

## Quick Example

```yaml
---
- name: Example playbook
  hosts: localhost
  connection: local
  gather_facts: false
  collections:
    - stevefulme1.coreweave
  tasks:
    - name: Get info
      stevefulme1.coreweave.coreweave_configmap_info:
        api_url: "{{ api_url }}"
        api_token: "{{ api_token }}"
      register: result

    - name: Show result
      ansible.builtin.debug:
        var: result
```

## Collection Contents

- **Modules**: 56
- **Roles**: 13
- **EDA plugins**: 2

## Next Steps

- Browse the module documentation: `ansible-doc stevefulme1.coreweave.<module_name>`
- Check the [README](../README.md) for the full module and role list
- Review [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
