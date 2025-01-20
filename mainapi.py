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
# Configure database path
import os
from pathlib import Path

# Use /data volume in Docker, fallback to local database directory
db_dir = Path(os.getenv('DATABASE_DIR', 'database'))
db_dir.mkdir(exist_ok=True, mode=0o777)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{db_dir}/pewpew.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Initialize the GeoIP2 reader
reader = geoip2.database.Reader('GeoLite2-City.mmdb')


# Configuration for attack home IP
IP_HOME = "8.8.8.8"  # Default home IP, can be changed later
def get_config(key, default=None):
    """Get a configuration value from database"""
    config = Config.query.filter_by(key=key).first()
    if config:
        return config.value == 'True' if default is False else config.value
    return default

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

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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
    demo_mode = get_config('demo_mode', False)
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
    if state not in ['on', 'off']:
        return jsonify({'status': 'error', 'message': 'Invalid state. Use "on" or "off"'}), 400
        
    # Update or create config entry
    config = Config.query.filter_by(key='demo_mode').first()
    if not config:
        config = Config(key='demo_mode')
        db.session.add(config)
    
    config.value = str(state == 'on')
    db.session.commit()
    
    socketio.emit('demo_mode_change', {'demo_mode': state == 'on'})
    return jsonify({
        'status': 'success',
        'message': f'Demo mode {"enabled" if state == "on" else "disabled"}',
        'demo_mode': state == 'on'
    }), 200

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
        
        # Broadcast destination change to all clients
        socketio.emit('destination_change', {
            'ip': dest.ip,
            'is_default': dest.is_default,
            'timestamp': dest.timestamp.isoformat()
        })
        
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
    try:
        # Get database directory from environment or use default
        db_dir = Path(os.getenv('DATABASE_DIR', 'database'))
        
        # Create database directory with proper permissions
        db_dir.mkdir(exist_ok=True, mode=0o777)
        
        # Set full path for database file
        db_path = db_dir / 'pewpew.db'
        
        # Initialize database if it doesn't exist
        if not db_path.exists():
            logger.info("Database not found. Creating new database...")
            
            # Create all tables
            db.create_all()
            
            # Add default home IP
            dest = DestinationIP(ip=IP_HOME, is_default=True)
            db.session.add(dest)
            
            # Add default demo mode config
            demo_config = Config(key='demo_mode', value='False')
            db.session.add(demo_config)
            
            db.session.commit()
            
            # Set permissions on database file
            try:
                db_path.chmod(0o666)  # Read/write for all
            except Exception as perm_error:
                logger.warning(f"Could not set permissions on database file: {perm_error}")
            
            logger.info(f"Database created successfully with default home IP: {IP_HOME}")
        else:
            logger.info("Existing database found")
            
        # Verify database is writable
        try:
            test_config = Config(key='test', value='test')
            db.session.add(test_config)
            db.session.commit()
            db.session.delete(test_config)
            db.session.commit()
            logger.info("Database write test successful")
        except Exception as write_error:
            logger.error(f"Database write test failed: {write_error}")
            raise
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # Try to continue running even if database initialization fails
        # This allows the API to run in a degraded mode

if __name__ == '__main__':
    # Initialize WebSocket server
    socketio.init_app(app)
    socketio.run(app, 
                debug=True, 
                host='0.0.0.0', 
                port=5000,
                use_reloader=False,
                log_output=True)
