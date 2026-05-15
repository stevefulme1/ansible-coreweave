# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this collection, please report it to:

**Email**: sfulmer@redhat.com

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge receipt of your report within 48 hours and will send a more detailed response within 7 days indicating the next steps in handling your report.

## Security Best Practices

When using this collection:

1. **Credentials Management**
   - Never commit kubeconfig files or API tokens to version control
   - Use Ansible Vault to encrypt sensitive variables
   - Rotate API tokens regularly
   - Use least-privilege service accounts

2. **Network Security**
   - Use TLS/SSL for all CoreWeave API connections
   - Verify SSL certificates (set `validate_certs: true`)
   - Use private networks (VPCs) when possible

3. **Resource Isolation**
   - Use Kubernetes namespaces to isolate workloads
   - Apply RBAC policies to limit permissions
   - Use network policies to control traffic

4. **Code Security**
   - Keep the collection and dependencies up to date
   - Review module parameters before execution
   - Use `no_log: true` for sensitive task outputs

## Known Security Considerations

- This collection requires kubernetes Python library, which must be kept up to date
- Kubeconfig files contain sensitive authentication data and must be protected
- API tokens grant access to CoreWeave resources and should be treated as secrets

## Security Updates

Security updates will be released as patch versions and announced via:
- GitHub Security Advisories
- GitHub Releases
- CHANGELOG.md

Subscribe to this repository's releases to receive notifications.
