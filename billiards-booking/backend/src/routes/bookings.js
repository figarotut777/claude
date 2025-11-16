import express from 'express';
import { PrismaClient } from '@prisma/client';
import {
  getBusinessDate,
  validateBookingTime,
  checkTimeOverlap,
  formatBusinessDate
} from '../utils/businessDate.js';

const router = express.Router();
const prisma = new PrismaClient();

/**
 * GET /api/bookings
 * Get bookings, optionally filtered by date and/or table
 */
router.get('/', async (req, res, next) => {
  try {
    const { businessDate, tableId, status } = req.query;

    const where = {
      ...(businessDate && {
        businessDate: new Date(businessDate)
      }),
      ...(tableId && { tableId: parseInt(tableId) }),
      ...(status && { status })
    };

    const bookings = await prisma.booking.findMany({
      where,
      include: {
        table: {
          include: {
            type: true
          }
        }
      },
      orderBy: [
        { startDatetime: 'asc' }
      ]
    });

    res.json({
      success: true,
      data: bookings
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/bookings/timeline
 * Get timeline view for a specific business date
 * Returns all tables grouped by type with their bookings
 */
router.get('/timeline', async (req, res, next) => {
  try {
    const { businessDate } = req.query;

    if (!businessDate) {
      return res.status(400).json({
        success: false,
        error: { message: 'businessDate query parameter is required' }
      });
    }

    const date = new Date(businessDate);

    // Get all active tables with their types
    const tableTypes = await prisma.tableType.findMany({
      orderBy: { sortOrder: 'asc' },
      include: {
        tables: {
          where: { isActive: true },
          orderBy: { number: 'asc' },
          include: {
            bookings: {
              where: {
                businessDate: date,
                status: 'ACTIVE'
              },
              orderBy: { startDatetime: 'asc' }
            }
          }
        }
      }
    });

    res.json({
      success: true,
      data: {
        businessDate: formatBusinessDate(date),
        tableTypes
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/bookings/:id
 * Get a single booking
 */
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    const booking = await prisma.booking.findUnique({
      where: { id: parseInt(id) },
      include: {
        table: {
          include: {
            type: true
          }
        }
      }
    });

    if (!booking) {
      return res.status(404).json({
        success: false,
        error: { message: 'Booking not found' }
      });
    }

    res.json({
      success: true,
      data: booking
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/bookings
 * Create a new booking
 */
router.post('/', async (req, res, next) => {
  try {
    const {
      tableId,
      startDatetime,
      endDatetime,
      customerName,
      customerPhone
    } = req.body;

    // Validation
    if (!tableId || !startDatetime || !endDatetime) {
      return res.status(400).json({
        success: false,
        error: { message: 'tableId, startDatetime, and endDatetime are required' }
      });
    }

    const start = new Date(startDatetime);
    const end = new Date(endDatetime);

    // Validate booking time
    const timeValidation = validateBookingTime(start, end);
    if (!timeValidation.valid) {
      return res.status(400).json({
        success: false,
        error: { message: timeValidation.error }
      });
    }

    // Get business date
    const businessDate = getBusinessDate(start);

    // Check for overlapping bookings on the same table
    const existingBookings = await prisma.booking.findMany({
      where: {
        tableId: parseInt(tableId),
        businessDate,
        status: 'ACTIVE'
      }
    });

    const newBooking = { startDatetime: start, endDatetime: end };
    const hasOverlap = existingBookings.some(existing =>
      checkTimeOverlap(existing, newBooking)
    );

    if (hasOverlap) {
      return res.status(409).json({
        success: false,
        error: { message: 'This time slot overlaps with an existing booking' }
      });
    }

    // Create booking
    const booking = await prisma.booking.create({
      data: {
        tableId: parseInt(tableId),
        businessDate,
        startDatetime: start,
        endDatetime: end,
        customerName,
        customerPhone,
        status: 'ACTIVE'
      },
      include: {
        table: {
          include: {
            type: true
          }
        }
      }
    });

    // Emit WebSocket event to all clients watching this business date
    const io = req.app.get('io');
    io.to(`date:${formatBusinessDate(businessDate)}`).emit('booking-created', booking);
    io.emit('booking-created', booking); // Also emit globally

    res.status(201).json({
      success: true,
      data: booking
    });
  } catch (error) {
    next(error);
  }
});

/**
 * PUT /api/bookings/:id
 * Update a booking
 */
router.put('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const {
      startDatetime,
      endDatetime,
      customerName,
      customerPhone,
      status
    } = req.body;

    // Get existing booking
    const existing = await prisma.booking.findUnique({
      where: { id: parseInt(id) }
    });

    if (!existing) {
      return res.status(404).json({
        success: false,
        error: { message: 'Booking not found' }
      });
    }

    // If updating time, validate
    if (startDatetime || endDatetime) {
      const start = startDatetime ? new Date(startDatetime) : existing.startDatetime;
      const end = endDatetime ? new Date(endDatetime) : existing.endDatetime;

      const timeValidation = validateBookingTime(start, end);
      if (!timeValidation.valid) {
        return res.status(400).json({
          success: false,
          error: { message: timeValidation.error }
        });
      }

      const businessDate = getBusinessDate(start);

      // Check for overlaps (excluding current booking)
      const existingBookings = await prisma.booking.findMany({
        where: {
          tableId: existing.tableId,
          businessDate,
          status: 'ACTIVE',
          id: { not: parseInt(id) }
        }
      });

      const updatedBooking = { startDatetime: start, endDatetime: end };
      const hasOverlap = existingBookings.some(other =>
        checkTimeOverlap(other, updatedBooking)
      );

      if (hasOverlap) {
        return res.status(409).json({
          success: false,
          error: { message: 'Updated time slot overlaps with an existing booking' }
        });
      }
    }

    // Update booking
    const booking = await prisma.booking.update({
      where: { id: parseInt(id) },
      data: {
        ...(startDatetime && { startDatetime: new Date(startDatetime) }),
        ...(endDatetime && { endDatetime: new Date(endDatetime) }),
        ...(startDatetime && { businessDate: getBusinessDate(new Date(startDatetime)) }),
        ...(customerName !== undefined && { customerName }),
        ...(customerPhone !== undefined && { customerPhone }),
        ...(status && { status })
      },
      include: {
        table: {
          include: {
            type: true
          }
        }
      }
    });

    // Emit WebSocket event
    const io = req.app.get('io');
    const bizDate = formatBusinessDate(booking.businessDate);
    io.to(`date:${bizDate}`).emit('booking-updated', booking);
    io.emit('booking-updated', booking);

    res.json({
      success: true,
      data: booking
    });
  } catch (error) {
    next(error);
  }
});

/**
 * DELETE /api/bookings/:id
 * Cancel a booking (soft delete)
 */
router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    const booking = await prisma.booking.update({
      where: { id: parseInt(id) },
      data: { status: 'CANCELLED' },
      include: {
        table: {
          include: {
            type: true
          }
        }
      }
    });

    // Emit WebSocket event
    const io = req.app.get('io');
    const bizDate = formatBusinessDate(booking.businessDate);
    io.to(`date:${bizDate}`).emit('booking-cancelled', booking);
    io.emit('booking-cancelled', booking);

    res.json({
      success: true,
      message: 'Booking cancelled successfully',
      data: booking
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/bookings/:id/complete
 * Mark a booking as completed
 */
router.post('/:id/complete', async (req, res, next) => {
  try {
    const { id } = req.params;

    const booking = await prisma.booking.update({
      where: { id: parseInt(id) },
      data: { status: 'COMPLETED' },
      include: {
        table: {
          include: {
            type: true
          }
        }
      }
    });

    res.json({
      success: true,
      data: booking
    });
  } catch (error) {
    next(error);
  }
});

export default router;
