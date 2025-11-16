import express from 'express';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

/**
 * GET /api/tables
 * Get all tables, optionally filtered by type
 */
router.get('/', async (req, res, next) => {
  try {
    const { typeId, includeInactive } = req.query;

    const where = {
      ...(typeId && { typeId: parseInt(typeId) }),
      ...(includeInactive !== 'true' && { isActive: true })
    };

    const tables = await prisma.table.findMany({
      where,
      include: {
        type: true
      },
      orderBy: [
        { type: { sortOrder: 'asc' } },
        { number: 'asc' }
      ]
    });

    res.json({
      success: true,
      data: tables
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/tables/:id
 * Get a single table
 */
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    const table = await prisma.table.findUnique({
      where: { id: parseInt(id) },
      include: {
        type: true
      }
    });

    if (!table) {
      return res.status(404).json({
        success: false,
        error: { message: 'Table not found' }
      });
    }

    res.json({
      success: true,
      data: table
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/tables
 * Create a new table
 */
router.post('/', async (req, res, next) => {
  try {
    const { typeId, number } = req.body;

    if (!typeId || !number) {
      return res.status(400).json({
        success: false,
        error: { message: 'typeId and number are required' }
      });
    }

    const table = await prisma.table.create({
      data: {
        typeId: parseInt(typeId),
        number: parseInt(number)
      },
      include: {
        type: true
      }
    });

    // Emit WebSocket event
    const io = req.app.get('io');
    io.emit('table-created', table);

    res.status(201).json({
      success: true,
      data: table
    });
  } catch (error) {
    next(error);
  }
});

/**
 * PUT /api/tables/:id
 * Update a table
 */
router.put('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { number, isActive } = req.body;

    const table = await prisma.table.update({
      where: { id: parseInt(id) },
      data: {
        ...(number !== undefined && { number: parseInt(number) }),
        ...(isActive !== undefined && { isActive })
      },
      include: {
        type: true
      }
    });

    // Emit WebSocket event
    const io = req.app.get('io');
    io.emit('table-updated', table);

    res.json({
      success: true,
      data: table
    });
  } catch (error) {
    next(error);
  }
});

/**
 * DELETE /api/tables/:id
 * Delete a table (soft delete by setting isActive = false)
 */
router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { hard } = req.query;

    if (hard === 'true') {
      // Hard delete - check if there are any bookings
      const bookingsCount = await prisma.booking.count({
        where: { tableId: parseInt(id) }
      });

      if (bookingsCount > 0) {
        return res.status(400).json({
          success: false,
          error: { message: 'Cannot delete table with existing bookings' }
        });
      }

      await prisma.table.delete({
        where: { id: parseInt(id) }
      });
    } else {
      // Soft delete
      await prisma.table.update({
        where: { id: parseInt(id) },
        data: { isActive: false }
      });
    }

    // Emit WebSocket event
    const io = req.app.get('io');
    io.emit('table-deleted', { id: parseInt(id) });

    res.json({
      success: true,
      message: 'Table deleted successfully'
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/tables/bulk-update-count
 * Bulk update table count for a specific type
 * Creates or deactivates tables to match the desired count
 */
router.post('/bulk-update-count', async (req, res, next) => {
  try {
    const { typeId, count } = req.body;

    if (!typeId || count === undefined) {
      return res.status(400).json({
        success: false,
        error: { message: 'typeId and count are required' }
      });
    }

    const targetCount = parseInt(count);
    const type = await prisma.tableType.findUnique({
      where: { id: parseInt(typeId) }
    });

    if (!type) {
      return res.status(404).json({
        success: false,
        error: { message: 'Table type not found' }
      });
    }

    // Get current active tables
    const currentTables = await prisma.table.findMany({
      where: {
        typeId: parseInt(typeId),
        isActive: true
      },
      orderBy: { number: 'asc' }
    });

    const currentCount = currentTables.length;

    if (targetCount > currentCount) {
      // Need to add tables
      const tablesToAdd = targetCount - currentCount;
      const newTables = [];

      for (let i = 0; i < tablesToAdd; i++) {
        const number = currentCount + i + 1;
        const table = await prisma.table.create({
          data: {
            typeId: parseInt(typeId),
            number
          }
        });
        newTables.push(table);
      }

      res.json({
        success: true,
        message: `Added ${tablesToAdd} table(s)`,
        data: newTables
      });
    } else if (targetCount < currentCount) {
      // Need to remove tables (soft delete from the end)
      const tablesToRemove = currentCount - targetCount;
      const tablesToDeactivate = currentTables.slice(-tablesToRemove);

      await prisma.table.updateMany({
        where: {
          id: { in: tablesToDeactivate.map(t => t.id) }
        },
        data: { isActive: false }
      });

      res.json({
        success: true,
        message: `Removed ${tablesToRemove} table(s)`,
        data: tablesToDeactivate
      });
    } else {
      res.json({
        success: true,
        message: 'Table count unchanged',
        data: []
      });
    }

    // Emit WebSocket event
    const io = req.app.get('io');
    io.emit('tables-bulk-updated', { typeId: parseInt(typeId), count: targetCount });
  } catch (error) {
    next(error);
  }
});

export default router;
