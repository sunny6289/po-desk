# PO Desk - Setup & Local Development Guide

This guide will help you run the **PO Desk** project on your local machine after cloning it from GitHub.

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed on your computer:

* **Node.js** (v18.0 or higher) & **npm** — [Download Node.js](https://nodejs.org/)
* **Python** (v3.10 or higher) & **pip** — [Download Python](https://www.python.org/)
* **Git** — [Download Git](https://git-scm.com/)

---

## 🚀 Step-by-Step Setup Instructions

### 1. Clone the Repository

Open your terminal or command prompt and clone the project:

```bash
git clone https://github.com/your-username/po-desk.git
cd po-desk
```

---

### 2. Set Up and Run the Backend (FastAPI)

1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create a Python Virtual Environment:
   * **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment variables (`.env`):
   Create a `.env` file inside the `backend/` directory and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

The backend server will run at: **`http://localhost:8000`**  
*(API documentation available at `http://localhost:8000/docs`)*

---

### 3. Set Up and Run the Frontend (React)

Open a **new terminal tab or window** (keep the backend running in the first terminal).

1. Navigate to the `frontend` folder from the root directory:
   ```bash
   cd po-desk/frontend
   ```

2. Install JavaScript dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   # Or if using Vite:
   # npm run dev
   ```

The frontend application will open automatically in your web browser at: **`http://localhost:3000`** (or `http://localhost:5173` if using Vite).

---

## 📁 Project Structure

```text
po-desk/
│
├── backend/                # FastAPI application
│   ├── main.py             # Server routes and entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Backend environment variables (Not committed)
│
├── frontend/               # ReactJS application
│   ├── src/                # UI source code
│   └── package.json        # Frontend dependencies & scripts
│
└── README.md               # Setup documentation
```
