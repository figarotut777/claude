import express from 'express';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

/**
 * GET /api/table-types
 * Get all table types
 */
router.get('/', async (req, res, next) => {
  try {
    const tableTypes = await prisma.tableType.findMany({
      orderBy: {
        sortOrder: 'asc'
      },
      include: {
        _count: {
          select: { tables: true }
        }
      }
    });

    res.json({
      success: true,
      data: tableTypes
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/table-types/:id
 * Get a single table type
 */
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    const tableType = await prisma.tableType.findUnique({
      where: { id: parseInt(id) },
      include: {
        tables: {
          where: { isActive: true },
          orderBy: { number: 'asc' }
        }
      }
    });

    if (!tableType) {
      return res.status(404).json({
        success: false,
        error: { message: 'Table type not found' }
      });
    }

    res.json({
      success: true,
      data: tableType
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/table-types
 * Create a new table type
 */
router.post('/', async (req, res, next) => {
  try {
    const { name, displayName, sortOrder, color } = req.body;

    if (!name || !displayName) {
      return res.status(400).json({
        success: false,
        error: { message: 'Name and displayName are required' }
      });
    }

    const tableType = await prisma.tableType.create({
      data: {
        name,
        displayName,
        sortOrder: sortOrder || 0,
        color: color || '#10B981'
      }
    });

    res.status(201).json({
      success: true,
      data: tableType
    });
  } catch (error) {
    next(error);
  }
});

/**
 * PUT /api/table-types/:id
 * Update a table type
 */
router.put('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { displayName, sortOrder, color } = req.body;

    const tableType = await prisma.tableType.update({
      where: { id: parseInt(id) },
      data: {
        ...(displayName && { displayName }),
        ...(sortOrder !== undefined && { sortOrder }),
        ...(color && { color })
      }
    });

    res.json({
      success: true,
      data: tableType
    });
  } catch (error) {
    next(error);
  }
});

export default router;
