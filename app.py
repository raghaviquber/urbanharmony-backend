from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# -----------------------------
# DATABASE CONFIG (FINAL FIX ✅)
# -----------------------------
database_url = os.environ.get("DATABASE_URL")

print("DATABASE_URL =", database_url)  # Debug

if database_url:
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔥 IMPORTANT: SSL FIX FOR RENDER
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "sslmode": "require"
    }
}

db = SQLAlchemy(app)

# -----------------------------
# MODEL
# -----------------------------
class Issue(db.Model):
    __tablename__ = "issues"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    category = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Pending")
    upvotes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# CREATE TABLES
# -----------------------------
with app.app_context():
    try:
        db.create_all()
        print("✅ Tables created / verified")
    except Exception as e:
        print("❌ DB ERROR:", str(e))

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/")
def home():
    return "UrbanHarmony Backend Running 🚀"

# -----------------------------
# GET ALL ISSUES
# -----------------------------
@app.route("/issues", methods=["GET"])
def get_issues():
    try:
        issues = Issue.query.order_by(Issue.created_at.desc()).all()

        result = []
        for i in issues:
            result.append({
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "location": i.location,
                "category": i.category,
                "status": i.status,
                "upvotes": i.upvotes,
                "user_id": i.user_id,
                "created_at": i.created_at.isoformat()
            })

        return jsonify(result)

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# -----------------------------
# GET USER ISSUES
# -----------------------------
@app.route("/my-issues/<user_id>", methods=["GET"])
def get_user_issues(user_id):
    try:
        issues = Issue.query.filter_by(user_id=user_id).order_by(Issue.created_at.desc()).all()

        result = []
        for i in issues:
            result.append({
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "location": i.location,
                "category": i.category,
                "status": i.status,
                "upvotes": i.upvotes,
                "user_id": i.user_id,
                "created_at": i.created_at.isoformat()
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# CREATE ISSUE
# -----------------------------
@app.route("/create-issue", methods=["POST"])
def create_issue():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        title = data.get("title")
        description = data.get("description")

        if not title or not description:
            return jsonify({"error": "Missing required fields"}), 400

        new_issue = Issue(
            title=title,
            description=description,
            location=data.get("location"),
            category=data.get("category"),
            user_id=data.get("user_id"),
            status="Pending",
            upvotes=0
        )

        db.session.add(new_issue)
        db.session.commit()

        return jsonify({"message": "Issue created successfully"}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# -----------------------------
# UPVOTE ISSUE
# -----------------------------
@app.route("/upvote", methods=["POST"])
def upvote():
    try:
        data = request.get_json()
        issue = Issue.query.get(data.get("issue_id"))

        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        issue.upvotes += 1
        db.session.commit()

        return jsonify({"message": "Upvoted successfully"}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# -----------------------------
# UPDATE STATUS
# -----------------------------
@app.route("/update-status", methods=["POST"])
def update_status():
    try:
        data = request.get_json()
        issue = Issue.query.get(data.get("issue_id"))

        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        issue.status = data.get("status")
        db.session.commit()

        return jsonify({"message": "Status updated"}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# -----------------------------
# DELETE ISSUE
# -----------------------------
@app.route("/delete-issue", methods=["POST"])
def delete_issue():
    try:
        data = request.get_json()
        issue = Issue.query.get(data.get("issue_id"))

        if not issue:
            return jsonify({"error": "Issue not found"}), 404

        db.session.delete(issue)
        db.session.commit()

        return jsonify({"message": "Issue deleted"}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
