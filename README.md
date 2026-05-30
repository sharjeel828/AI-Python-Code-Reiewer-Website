# 🛠️ AI-Powered Python Code Reviewer

An intelligent, full-stack Flask web application that performs automated multi-dimensional analysis on Python source code. It combines static style guides (PEP 8), AST-based structural complexity checks, algorithmic risk analysis, and LLM-driven auto-correction (via Groq and Llama 3) to deliver immediate, actionable feedback and side-by-side debugged code.

---

## 🌟 Key Features

- **🔐 User Session & History Management**: Secure user registration and login system backed by scrypt password hashing. Users can save, browse, and track all past submissions and reports in their personal dashboard.
- **🌳 Abstract Syntax Tree (AST) Deep Parser**: Custom AST parser that explores Python source code structures to compute essential software metrics:
  - *Cyclomatic Complexity* (estimate based on decision branch points)
  - *Maximum Nesting Depth* (identifies Arrow anti-patterns)
  - *Function & Loop Densities*
- **📏 PEP 8 Style Checker**: Seamless subprocess integration with **Flake8** to flag styling errors, syntax mistakes, formatting inconsistencies, and code smells on a line-by-line basis.
- **🤖 Predictive Risk Engine**: Calculates a composite **Vulnerability Risk Score** based on nested block depth and Flake8 issue count, and outputs architectural recommendations.
- **✨ LLM-Powered Auto-Correction**: Leverages **Groq's Llama 3** model API to reconstruct syntax-broken or style-deficient code into pure, running, fully corrected Python code. Features smart API rate-limit resilience, safe truncation, and error handling.
- **🎨 Glassmorphic Premium Interface**: Modern, responsive dark-mode dashboard styled with vanilla CSS, glassmorphism containers, hover state transitions, and a side-by-side comparative panel for original vs. corrected code.

---

## 🏗️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python / Flask | Core application server, session management, and routing. |
| **Database** | SQLAlchemy / SQLite | Relational ORM mapping user profiles, submissions, and detailed analysis reports. |
| **AST Engine** | Standard `ast` module | Custom visitor (`CodeMetricsVisitor`) extracting syntax graph properties. |
| **Static Linter** | Flake8 | Rule-based PEP 8 verification. |
| **AI LLM API** | Groq (`llama-3.1-8b-instant`) | Ultra-fast Llama-3 completion engine generating raw, clean code corrections. |
| **Frontend** | HTML5 / CSS3 / Vanilla JS | Sleek, glassmorphic layout, clean animations, and responsive layout. |

---

## 📂 Project Structure

```text
├── app.py              # Main Flask app, routes (Auth & Analysis), and configuration
├── analyzer.py         # AST parsing routines and Flake8 linter integration
├── ml_module.py        # ML vulnerability simulator & Groq LLM API client
├── models.py           # SQLAlchemy Database tables (User, Submission, Report, ModelVersion)
├── extensions.py       # Shared Flask-SQLAlchemy and Flask-Login instances
├── migrate_db.py       # Helper script to migrate database schemas
├── requirements.txt    # Direct & indirect Python dependencies
├── static/
│   ├── css/
│   │   └── style.css   # Modern, responsive dark-mode & glassmorphism theme
│   └── js/             # Client-side UI animations and helpers
└── templates/
    ├── base.html       # Shared site layout, navigation, and flashes
    ├── index.html      # Submission editor (supports text area & file uploads)
    ├── report.html     # Side-by-side report analysis, metrics, and fixes
    ├── history.html    # User submission audit log
    ├── login.html      # Clean, minimalist authentication forms
    └── register.html   # User sign-up forms
```

---

## 🚀 Getting Started

Follow these steps to set up the repository locally.

### 📋 Prerequisites

- **Python 3.8+** installed.
- A **Groq API Key** (Get one from the [Groq Console](https://console.groq.com/)).

### 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Environment Variables:**
   Create a `.env` file in the root directory and insert your Groq API Key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

5. **Run DB Migrations (if database is already created and needs update):**
   ```bash
   python migrate_db.py
   ```

6. **Start the Flask development server:**
   ```bash
   python app.py
   ```

7. Open your browser and navigate to `http://127.0.0.1:5000` to start reviewing your code!

---

## 🛠️ Verification & Testing

To test the parsing functionality and model prediction routines directly from the CLI, run the built-in testing script:
```bash
python test_ast.py
```

---

## 🤝 Contributing

Contributions are welcome! If you find any bugs or have feature suggestions, feel free to open an **issue** or submit a **pull request**.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
