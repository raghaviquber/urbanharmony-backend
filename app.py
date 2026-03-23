from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ✅ CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Database (Render safe)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///urbanharmony.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# ENSURE TABLES ALWAYS EXIST
# -----------------------------
@app.before_request
def create_tables():
    db.create_all()

# -----------------------------
# MODELS
# -----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))
    civic_score = db.Column(db.Integer, default=0)


class Authority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    email = db.Column(db.String(100))


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    assigned_authority_id = db.Column(db.Integer)


class Upvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    issue_id = db.Column(db.Integer)

# -----------------------------
# HELPER FUNCTION
# -----------------------------

def suggest_category(description):
    text = description.lower()

    if "garbage" in text or "trash" in text:
        return "Waste Management"
    elif "pothole" in text or "road" in text:
        return "Road Issue"
    elif "water" in text or "leak" in text:
        return "Water Issue"
    elif "light" in text:
        return "Electricity"
    else:
        return "General"

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/", methods=["GET"])
def home():
    return "UrbanHarmony Backend Running 🚀"


@app.route("/create-issue", methods=["POST"])
def create_issue():
    data = request.json

    category = suggest_category(data["description"])

    issue = Issue(
        title=data["title"],
        description=data["description"],
        category=category,
        location=data["location"],
        created_by=data.get("user_id", 1)
    )

    db.session.add(issue)
    db.session.commit()

    return jsonify({
        "message": "Issue created",
        "category": category
    })


@app.route("/issues", methods=["GET"])
def get_issues():
    try:
        issues = Issue.query.all()
        result = []

        for i in issues:
            upvotes = Upvote.query.filter_by(issue_id=i.id).count()

            result.append({
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "category": i.category,
                "location": i.location,
                "status": i.status,
                "upvotes": upvotes
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upvote", methods=["POST"])
def upvote():
    data = request.json

    existing = Upvote.query.filter_by(
        user_id=data["user_id"],
        issue_id=data["issue_id"]
    ).first()

    if existing:
        return jsonify({"message": "Already upvoted"})

    vote = Upvote(
        user_id=data["user_id"],
        issue_id=data["issue_id"]
    )

    db.session.add(vote)
    db.session.commit()

    return jsonify({"message": "Upvoted"})

# -----------------------------
# RUN (LOCAL ONLY)
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)