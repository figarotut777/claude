# Deployment Guide

Complete guide for deploying Billiards Booking App to production.

## Table of Contents

- [Backend Deployment](#backend-deployment)
  - [Railway](#railway)
  - [Render](#render)
  - [DigitalOcean](#digitalocean)
- [Mobile App Deployment](#mobile-app-deployment)
  - [iOS (App Store)](#ios-app-store)
  - [Android (Google Play)](#android-google-play)
- [Environment Variables](#environment-variables)
- [Database Migration](#database-migration)
- [Monitoring](#monitoring)

---

## Backend Deployment

### Railway

Railway is the easiest option with built-in PostgreSQL.

1. **Create account** at https://railway.app

2. **Create new project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Navigate to backend folder
   cd billiards-booking/backend

   # Initialize
   railway init

   # Add PostgreSQL
   railway add postgresql

   # Deploy
   railway up
   ```

3. **Set environment variables**
   ```bash
   railway variables set NODE_ENV=production
   railway variables set PORT=3000
   railway variables set CLUB_OPENING_HOUR=12
   railway variables set CLUB_CLOSING_HOUR=4
   ```

4. **Database is automatically connected via `DATABASE_URL`**

5. **Run migrations**
   ```bash
   railway run npx prisma db push
   railway run npm run db:seed
   ```

6. **Get your public URL**
   ```bash
   railway domain
   ```

### Render

1. **Create account** at https://render.com

2. **Create PostgreSQL database**
   - New → PostgreSQL
   - Note down the Internal Database URL

3. **Create Web Service**
   - New → Web Service
   - Connect your GitHub repo
   - Root Directory: `billiards-booking/backend`
   - Build Command: `npm install && npx prisma generate`
   - Start Command: `npm start`

4. **Environment Variables**
   ```
   NODE_ENV=production
   DATABASE_URL=<your-postgres-internal-url>
   PORT=3000
   CLUB_OPENING_HOUR=12
   CLUB_CLOSING_HOUR=4
   ```

5. **After first deploy, run migrations**
   - Go to Shell tab
   - Run: `npx prisma db push && npm run db:seed`

### DigitalOcean App Platform

1. **Create Managed PostgreSQL Database**
   - Databases → Create Database
   - Choose your region
   - Note connection string

2. **Deploy App**
   - Apps → Create App
   - Choose GitHub repo
   - Detect Dockerfile automatically

3. **Environment Variables** (same as above)

4. **Run migrations via console or SSH**

---

## Mobile App Deployment

### Prerequisites

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Navigate to mobile folder
cd billiards-booking/mobile
```

### Configure EAS

```bash
# Initialize EAS
eas build:configure
```

This creates `eas.json`:

```json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {}
  }
}
```

### Update API URL for Production

In `mobile/src/config/api.js`:

```javascript
const API_BASE_URL = __DEV__
  ? 'http://localhost:3000/api'
  : 'https://your-production-backend.railway.app/api'; // ← Update this

export const WEBSOCKET_URL = __DEV__
  ? 'http://localhost:3000'
  : 'https://your-production-backend.railway.app'; // ← Update this
```

### iOS (App Store)

1. **Prerequisites**
   - Apple Developer Account ($99/year)
   - App Store Connect app created

2. **Build for iOS**
   ```bash
   eas build --platform ios --profile production
   ```

3. **Submit to App Store**
   ```bash
   eas submit --platform ios --latest
   ```

   Or manually:
   - Download `.ipa` from EAS
   - Upload via Transporter app
   - Submit for review in App Store Connect

4. **App Store Metadata**
   - App Name: "Billiards Booking"
   - Category: Business / Lifestyle
   - Screenshots (required sizes):
     - 6.7" (iPhone 14 Pro Max): 1290 x 2796
     - 6.5" (iPhone 11 Pro Max): 1242 x 2688
     - 5.5" (iPhone 8 Plus): 1242 x 2208
   - App Icon: 1024x1024 PNG

### Android (Google Play)

1. **Prerequisites**
   - Google Play Developer Account ($25 one-time)
   - Play Console app created

2. **Build for Android**
   ```bash
   eas build --platform android --profile production
   ```

3. **Submit to Google Play**
   ```bash
   eas submit --platform android --latest
   ```

   Or manually:
   - Download `.aab` from EAS
   - Upload to Play Console
   - Fill out store listing

4. **Play Store Metadata**
   - App Name: "Billiards Booking"
   - Category: Business
   - Screenshots (required):
     - Phone: 16:9 ratio (1920x1080 recommended)
     - 7-inch tablet: 16:9
     - 10-inch tablet: 16:9
   - Feature Graphic: 1024w x 500h
   - App Icon: 512x512 PNG

---

## Environment Variables

### Backend

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `PORT` | Server port | 3000 | ❌ |
| `NODE_ENV` | Environment | development | ❌ |
| `CLUB_OPENING_HOUR` | Opening hour (24h format) | 12 | ❌ |
| `CLUB_CLOSING_HOUR` | Closing hour (24h format) | 4 | ❌ |
| `ENABLE_WEBSOCKET` | Enable WebSocket | true | ❌ |

### Mobile

Configured in `app.json` and `src/config/api.js`:

- `API_BASE_URL` - Backend API URL
- `WEBSOCKET_URL` - WebSocket server URL

---

## Database Migration

### When updating schema

1. **Update `backend/prisma/schema.prisma`**

2. **Generate migration**
   ```bash
   npx prisma migrate dev --name descriptive_name
   ```

3. **Deploy to production**
   ```bash
   # Railway
   railway run npx prisma migrate deploy

   # Render (via Shell)
   npx prisma migrate deploy

   # Or use db push for development
   npx prisma db push
   ```

### Backup production database

**Railway:**
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

**Render:**
```bash
pg_dump <your-database-url> > backup.sql
```

**Restore:**
```bash
psql $DATABASE_URL < backup.sql
```

---

## CORS Configuration

Update `backend/src/index.js` for production:

```javascript
app.use(cors({
  origin: [
    'https://your-domain.com',
    'exp://your-expo-app',
  ],
  credentials: true
}));
```

---

## SSL/HTTPS

Most platforms (Railway, Render) provide automatic HTTPS.

If self-hosting:

1. Use **Nginx** as reverse proxy
2. Get free SSL with **Let's Encrypt**
3. Configure auto-renewal

Example Nginx config:

```nginx
server {
    listen 80;
    server_name api.billiards-booking.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.billiards-booking.com;

    ssl_certificate /etc/letsencrypt/live/api.billiards-booking.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.billiards-booking.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Monitoring

### Backend Monitoring

**1. Health endpoint**
```bash
curl https://your-api.com/health
```

**2. Set up monitoring service**
- **UptimeRobot** (free) - ping every 5 minutes
- **Better Uptime** - advanced monitoring
- **New Relic** - APM

**3. Logging**

Add structured logging with **Winston**:

```javascript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Use in code
logger.info('Booking created', { bookingId: booking.id });
logger.error('Database error', { error: err.message });
```

### Mobile Monitoring

**1. Expo Application Services**
- Automatic crash reporting
- Performance metrics
- User analytics

**2. Sentry** (optional)
```bash
npm install @sentry/react-native

# Add to app/_layout.js
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: 'your-sentry-dsn',
  enableInExpoDevelopment: false,
});
```

---

## Performance Optimization

### Backend

1. **Add database indexes**
   ```prisma
   model Booking {
     // ...
     @@index([businessDate, tableId])
     @@index([startDatetime, endDatetime])
   }
   ```

2. **Enable connection pooling** (included in Prisma)

3. **Add Redis caching** (optional)
   ```bash
   npm install redis
   ```

### Mobile

1. **Image optimization**
   - Use optimized images for splash/icon
   - Compress assets

2. **Bundle size**
   ```bash
   npx expo-doctor
   ```

3. **Performance profiling**
   - Use React DevTools
   - Monitor re-renders

---

## Rollback Strategy

1. **Keep previous builds**
   ```bash
   # iOS
   eas build:list --platform ios

   # Android
   eas build:list --platform android
   ```

2. **Database migrations**
   - Always backup before migration
   - Test migrations on staging first
   - Keep rollback scripts

3. **Backend rollback**
   - Railway/Render: Redeploy previous version
   - Or use Git tags for version control

---

## Checklist

### Before Production Launch

- [ ] Update API URLs in mobile app
- [ ] Configure CORS for production domain
- [ ] Set up database backups
- [ ] Enable HTTPS
- [ ] Set up monitoring/alerts
- [ ] Test all features on production
- [ ] Load testing (optional)
- [ ] Security audit (optional)
- [ ] Privacy policy & Terms of Service
- [ ] App Store/Play Store listings complete

### After Launch

- [ ] Monitor error logs
- [ ] Check uptime
- [ ] Gather user feedback
- [ ] Plan updates/improvements

---

## Support

For deployment issues:
- Railway: https://help.railway.app
- Render: https://render.com/docs
- Expo: https://docs.expo.dev

Good luck! 🚀
