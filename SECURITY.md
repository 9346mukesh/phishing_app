# Security Policy

## Reporting Security Issues

**Do not** open a public GitHub issue for security vulnerabilities. Instead, please email security concerns to the project maintainers directly or use GitHub's private vulnerability reporting feature if available.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and work on a fix promptly.

## Current Security Practices

### Model Artifacts

- Model files (`.pkl`) are **not** included in the repository by default.
- Models should be stored in a secure artifact registry (e.g., S3, artifact storage).
- Always validate model integrity using checksums or signatures before loading.
- Never unpickle untrusted files; use `joblib.load()` only on trusted sources or consider safer serialization (ONNX, SafePickle).

### Input Validation

- All user inputs are validated using `pydantic` models.
- URLs are strictly validated before processing.
- Network operations include timeouts to prevent DoS.

### Dependencies

- Dependencies are pinned in `requirements.txt`.
- Automated dependency updates are enabled via Dependabot.
- Security advisories are reviewed regularly.

### Secrets Management

- Never commit API keys, credentials, or secrets.
- Use environment variables or secret management services (GitHub Secrets, HashiCorp Vault).

### Containerization

- Docker images use minimal base images (`python:3.11-slim`).
- Containers run as non-root users.
- Build artifacts are scanned for vulnerabilities.

## Known Limitations

- This project is primarily educational; use with caution in production.
- Phishing detection is not 100% accurate; always combine with other security tools.
- The model may have biases based on training data.

## Future Improvements

- [ ] Migrate to safer model serialization (ONNX).
- [ ] Add rate limiting and request throttling.
- [ ] Implement authentication and authorization.
- [ ] Add Web Application Firewall (WAF) rules.
- [ ] Set up continuous security scanning (SAST, DAST).

## Attribution

Thank you to all security researchers who responsibly report issues.
