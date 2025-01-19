from flask import Flask, jsonify, request
import geoip2.database
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pewpew.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Initialize the GeoIP2 reader
reader = geoip2.database.Reader('GeoLite2-City.mmdb')


class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source_ip = db.Column(db.String(15))
    source_country = db.Column(db.String(2))
    source_lat = db.Column(db.Float)
    source_long = db.Column(db.Float)
    dest_ip = db.Column(db.String(15))
    dest_country = db.Column(db.String(2))
    dest_lat = db.Column(db.Float)
    dest_long = db.Column(db.Float)
    attack_type = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'source': {
                'ip': self.source_ip,
                'country': self.source_country,
                'latitude': self.source_lat,
                'longitude': self.source_long
            },
            'destination': {
                'ip': self.dest_ip,
                'country': self.dest_country,
                'latitude': self.dest_lat,
                'longitude': self.dest_long
            },
            'attack_type': self.attack_type
        }

@app.route('/api/attacks', methods=['GET'])
def get_attacks():
    """Return all recorded attacks"""
    attacks = Attack.query.order_by(Attack.timestamp.desc()).limit(100).all()
    return jsonify([attack.to_dict() for attack in attacks])

@app.route('/api/attacks', methods=['POST'])
def add_attack():
    """Record a new attack"""
    attack = Attack(
        source_ip=request.json.get('source_ip'),
        source_country=request.json.get('source_country'),
        source_lat=request.json.get('source_lat'),
        source_long=request.json.get('source_long'),
        dest_ip=request.json.get('dest_ip'),
        dest_country=request.json.get('dest_country'),
        dest_lat=request.json.get('dest_lat'),
        dest_long=request.json.get('dest_long'),
        attack_type=request.json.get('attack_type')
    )
    db.session.add(attack)
    db.session.commit()
    return jsonify(attack.to_dict()), 201

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return basic attack statistics"""
    stats = {
        'total_attacks': Attack.query.count(),
        'unique_sources': Attack.query.distinct(Attack.source_country).count(),
        'unique_destinations': Attack.query.distinct(Attack.dest_country).count()
    }
    return jsonify(stats)

@app.route('/api/ip2geo', methods=['GET'])
def ip_to_geo():
    ip_address = request.args.get('ip')
    
    if not ip_address:
        return jsonify({'error': 'No IP address provided. Use ?ip=X.X.X.X'}), 400
    
    try:
        response = reader.city(ip_address)
        return jsonify({
            'latitude': float(response.location.latitude),
            'longitude': float(response.location.longitude),
            'city': response.city.name,
            'country': response.country.name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
