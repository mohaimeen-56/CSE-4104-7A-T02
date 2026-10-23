# SalesIQ — Project Documentation Directory

Welcome to the **SalesIQ (AI Sales Analytics Dashboard)** documentation repository. All architectural diagrams, project reports, deployment manuals, and API specifications are neatly organized within this directory.

---

## 📁 Directory Structure

```text
docs/
├── diagrams/                          # Architectural & Design Diagrams (PDF)
│   ├── CSE4104-7A-T02_ArchitectureDiagram.pdf
│   ├── CSE4104-7A-T02_ERDiagram.pdf
│   └── CSE4104-7A-T02_UseCaseDiagram.pdf
├── reports/                           # Academic & Project Reports (PDF & DOCX)
│   ├── CSE4104-7A-T02_FinalReport.docx
│   ├── CSE4104-7A-T02_Proposal.pdf
│   ├── CSE4104-7A-T02_SRS.pdf
│   ├── CSE4104-7A-T02_TeamInfo.pdf
│   ├── CSE4104-7A-T02_TestCases.pdf
│   ├── CSE4104-7A-T02_TestingReport.pdf
│   └── CSE4104-7A-T02_BugReport.pdf
├── scripts/                            # Documentation generator scripts
│   └── generate_reports.py
├── assets/                            # Branding & Graphical Assets
│   └── myicon.ico
├── API.md                             # REST API Specification & Endpoints
├── ARCHITECTURE.md                    # System Architecture, Tech Stack & Design Principles
├── DEPLOYMENT.md                      # Production Deployment Guide (Supabase, Render, Vercel, Cloudflare)
├── SETUP.md                           # Local Environment Setup & Execution Guide
└── README.md                          # Documentation Index (this file)
```

---

## 📚 Document Index

### 1. Technical Guides
- **[API Specification](API.md)**: Detailed description of all backend REST endpoints, request/response models, and RBAC authentication.
- **[System Architecture](ARCHITECTURE.md)**: Architectural patterns, component relationships, data flow diagrams, and tech stack choices.
- **[Production Deployment Guide](DEPLOYMENT.md)**: Step-by-step instructions for deploying to Supabase (PostgreSQL), Render (FastAPI), Vercel (React Frontend), and Cloudflare.
- **[Local Setup Guide](SETUP.md)**: Step-by-step environment preparation, dependency installation, database migration, and test runner instructions.

### 2. Diagrams (`docs/diagrams/`)
- **[Architecture Diagram](diagrams/CSE4104-7A-T02_ArchitectureDiagram.pdf)**: Multi-tier architectural topology (Client, Reverse Proxy, Application Server, PostgreSQL, AI Provider Layer).
- **[Entity Relationship (ER) Diagram](diagrams/CSE4104-7A-T02_ERDiagram.pdf)**: Relational schema model and database table associations.
- **[Use Case Diagram](diagrams/CSE4104-7A-T02_UseCaseDiagram.pdf)**: User interactions, roles (Admin, Manager, Viewer), and functional boundaries.

### 3. Project Reports & Academic Submissions (`docs/reports/`)
- **[Final Report](reports/CSE4104-7A-T02_FinalReport.docx)**: Comprehensive project final report document (Word / DOCX format).
- **[Project Proposal](reports/CSE4104-7A-T02_Proposal.pdf)**: Initial scope, objectives, problem statement, and proposed deliverables.
- **[Software Requirements Specification (SRS)](reports/CSE4104-7A-T02_SRS.pdf)**: Formal functional and non-functional requirements.
- **[Team Information](reports/CSE4104-7A-T02_TeamInfo.pdf)**: Member roles, student IDs, and responsibilities.
- **[Test Cases](reports/CSE4104-7A-T02_TestCases.pdf)**: Test case specifications across authentication, CRUD, and AI features.
- **[Testing Report](reports/CSE4104-7A-T02_TestingReport.pdf)**: Comprehensive test execution results and coverage documentation.
- **[Bug Report](reports/CSE4104-7A-T02_BugReport.pdf)**: Documented issues, resolutions, and verification logs.
