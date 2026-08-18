# PO Desk

PO Desk is an internal request-management system where employees can submit requests, receive clarification when required, and track their requests. Approvers can review requests, approve/reject them, and send a response to the requestor.

## Prerequisites

Make sure you have the following installed:

* **Python 3.10+**
* **Node.js 18+**
* **npm**
* **Git**

## 1. Clone the Repository

```bash
git clone https://github.com/sunny6289/po-desk
cd po-desk
```

---

# 2. Setup the Backend

Open a terminal in the project root and navigate to the backend:

```bash
cd backend
```

### Create a Python virtual environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create `.env`

Create a file named `.env` inside the `backend` folder:

```env
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=onboarding@resend.dev
```

> Do **not** commit the `.env` file. It is already included in the backend `.gitignore`.

### Start the backend

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The FastAPI backend will run at:

```text
http://localhost:8000
```

API documentation is available at:

```text
http://localhost:8000/docs
```

The SQLite database will be created locally by the backend.

---

# 3. Setup the Requestor Frontend

Open a **new terminal** and navigate to the requestor frontend:

```bash
cd po-desk/frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The requestor portal will be available at:

```text
http://localhost:5173
```

This frontend is used by employees to:

* Submit requests
* Answer clarification questions
* Track previously submitted requests
* View request status and details

---

# 4. Setup the Approval Frontend

Open another **new terminal** and navigate to the approval frontend:

```bash
cd po-desk/approval-frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The approval portal will be available at:

```text
http://localhost:5174
```

This frontend is used by approvers to:

* Select a department
* View requests assigned to the department
* Filter requests by status
* View complete request details
* Approve or reject requests
* Provide an approval/rejection reason

---

# 5. Run the Complete Application

You should have **three terminals** running:

### Terminal 1 — Backend

```powershell
cd po-desk/backend
.\venv\Scripts\activate
uvicorn main:app --reload
```

Runs on:

```text
http://localhost:8000
```

### Terminal 2 — Requestor Frontend

```powershell
cd po-desk/frontend
npm run dev
```

Runs on:

```text
http://localhost:5173
```

### Terminal 3 — Approval Frontend

```powershell
cd po-desk/approval-frontend
npm run dev
```

Runs on:

```text
http://localhost:5174
```

---

## Project Structure

```text
po-desk/
│
├── backend/
│   ├── agents/
│   ├── constants/
│   ├── database/
│   ├── models/
│   ├── utility/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env                  # Not committed
│   └── .gitignore
│
├── frontend/                  # Requestor portal
│   ├── src/
│   ├── package.json
│   └── ...
│
├── approval-frontend/         # Approver portal
│   ├── src/
│   ├── package.json
│   └── ...
│
└── README.md
```

## Environment Variables

The backend requires:

| Variable            | Purpose                           |
| ------------------- | --------------------------------- |
| `GEMINI_API_KEY`    | Used by the AI agents             |
| `RESEND_API_KEY`    | Used for sending emails           |
| `RESEND_FROM_EMAIL` | Email address used to send emails |

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=onboarding@resend.dev
```

**Never commit your API keys or `.env` file to GitHub.**
