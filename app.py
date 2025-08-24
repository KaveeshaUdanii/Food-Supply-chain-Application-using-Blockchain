# app.py
import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models import db, User, Product
from blockchain import Blockchain
from pathlib import Path
import pandas as pd
from data_simulation import generate_sample_batch
from werkzeug.security import generate_password_hash
from flask import request, redirect, url_for, flash, render_template

from flask import render_template
import pandas as pd
import plotly.express as px
import json

import plotly
import plotly.graph_objs as go
from collections import Counter

from collections import Counter, defaultdict
import json
from flask import render_template
from flask_login import current_user
from models import Product 


from collections import defaultdict
import json, random
from datetime import datetime
from models import Product, db



BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "app.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretdevkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    blockchain = Blockchain()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize database tables right after app creation
    with app.app_context():
        db.create_all()

    # --- Authentication routes ---
    from werkzeug.security import generate_password_hash
    from flask import request, redirect, url_for, flash, render_template

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']   # required field
            role = request.form.get('role', 'farmer')

            # Check if username already exists
            if User.query.filter_by(username=username).first():
                flash("Username already exists", "danger")
                return redirect(url_for('signup'))

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash("Email already in use", "danger")
                return redirect(url_for('signup'))

            # Hash the password
            hash_pw = generate_password_hash(password)

            # Create user
            user = User(username=username, email=email, password_hash=hash_pw, role=role)
            db.session.add(user)
            db.session.commit()

            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for('login'))

        # GET request → render signup form
        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for("dashboard"))
            flash("Invalid credentials", "danger")
            return redirect(url_for('login'))
        return render_template("login.html")

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # --- Index & Dashboard ---
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        products = Product.query.filter(
            (Product.owner_id == current_user.id) | (current_user.role == 'admin')
        ).all()
        total_blocks = len(blockchain.chain)
        total_transactions = sum(len(b.transactions) for b in blockchain.chain)
        return render_template(
            "dashboard.html",
            products=products,
            total_blocks=total_blocks,
            total_transactions=total_transactions
        )

    # --- Product registration ---
    @app.route("/product/register", methods=["GET", "POST"])
    @login_required
    def register_product():
        if request.method == "POST":
            product_type = request.form['name']       # renamed from 'name'
            origin = request.form['origin']
            batch_id = request.form.get('batch_id') or str(uuid.uuid4())[:8]
            temp = float(request.form.get('temperature', 0))
            humidity = float(request.form.get('humidity', 0))
            notes = request.form.get('notes', '')

            # Check if batch_id already exists
            if Product.query.filter_by(batch_id=batch_id).first():
                flash("Batch ID already exists. Pick another or leave blank to auto-generate.", "danger")
                return redirect(url_for('register_product'))

            # Create Product
            product = Product(
                batch_id=batch_id,
                product_type=product_type,
                origin=origin,
                owner_id=current_user.id,
                current_owner=current_user.username,
                product_metadata=json.dumps({
                    'temperature': temp,
                    'humidity': humidity,
                    'notes': notes
                })
            )

            db.session.add(product)
            db.session.commit()

            # Add transaction to blockchain
            tx = {
                'type': 'create',
                'batch_id': batch_id,
                'product_name': product_type,
                'origin': origin,
                'owner': current_user.username,
                'timestamp': datetime.utcnow().timestamp(),
                'metadata': {'temperature': temp, 'humidity': humidity, 'notes': notes}
            }
            blockchain.add_transaction(tx)
            mined = blockchain.mine()

            flash(f"Product registered and block mined (index {mined['index']}).", "success")
            return redirect(url_for('dashboard'))

        return render_template("register.html")

    # --- Transfer ownership ---
    @app.route("/product/transfer/<int:product_id>", methods=["GET", "POST"])
    @login_required
    def transfer(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == "POST":
            new_owner_username = request.form['new_owner']
            temp = float(request.form.get('temperature', 0))
            humidity = float(request.form.get('humidity', 0))
            notes = request.form.get('notes', '')
            new_owner = User.query.filter_by(username=new_owner_username).first()
            if not new_owner:
                flash("Target owner not found.", "danger")
                return redirect(url_for('transfer', product_id=product_id))
            old_owner = User.query.get(product.owner_id)
            product.owner_id = new_owner.id
            product.last_update = datetime.utcnow()
            product.product_metadata = json.dumps({'temperature': temp, 'humidity': humidity, 'notes': notes})
            db.session.commit()
            tx = {
                'type': 'transfer',
                'batch_id': product.batch_id,
                'from': old_owner.username if old_owner else 'unknown',
                'to': new_owner.username,
                'timestamp': datetime.utcnow().timestamp(),
                'metadata': {'temperature': temp, 'humidity': humidity, 'notes': notes}
            }
            blockchain.add_transaction(tx)
            mined = blockchain.mine()
            flash(f"Product transferred and block mined (index {mined['index']}).", "success")
            return redirect(url_for('dashboard'))
        users = User.query.filter(User.id != product.owner_id).all()
        return render_template("transfer.html", product=product, users=users)

    # --- History & Traceability ---
    @app.route("/product/history/<batch_id>")
    @login_required
    def history(batch_id):
        history = blockchain.get_product_history(batch_id)
        return render_template("history.html", history=history, batch_id=batch_id)


    #-------------stats-------------------#
    @app.route("/analytics")
    def analytics():
        # --- Base stats ---
        total_products = Product.query.count()
        user_products = Product.query.filter_by(owner_id=current_user.id).count()
        
        # Temperature & Humidity Violations
        products = Product.query.all()
        temp_violations = 0
        humidity_violations = 0
        safety_data = []
        violations_per_owner = defaultdict(int)
        risky_locations = defaultdict(int)

        for p in products:
            if p.product_metadata:
                meta = json.loads(p.product_metadata)
                temp = meta.get("temperature", 0)
                hum = meta.get("humidity", 0)
                notes = meta.get("notes", "")
                ts = p.timestamp.strftime("%Y-%m-%d %H:%M")

                # Collect line data
                safety_data.append({
                    "timestamp": ts,
                    "temperature": temp,
                    "humidity": hum,
                    "owner": p.current_owner
                })

                # Violations
                if temp > 25:
                    temp_violations += 1
                    violations_per_owner[p.current_owner] += 1
                    risky_locations[p.origin] += 1
                if hum > 60:
                    humidity_violations += 1
                    violations_per_owner[p.current_owner] += 1
                    risky_locations[p.origin] += 1

        # --- Food Safety Charts ---
        safety_line_json = {
            "timestamps": [d["timestamp"] for d in safety_data],
            "temperature": [d["temperature"] for d in safety_data],
            "humidity": [d["humidity"] for d in safety_data],
        }

        violations_bar_json = {
            "owners": list(violations_per_owner.keys()),
            "violations": list(violations_per_owner.values())
        }

        heatmap_json = {
            "locations": list(risky_locations.keys()),
            "counts": list(risky_locations.values())
        }

        # --- Fraud Detection (Simulated) ---
        fraud_pie_json = {
            "labels": ["Normal Transfers", "Suspicious Transfers"],
            "values": [len(products) - 3, 3]
        }

        fraud_scatter_json = {
            "distance": [random.randint(50, 500) for _ in range(20)],
            "time": [random.randint(1, 24) for _ in range(20)]
        }

        fraud_network_json = {
            "nodes": ["Farmer1", "Distributor1", "Retailer1", "Retailer2"],
            "links": [("Farmer1","Distributor1"), ("Distributor1","Retailer1"), ("Retailer1","Distributor1")]
        }

        # --- Supply Chain Performance ---
        owner_counts = defaultdict(int)
        status_counts = defaultdict(int)
        transport_durations = []

        for p in products:
            owner_counts[p.current_owner] += 1
            status_counts[p.status] += 1
            transport_durations.append(random.randint(1, 10))

        performance_bar_json = {
            "owners": list(owner_counts.keys()),
            "counts": list(owner_counts.values())
        }

        performance_stacked_json = {
            "statuses": list(status_counts.keys()),
            "counts": list(status_counts.values())
        }

        performance_timeline_json = {
            "batches": [p.batch_id for p in products],
            "durations": transport_durations
        }

        return render_template("analytics.html",
                            total_products=total_products,
                            user_products=user_products,
                            temp_violations=temp_violations,
                            humidity_violations=humidity_violations,
                            # Food Safety
                            safety_line_json=safety_line_json,
                            violations_bar_json=violations_bar_json,
                            heatmap_json=heatmap_json,
                            # Fraud Detection
                            fraud_pie_json=fraud_pie_json,
                            fraud_scatter_json=fraud_scatter_json,
                            fraud_network_json=fraud_network_json,
                            # Supply Chain
                            performance_bar_json=performance_bar_json,
                            performance_stacked_json=performance_stacked_json,
                            performance_timeline_json=performance_timeline_json)


    # --- Validate chain ---
    @app.route("/chain/validate")
    @login_required
    def validate():
        valid = blockchain.is_valid_chain()
        return render_template("validate.html", valid=valid, length=len(blockchain.chain))

    # --- API endpoints ---
    @app.route("/api/chain")
    def api_chain():
        return jsonify([b.to_dict() for b in blockchain.chain])

    @app.route("/api/seed")
    @login_required
    def api_seed():
        if current_user.role != 'admin':
            return jsonify({'error': 'unauthorized'}), 403
        for _ in range(5):
            b = generate_sample_batch(current_user.username)
            if Product.query.filter_by(batch_id=b['batch_id']).first():
                continue
            product = Product(
                batch_id=b['batch_id'],
                name=b['product_name'],
                origin=b['origin'],
                owner_id=current_user.id,
                product_metadata=json.dumps(b['metadata'])
            )
            db.session.add(product)
            db.session.commit()
            blockchain.add_transaction({
                'type': 'create',
                'batch_id': b['batch_id'],
                'product_name': b['product_name'],
                'origin': b['origin'],
                'owner': current_user.username,
                'timestamp': b['timestamp'],
                'metadata': b['metadata']
            })
            blockchain.mine()
        return jsonify({'status': 'seeded'})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
