import csv
import json
import warnings
from io import StringIO
from datetime import datetime
from db import get_connection
from flask import make_response
from tag_extractor import extract_tags
from flask import Flask, render_template, request, jsonify






warnings.filterwarnings("ignore", category=DeprecationWarning)



app = Flask(__name__)
app.secret_key = "chiave"



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/v1/delete/<int:req_id>", methods=["GET"])
def delete(req_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM service_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})
    
    
@app.route("/api/v1/requests")
def list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM service_requests ORDER BY updated_at DESC")
    rows = cur.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "status": r["status"],
            "priority": r["priority"],
            "assignee": r["assignee"],
            "tags": r["tags"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })
    return jsonify(data)


@app.route("/api/v1/request/<int:req_id>", methods=["GET"])
def details(req_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM service_requests WHERE id = ?", (req_id,))
    r = cur.fetchone()
    conn.close()

    if not r:
        return jsonify({"error": "not found"}), 404

    data = {
        "id": r["id"],
        "title": r["title"],
        "description": r["description"],
        "status": r["status"],
        "priority": r["priority"],
        "assignee": r["assignee"],
        "tags": r["tags"],
        "created_at": r["created_at"][:10],
        "updated_at": r["updated_at"][:10]
    }
    return jsonify(data)
    
    
@app.route("/api/v1/requests/<int:req_id>", methods=["POST"])
def update(req_id):
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    payload = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM service_requests WHERE id = ?", (req_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "not found"}), 404

    title = payload.get("title", row["title"])
    description = payload.get("description", row["description"])
    status = payload.get("status", row["status"])
    priority = payload.get("priority", row["priority"])
    assignee = payload.get("assignee", row["assignee"])
    tags = payload.get("tags", row["tags"])

    cur.execute("""
        UPDATE service_requests
        SET title=?, description=?, status=?, priority=?, assignee=?, tags=?, updated_at=?
        WHERE id=?
    """, (title, description, status, priority, assignee, tags, datetime.utcnow().isoformat(), req_id))

    conn.commit()
    conn.close()
    return jsonify({"success": True})
    
    
@app.route("/api/v1/request", methods=["POST"])
def create():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    payload = request.get_json()

    required = ["title", "description"]
    for field in required:
        if field not in payload or payload[field] is None or payload[field] == "":
            return jsonify({"error": f"Missing field: {field}"}), 400

    title = payload["title"]
    description = payload["description"]

    status = payload.get("status", "nuova")
    priority = payload.get("priority", "")
    assignee = payload.get("assignee", "")
    tags = payload.get("tags", "")
    if not tags:
        tags_list = extract_tags(description)
        tags = ",".join(tags_list) if tags_list else ""

    created = datetime.utcnow().isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO service_requests (title, description, status, priority, assignee, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, description, status, priority, assignee, tags, created, created))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/api/export_csv", methods=["POST"])
def export_csv():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    requests_data = request.get_json()

    output = StringIO()
    writer = csv.writer(output)

    # intestazioni
    writer.writerow([
        "ID", "Title", "Description", "Status", "Priority", "Assignee",
        "Tags", "Created At", "Updated At"
    ])

    # righe
    for r in requests_data:
        writer.writerow([
            r.get("id", ""),
            r.get("title", ""),
            r.get("description", ""),
            r.get("status", ""),
            r.get("priority", ""),
            r.get("assignee", ""),
            r.get("tags", ""),
            r.get("created_at", ""),
            r.get("updated_at", "")
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=requests_report.csv"
    response.headers["Content-Type"] = "text/csv"

    return response

    
    

if __name__ == "__main__":
    app.run(debug=True)