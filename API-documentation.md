# IPew API Documentation

## Base URL
`http://localhost:5000/api`

## Endpoints

### 1. Record an Attack
**POST** `/attacks`

Records a new attack in the database.

#### Request Body
```json
{
  "source_ip": "1.2.3.4",
  "source_country": "US",
  "source_lat": 37.7749,
  "source_long": -122.4194,
  "dest_ip": "8.8.8.8",
  "dest_country": "US",
  "dest_lat": 34.0522,
  "dest_long": -118.2437,
  "attack_type": "SYN Flood"
}
```

#### Example
```bash
curl -X POST http://localhost:5000/api/attacks \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "1.2.3.4",
    "source_country": "US",
    "source_lat": 37.7749,
    "source_long": -122.4194,
    "dest_ip": "8.8.8.8",
    "dest_country": "US",
    "dest_lat": 34.0522,
    "dest_long": -118.2437,
    "attack_type": "SYN Flood"
  }'
```

### 2. Get Recent Attacks
**GET** `/attacks`

Returns the most recent 100 attacks.

#### Example
```bash
curl http://localhost:5000/api/attacks
```

### 3. Get Attack Statistics
**GET** `/stats`

Returns basic attack statistics.

#### Example
```bash
curl http://localhost:5000/api/stats
```

### 4. Record Attack from Specific IP
**POST** `/attackfromip/<ip>`

Records an attack from a specific IP address to the default home IP.

#### Example
```bash
curl -X POST http://localhost:5000/api/attackfromip/1.2.3.4
```

### 5. Get Geo Location for IP
**GET** `/ip2geo`

Returns geo location information for an IP address.

#### Parameters
- `ip`: IP address to lookup

#### Example
```bash
curl http://localhost:5000/api/ip2geo?ip=1.2.3.4
```

### 6. Demo Mode Control
**POST** `/demo/<state>`

Controls demo mode (on/off).

#### Parameters
- `state`: "on" or "off"

#### Examples
Enable demo mode:
```bash
curl -X POST http://localhost:5000/api/demo/on
```

Disable demo mode:
```bash
curl -X POST http://localhost:5000/api/demo/off
```

### 7. Check Demo Mode Status
**GET** `/demo/status`

Returns current demo mode status.

#### Example
```bash
curl http://localhost:5000/api/demo/status
```

### 8. Get Current Destination
**GET** `/setdestination`

Returns current destination IP configuration.

#### Example
```bash
curl http://localhost:5000/api/setdestination
```

### 9. Set New Destination
**POST** `/setdestination/<ip>`

Sets a new destination IP address.

#### Example
```bash
curl -X POST http://localhost:5000/api/setdestination/1.1.1.1
```

## WebSocket Events

### New Attack Event
When a new attack is recorded, the server emits a `new_attack` event with the attack data.

#### Example Data
```json
{
  "id": 123,
  "timestamp": "2025-01-20T12:34:56.789012",
  "source_ip": "1.2.3.4",
  "dest_ip": "8.8.8.8",
  "attack_type": "Manual attack from 1.2.3.4",
  "geo": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "city": "San Francisco",
    "country": "United States"
  }
}
```

## Error Responses
All API endpoints return JSON responses with the following structure for errors:

```json
{
  "status": "error",
  "message": "Error description"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error
