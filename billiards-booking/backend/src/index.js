import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server } from 'socket.io';

// Routes
import tableTypesRouter from './routes/tableTypes.js';
import tablesRouter from './routes/tables.js';
import bookingsRouter from './routes/bookings.js';
import settingsRouter from './routes/settings.js';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*', // In production, specify exact origins
    methods: ['GET', 'POST']
  }
});

const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Make io accessible to routes
app.set('io', io);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'billiards-booking-api'
  });
});

// API Routes
app.use('/api/table-types', tableTypesRouter);
app.use('/api/tables', tablesRouter);
app.use('/api/bookings', bookingsRouter);
app.use('/api/settings', settingsRouter);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);

  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal server error',
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: {
      message: 'Route not found'
    }
  });
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });

  // Join a specific business date room for live updates
  socket.on('join-date', (businessDate) => {
    socket.join(`date:${businessDate}`);
    console.log(`Client ${socket.id} joined room: date:${businessDate}`);
  });

  socket.on('leave-date', (businessDate) => {
    socket.leave(`date:${businessDate}`);
    console.log(`Client ${socket.id} left room: date:${businessDate}`);
  });
});

// Start server
httpServer.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎱 Billiards Booking API Server                        ║
║                                                           ║
║   Port:        ${PORT}                                       ║
║   Environment: ${process.env.NODE_ENV || 'development'}                                ║
║   WebSocket:   ${process.env.ENABLE_WEBSOCKET === 'true' ? 'Enabled' : 'Disabled'}                                 ║
║                                                           ║
║   Ready to accept connections!                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

export { io };
