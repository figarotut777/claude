# 🚀 Quick Start Guide

Get the Billiards Booking App running in 5 minutes!

## Option 1: Docker (Fastest) ⚡

```bash
cd billiards-booking

# Start backend + database
docker-compose up -d

# Wait 10 seconds for database to initialize, then:
docker-compose exec backend npx prisma db push
docker-compose exec backend npm run db:seed

# ✅ Backend running at http://localhost:3000
```

Test it:
```bash
curl http://localhost:3000/health
# Should return: {"status":"ok",...}
```

## Option 2: Local Development 💻

### Backend

```bash
cd billiards-booking/backend

# Install dependencies
npm install

# Start PostgreSQL (via Docker)
docker run --name billiards-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=billiards \
  -p 5432:5432 \
  -d postgres:16-alpine

# Setup database
npx prisma db push
npm run db:seed

# Start server
npm run dev

# ✅ Backend running at http://localhost:3000
```

### Mobile App

```bash
cd billiards-booking/mobile

# Install dependencies
npm install

# Start Expo
npx expo start

# Choose your platform:
# - Press 'i' for iOS simulator
# - Press 'a' for Android emulator
# - Scan QR code with Expo Go app
```

**Important:** Update the API URL in `mobile/src/config/api.js` if using a physical device:

```javascript
// Find your computer's IP address:
// Mac: System Preferences → Network
// Windows: ipconfig
// Linux: ifconfig

const API_BASE_URL = 'http://YOUR_IP:3000/api'; // e.g., http://192.168.1.100:3000/api
```

## Default Login

No authentication implemented yet - all features are open.

## Default Data (After Seeding)

- **2 table types:** Russian Billiards (5 tables), American Pool (10 tables)
- **2 sample bookings** for today

## Verify Installation

### Backend Health Check
```bash
curl http://localhost:3000/health
```

### Get Timeline Data
```bash
curl http://localhost:3000/api/bookings/timeline?businessDate=2024-11-16
```

### View Database
```bash
cd backend
npm run db:studio
# Opens Prisma Studio at http://localhost:5555
```

## Common Issues

### Port 3000 already in use
```bash
# Change PORT in backend/.env
PORT=3001
```

### Cannot connect from mobile
- Make sure backend is running
- Check firewall allows connections
- Use your computer's IP address, not localhost
- Mobile device and computer must be on same network

### Database connection error
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend npx prisma db push
docker-compose exec backend npm run db:seed
```

### Expo cache issues
```bash
cd mobile
npx expo start -c  # Start with cleared cache
```

## Next Steps

1. ✅ Backend running
2. ✅ Mobile app running
3. 📱 Create your first booking in the app
4. ⚙️ Try the admin panel (gear icon)
5. 📖 Read full [README.md](README.md) for detailed documentation

## Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for deploying to:
- Railway / Render (Backend)
- App Store / Google Play (Mobile)

## Need Help?

Check these files:
- [README.md](README.md) - Full documentation
- [API_EXAMPLES.md](docs/API_EXAMPLES.md) - API usage examples
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment guide

---

**Happy coding! 🎱**
