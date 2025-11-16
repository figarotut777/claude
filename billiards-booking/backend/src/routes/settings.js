import express from 'express';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

/**
 * GET /api/settings
 * Get all settings
 */
router.get('/', async (req, res, next) => {
  try {
    const settings = await prisma.setting.findMany();

    // Convert to object format
    const settingsObj = settings.reduce((acc, setting) => {
      acc[setting.key] = JSON.parse(setting.value);
      return acc;
    }, {});

    res.json({
      success: true,
      data: settingsObj
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/settings/:key
 * Get a specific setting
 */
router.get('/:key', async (req, res, next) => {
  try {
    const { key } = req.params;

    const setting = await prisma.setting.findUnique({
      where: { key }
    });

    if (!setting) {
      return res.status(404).json({
        success: false,
        error: { message: 'Setting not found' }
      });
    }

    res.json({
      success: true,
      data: {
        key: setting.key,
        value: JSON.parse(setting.value)
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * PUT /api/settings/:key
 * Update or create a setting
 */
router.put('/:key', async (req, res, next) => {
  try {
    const { key } = req.params;
    const { value } = req.body;

    if (value === undefined) {
      return res.status(400).json({
        success: false,
        error: { message: 'value is required' }
      });
    }

    const setting = await prisma.setting.upsert({
      where: { key },
      update: {
        value: JSON.stringify(value)
      },
      create: {
        key,
        value: JSON.stringify(value)
      }
    });

    res.json({
      success: true,
      data: {
        key: setting.key,
        value: JSON.parse(setting.value)
      }
    });
  } catch (error) {
    next(error);
  }
});

export default router;
