# MudraMitra 

# About
MudraMitra is a simple Python project that I am developing to manage financial records. The main aim is to make it easier to add, view, and manage basic money-related information.

# What it does
- Helps manage financial records.
- Provides a simple menu to interact with the program.
- Stores records using JSON.
- Uses basic Python concepts like functions, loops, and conditions.

## How to run

1. Create and activate a virtual environment (first time only):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Start the API from the project root:
   ```powershell
   uvicorn app.main:app --reload
   ```
4. Open http://127.0.0.1:8000/docs to try the endpoints.

## Endpoints
| Method | Path | What it does |
| GET | `/health` | Health check |
| GET | `/records?limit=5` | List records (optional limit) |
| GET | `/records/{id}` | One record, 404 if missing |
| GET | `/search?q=rent` | Top 3 records ranked by TF-IDF + cosine similarity |
| POST | `/questions` | Save a user question to `data/questions.json` |

## Other scripts
python analysis/explore.py     # 3 facts about the data (pandas)
python -m app.smart_search     # try the ranking in the terminal
python -m app.cli              # Day 2 menu
```

