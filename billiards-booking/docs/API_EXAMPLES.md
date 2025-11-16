# API Usage Examples

## Table of Contents
- [Setup](#setup)
- [Table Types](#table-types)
- [Tables Management](#tables-management)
- [Bookings](#bookings)
- [Timeline](#timeline)
- [WebSocket Real-time Updates](#websocket-real-time-updates)

---

## Setup

All examples use `curl` and assume backend is running on `http://localhost:3000`.

Base URL: `http://localhost:3000/api`

---

## Table Types

### Get all table types

```bash
curl http://localhost:3000/api/table-types
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "russian",
      "displayName": "Русский бильярд",
      "sortOrder": 1,
      "color": "#8B5CF6",
      "createdAt": "2024-11-16T10:00:00.000Z",
      "_count": {
        "tables": 5
      }
    },
    {
      "id": 2,
      "name": "american_pool",
      "displayName": "Американский пул",
      "sortOrder": 2,
      "color": "#F59E0B",
      "createdAt": "2024-11-16T10:00:00.000Z",
      "_count": {
        "tables": 10
      }
    }
  ]
}
```

### Create a new table type

```bash
curl -X POST http://localhost:3000/api/table-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "snooker",
    "displayName": "Снукер",
    "sortOrder": 3,
    "color": "#10B981"
  }'
```

---

## Tables Management

### Get all tables

```bash
curl http://localhost:3000/api/tables
```

### Get tables by type

```bash
curl http://localhost:3000/api/tables?typeId=1
```

### Create a new table

```bash
curl -X POST http://localhost:3000/api/tables \
  -H "Content-Type: application/json" \
  -d '{
    "typeId": 1,
    "number": 6
  }'
```

### Bulk update table count

This is the recommended way to manage tables. It automatically creates or deactivates tables to match the desired count.

```bash
# Set Russian billiards tables to 7
curl -X POST http://localhost:3000/api/tables/bulk-update-count \
  -H "Content-Type: application/json" \
  -d '{
    "typeId": 1,
    "count": 7
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Added 2 table(s)",
  "data": [
    {
      "id": 6,
      "typeId": 1,
      "number": 6,
      "isActive": true
    },
    {
      "id": 7,
      "typeId": 1,
      "number": 7,
      "isActive": true
    }
  ]
}
```

### Deactivate a table (soft delete)

```bash
curl -X DELETE http://localhost:3000/api/tables/1
```

---

## Bookings

### Create a booking

**Important:** Times must account for overnight operations (12:00 PM - 04:00 AM).

```bash
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "tableId": 1,
    "startDatetime": "2024-11-16T14:00:00Z",
    "endDatetime": "2024-11-16T16:00:00Z",
    "customerName": "Иван Петров",
    "customerPhone": "+7 (999) 123-45-67"
  }'
```

**Success Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "tableId": 1,
    "businessDate": "2024-11-16T00:00:00.000Z",
    "startDatetime": "2024-11-16T14:00:00.000Z",
    "endDatetime": "2024-11-16T16:00:00.000Z",
    "customerName": "Иван Петров",
    "customerPhone": "+7 (999) 123-45-67",
    "status": "ACTIVE",
    "createdAt": "2024-11-16T10:30:00.000Z",
    "table": {
      "id": 1,
      "number": 1,
      "type": {
        "id": 1,
        "displayName": "Русский бильярд",
        "color": "#8B5CF6"
      }
    }
  }
}
```

**Error Response (Overlap):**
```json
{
  "success": false,
  "error": {
    "message": "This time slot overlaps with an existing booking"
  }
}
```

### Create overnight booking (crosses midnight)

For bookings that go past midnight (e.g., 22:00 - 02:00):

```bash
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "tableId": 2,
    "startDatetime": "2024-11-16T22:00:00Z",
    "endDatetime": "2024-11-17T02:00:00Z",
    "customerName": "Алексей Сидоров",
    "customerPhone": "+7 (999) 987-65-43"
  }'
```

**Note:** The `businessDate` will be `2024-11-16` even though `endDatetime` is the next day.

### Get all bookings

```bash
curl http://localhost:3000/api/bookings
```

### Get bookings for a specific date

```bash
curl http://localhost:3000/api/bookings?businessDate=2024-11-16
```

### Get bookings for a specific table

```bash
curl http://localhost:3000/api/bookings?tableId=1
```

### Get a specific booking

```bash
curl http://localhost:3000/api/bookings/1
```

### Update a booking

```bash
curl -X PUT http://localhost:3000/api/bookings/1 \
  -H "Content-Type: application/json" \
  -d '{
    "customerName": "Иван Иванович Петров",
    "customerPhone": "+7 (999) 111-22-33"
  }'
```

### Cancel a booking

```bash
curl -X DELETE http://localhost:3000/api/bookings/1
```

### Complete a booking

```bash
curl -X POST http://localhost:3000/api/bookings/1/complete
```

---

## Timeline

### Get timeline view for a business date

This is the main endpoint for the mobile app's timeline view.

```bash
curl http://localhost:3000/api/bookings/timeline?businessDate=2024-11-16
```

**Response:**
```json
{
  "success": true,
  "data": {
    "businessDate": "2024-11-16",
    "tableTypes": [
      {
        "id": 1,
        "name": "russian",
        "displayName": "Русский бильярд",
        "sortOrder": 1,
        "color": "#8B5CF6",
        "tables": [
          {
            "id": 1,
            "typeId": 1,
            "number": 1,
            "isActive": true,
            "bookings": [
              {
                "id": 1,
                "tableId": 1,
                "businessDate": "2024-11-16T00:00:00.000Z",
                "startDatetime": "2024-11-16T14:00:00.000Z",
                "endDatetime": "2024-11-16T16:00:00.000Z",
                "customerName": "Иван Петров",
                "customerPhone": "+7 (999) 123-45-67",
                "status": "ACTIVE"
              }
            ]
          },
          {
            "id": 2,
            "typeId": 1,
            "number": 2,
            "isActive": true,
            "bookings": []
          }
        ]
      },
      {
        "id": 2,
        "name": "american_pool",
        "displayName": "Американский пул",
        "sortOrder": 2,
        "color": "#F59E0B",
        "tables": [
          {
            "id": 11,
            "typeId": 2,
            "number": 1,
            "isActive": true,
            "bookings": [
              {
                "id": 2,
                "tableId": 11,
                "businessDate": "2024-11-16T00:00:00.000Z",
                "startDatetime": "2024-11-16T18:30:00.000Z",
                "endDatetime": "2024-11-16T20:00:00.000Z",
                "customerName": "Алексей Сидоров",
                "status": "ACTIVE"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## WebSocket Real-time Updates

### JavaScript Example

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3000');

// Connect
socket.on('connect', () => {
  console.log('Connected to WebSocket');

  // Join a specific business date room
  socket.emit('join-date', '2024-11-16');
});

// Listen for booking events
socket.on('booking-created', (booking) => {
  console.log('New booking created:', booking);
  // Update UI with new booking
});

socket.on('booking-updated', (booking) => {
  console.log('Booking updated:', booking);
  // Update UI with modified booking
});

socket.on('booking-cancelled', (booking) => {
  console.log('Booking cancelled:', booking);
  // Remove or grey out booking in UI
});

socket.on('table-created', (table) => {
  console.log('New table added:', table);
});

socket.on('table-updated', (table) => {
  console.log('Table updated:', table);
});

// Leave a room
socket.emit('leave-date', '2024-11-16');

// Disconnect
socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket');
});
```

### React Native Example (with Socket.io)

```javascript
import { useEffect } from 'react';
import io from 'socket.io-client';

function useBookingSocket(businessDate, onBookingUpdate) {
  useEffect(() => {
    const socket = io('http://localhost:3000');

    socket.on('connect', () => {
      socket.emit('join-date', businessDate);
    });

    socket.on('booking-created', onBookingUpdate);
    socket.on('booking-updated', onBookingUpdate);
    socket.on('booking-cancelled', onBookingUpdate);

    return () => {
      socket.emit('leave-date', businessDate);
      socket.disconnect();
    };
  }, [businessDate, onBookingUpdate]);
}

// Usage in component
function TimelineScreen() {
  const [businessDate, setBusinessDate] = useState('2024-11-16');
  const queryClient = useQueryClient();

  useBookingSocket(businessDate, () => {
    // Invalidate queries to refetch data
    queryClient.invalidateQueries(['timeline', businessDate]);
  });

  // ... rest of component
}
```

---

## Common Scenarios

### Scenario 1: Customer wants to book for 2 hours starting at 8 PM

```bash
# 8 PM to 10 PM on Nov 16
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "tableId": 1,
    "startDatetime": "2024-11-16T20:00:00Z",
    "endDatetime": "2024-11-16T22:00:00Z",
    "customerName": "Мария Иванова"
  }'
```

### Scenario 2: Late night booking (11 PM - 1 AM)

```bash
# 11 PM Nov 16 to 1 AM Nov 17 (same business date: Nov 16)
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "tableId": 2,
    "startDatetime": "2024-11-16T23:00:00Z",
    "endDatetime": "2024-11-17T01:00:00Z",
    "customerName": "Петр Смирнов"
  }'
```

### Scenario 3: Admin increases American pool tables from 10 to 15

```bash
curl -X POST http://localhost:3000/api/tables/bulk-update-count \
  -H "Content-Type: application/json" \
  -d '{
    "typeId": 2,
    "count": 15
  }'
```

### Scenario 4: Check if table is available at specific time

```bash
# Get all bookings for table #1
curl http://localhost:3000/api/bookings?tableId=1&businessDate=2024-11-16

# Check the response for any overlapping bookings
# If no bookings overlap with your desired time, the slot is available
```

---

## Error Codes

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 409 | Conflict (booking overlap) |
| 500 | Internal Server Error |

---

## Validation Rules

### Booking Time Validation

- End time must be after start time
- Both times must be within operating hours (12:00-04:00)
- Both times must be on the same business date
- Minimum booking duration: 30 minutes
- No overlapping bookings on the same table

### Table Validation

- Table number must be unique within its type
- Cannot delete a table with active bookings (use soft delete)

---

## Tips

1. **Always use business date for queries** - Don't use calendar date directly, calculate business date first
2. **Handle overnight bookings carefully** - End datetime can be next calendar day
3. **Use WebSocket for real-time updates** - Don't poll the API excessively
4. **Validate on both client and server** - Client validation for UX, server validation for security
5. **Use bulk operations for admin tasks** - More efficient than individual table creation
