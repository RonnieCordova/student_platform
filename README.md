# 🎓 Cloud-Native Tutoring Platform API

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-green.svg)
![Docker](https://img.shields.io/badge/Container-Hardened-orange.svg)
![AWS](https://img.shields.io/badge/AWS-Cloud%20Native-232F3E.svg)
![Security](https://img.shields.io/badge/Security-OAuth2%20%7C%20RBAC-red.svg)

> **A scalable, secure-by-design peer-to-peer tutoring backend architecture.**
>
> *Built as part of my journey towards the AWS Solutions Architect Associate (SAA-C03) & Cloud Security Architect certification.*

---

## 📖 Project Overview

This project is not just a tutoring application; it is a **Cloud Security & Architecture Reference Implementation**.

The goal is to connect university students with peer tutors through a secure RESTful API. However, the *primary engineering focus* is demonstrating **production-grade cloud practices**: containerization security, infrastructure scalability on AWS (ECS Fargate), and strict adherence to the **AWS Shared Responsibility Model**.

### 🏗️ Architecture Design
*(See `/docs/architecture-diagram.png` for the full AWS topology)*

* **Compute:** AWS ECS (Fargate) for serverless container orchestration.
* **Database:** Amazon RDS (PostgreSQL) inside private subnets.
* **Registry:** Amazon ECR with **Image Scanning** enabled for vulnerability detection.
* **Security:**
    * **Least Privilege:** Containers run as `non-root` users (UID 1000).
    * **Authentication:** OAuth2 with Password Flow + JWT (JSON Web Tokens).
    * **Secrets Management:** (Planned) AWS Systems Manager Parameter Store.

---

## 🛡️ Security Posture (DevSecOps)

As an aspiring **Cloud Security Architect**, I have implemented specific controls to mitigate common OWASP Top 10 vulnerabilities:

| Security Control | Implementation Detail |
| :--- | :--- |
| **Container Hardening** | Custom `Dockerfile` using `slim` base, stripping unneeded packages, and enforcing a **non-root user** execution context to prevent container breakout. |
| **Identity Management** | Stateless authentication using JWTs. Passwords hashed using `bcrypt` (salt + pepper). |
| **Network Isolation** | (In Deployment) Database resides in a **Private Subnet**; only the API (in Public Subnet/ALB) can communicate with it via Security Group allow-listing. |
| **Input Validation** | Strict Pydantic schemas prevent Mass Assignment and Injection attacks. |

---

## 🛠️ Tech Stack

* **Language:** Python 3.9
* **Framework:** FastAPI (Asynchronous, Type-safe)
* **ORM:** SQLAlchemy (with PostgreSQL adapter `psycopg2`)
* **Containerization:** Docker (Multi-stage builds optimized for security)
* **CI/CD:** GitHub Actions (Planned)

---

## ⚡ Key Features

* **User Management:** Role-Based Access Control (RBAC) for `Student` vs `Tutor`.
* **Marketplace Logic:** Tutors can set specific subjects and hourly rates.
* **Search Engine:** Public endpoint to filter tutors by subject.
* **Booking System:** Complete lifecycle (Request -> Pending -> Confirm/Reject).
* **Reputation System:** 5-star review system with text feedback.

---

## 🚀 Getting Started (Local Development)

### Prerequisites
* Docker & Docker Compose
* Python 3.9+

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/backend-tutorias.git](https://github.com/YOUR_USERNAME/backend-tutorias.git)
cd backend-tutorias
