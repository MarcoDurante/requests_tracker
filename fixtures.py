import json
import warnings
from datetime import datetime
from db import get_connection, init_db
from tag_extractor import extract_tags


warnings.filterwarnings("ignore", category=DeprecationWarning)


examples = [
  {
    "title": "Checkout non funzionante",
    "description": "Errore 500 durante pagamento con carta Visa",
    "status": "nuova",
    "priority": "alta",
    "assignee": "Carlo",
    "created_at": "2025-12-01",
    "updated_at": "2025-12-01",
    "tags": ""
  },
  {
    "title": "Magazzino non sincronizzato",
    "description": "Quantità errate prodotto X in magazzino",
    "status": "in_lavorazione",
    "priority": "bassa",
    "assignee": "Lucia",
    "created_at": "2025-11-28",
    "updated_at": "2025-12-01",
    "tags": ""
  },
  {
    "title": "Aggiornare grafica homepage",
    "description": "Nuovo banner promozionale per la campagna",
    "status": "chiusa",
    "priority": "media",
    "assignee": "Pippo",
    "created_at": "2025-11-20",
    "updated_at": "2025-11-30",
    "tags": "grafica,web"
  }
]

init_db()


conn = get_connection()
cur = conn.cursor()
for r in examples:
	tags = r.get("tags") or ""
	if not tags:
		tags_list = extract_tags(r.get("description",""))
		tags = ",".join(tags_list) if tags_list else ""
	cur.execute("""
		INSERT INTO service_requests (title, description, status, created_at, updated_at, priority, assignee, tags)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	""", (r.get("title"), r.get("description"), r.get("status"), r.get("created_at"), r.get("updated_at"), r.get("priority"), r.get("assignee"), tags))
conn.commit()
conn.close()
print("Fixtures caricate.")
    
