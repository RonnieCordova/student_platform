# Security Policy

## Supported Versions
Solo la versión `main` recibe actualizaciones de seguridad.

## Security Controls Implemented
* **Container Security:** Imagen base `python:3.9-slim`, ejecución con usuario no-root, escaneo de vulnerabilidades en AWS ECR (Scan on Push).
* **Network Security:** (Próximamente) Microsegmentación con AWS Security Groups.
* **Data Security:** (Próximamente) Cifrado en reposo con AWS KMS en RDS PostgreSQL.

## Reporting a Vulnerability
Por favor, no abras un issue público. Contacta al administrador directamente a través de [Tu Correo/LinkedIn].