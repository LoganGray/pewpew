import sys
import os
# Add user's local site-packages to Python path
user_site_packages = os.path.expanduser('~/.local/lib/python3.10/site-packages')
if user_site_packages not in sys.path:
    sys.path.append(user_site_packages)

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import geoip2.database
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='eventlet',
                   logger=True,
                   engineio_logger=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pewpew.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Initialize the GeoIP2 reader
reader = geoip2.database.Reader('GeoLite2-City.mmdb')


# Configuration for attack home IP
IP_HOME = "8.8.8.8"  # Default home IP, can be changed later
demo_mode = False  # Global flag for demo mode

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

class DestinationIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False, default=IP_HOME)
    is_default = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class IPAttack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source_ip = db.Column(db.String(15), nullable=False)
    source_country = db.Column(db.String(2))
    source_lat = db.Column(db.Float)
    source_long = db.Column(db.Float)
    dest_ip = db.Column(db.String(15), nullable=False, default=IP_HOME)
    dest_country = db.Column(db.String(2))
    dest_lat = db.Column(db.Float)
    dest_long = db.Column(db.Float)
    attack_type = db.Column(db.String(50), default="Manual IP Attack")

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

@app.route('/api/demo/status', methods=['GET'])
def demo_status():
    """Check if demo mode is enabled"""
    return jsonify({'demo_mode': demo_mode}), 200

@app.route('/api/attackfromip/<ip>', methods=['POST'])
def attack_from_ip(ip):
    """Record an attack from a specific IP address"""
    try:
        # Get current destination IP
        dest = get_current_destination()
        
        # Get geo locations for both source and destination IPs
        src_geo = reader.city(ip)
        dest_geo = reader.city(dest.ip)
        
        # Handle potential None values from GeoIP lookup
        attack = IPAttack(
            source_ip=ip,
            source_country=src_geo.country.iso_code if src_geo.country else None,
            source_lat=float(src_geo.location.latitude) if src_geo.location and src_geo.location.latitude else None,
            source_long=float(src_geo.location.longitude) if src_geo.location and src_geo.location.longitude else None,
            dest_ip=dest.ip,
            dest_country=dest_geo.country.iso_code if dest_geo.country else None,
            dest_lat=float(dest_geo.location.latitude) if dest_geo.location and dest_geo.location.latitude else None,
            dest_long=float(dest_geo.location.longitude) if dest_geo.location and dest_geo.location.longitude else None,
            attack_type=f"Manual attack from {ip}"
        )
        
        db.session.add(attack)
        db.session.commit()
        
        # Broadcast attack to all connected clients
        attack_data = {
            'id': attack.id,
            'timestamp': attack.timestamp.isoformat(),
            'source_ip': attack.source_ip,
            'dest_ip': attack.dest_ip,
            'attack_type': attack.attack_type,
            'geo': {
                'latitude': float(src_geo.location.latitude) if src_geo.location and src_geo.location.latitude else None,
                'longitude': float(src_geo.location.longitude) if src_geo.location and src_geo.location.longitude else None,
                'city': src_geo.city.name if src_geo.city else None,
                'country': src_geo.country.name if src_geo.country else None
            },
            'dest_geo': {
                'latitude': float(dest_geo.location.latitude) if dest_geo.location and dest_geo.location.latitude else None,
                'longitude': float(dest_geo.location.longitude) if dest_geo.location and dest_geo.location.longitude else None,
                'city': dest_geo.city.name if dest_geo.city else None,
                'country': dest_geo.country.name if dest_geo.country else None
            }
        }
        socketio.emit('new_attack', attack_data)
        
        return jsonify({
            'status': 'success',
            'message': f'Attack from {ip} recorded',
            'attack': attack_data
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/demo/<state>', methods=['POST'])
def toggle_demo(state):
    """Toggle demo mode on/off"""
    global demo_mode
    
    if state == 'on':
        demo_mode = True
        return jsonify({'status': 'success', 'message': 'Demo mode enabled'}), 200
    elif state == 'off':
        demo_mode = False
        return jsonify({'status': 'success', 'message': 'Demo mode disabled'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid state. Use "on" or "off"'}), 400

def get_current_destination():
    """Get the current destination IP from database"""
    dest = DestinationIP.query.order_by(DestinationIP.timestamp.desc()).first()
    if not dest:
        # Initialize with default if none exists
        dest = DestinationIP(ip=IP_HOME, is_default=True)
        db.session.add(dest)
        db.session.commit()
    return dest

@app.route('/api/setdestination', methods=['GET'])
def get_destination():
    """Get current destination IP"""
    dest = get_current_destination()
    return jsonify({
        'ip': dest.ip,
        'is_default': dest.is_default,
        'timestamp': dest.timestamp.isoformat()
    })

@app.route('/api/setdestination/<ip>', methods=['POST'])
def set_destination(ip):
    """Set new destination IP"""
    try:
        # Validate IP format
        import ipaddress
        ipaddress.ip_address(ip)  # Will raise ValueError if invalid
        
        # Create new destination record
        dest = DestinationIP(ip=ip, is_default=False)
        db.session.add(dest)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Destination IP set to {ip}',
            'destination': {
                'ip': dest.ip,
                'is_default': dest.is_default,
                'timestamp': dest.timestamp.isoformat()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid IP address: {ip}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

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


import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the database
with app.app_context():
    db_file = Path('pewpew.db')
    if not db_file.exists():
        logger.info("Database not found. Creating new database...")
        db.create_all()
        # Add default home IP to configuration
        logger.info(f"Database created successfully with default home IP: {IP_HOME}")
    else:
        logger.info("Existing database found")

if __name__ == '__main__':
    # Initialize WebSocket server
    socketio.init_app(app)
    socketio.run(app, 
                debug=True, 
                host='0.0.0.0', 
                port=5000,
                use_reloader=False,
                log_output=True)
