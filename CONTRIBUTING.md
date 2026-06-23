# Contributing to Enterprise AI Gateway

Thank you for your interest in contributing to the Enterprise AI Gateway! We welcome contributions from the community to make this project more robust and feature-rich.

## 🛠️ Development Setup

### 1. Local Environment
*   Ensure you have **Python 3.11+** and **Node.js 18+** installed.
*   Install Docker and Docker Compose.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Running Infrastructure
The easiest way to develop is to run the database and Redis via Docker while running the app locally:
```bash
docker-compose up db redis -d
```

## 📜 Coding Standards

### Backend (Python)
*   Use `async/await` for all I/O operations.
*   Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.
*   Use type hints for all function signatures.
*   All new API endpoints should be added under `app/api/v1`.

### Frontend (TypeScript/React)
*   Use Functional Components and Hooks.
*   Tailwind CSS is preferred for styling.
*   Ensure all components are typed with TypeScript.

## 🚀 Pull Request Process
1.  Fork the repository and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  Ensure the test suite passes.
4.  Update the documentation if you've changed or added features.
5.  Submit a Pull Request with a clear description of the changes.

## 🛡️ Security
If you discover a security vulnerability, please do NOT open an issue. Instead, email us at [security@example.com] (placeholder).

## 💬 Community
Join our Discord/Slack (placeholder) to discuss features and get help.
