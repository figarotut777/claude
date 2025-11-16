import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create table types
  console.log('Creating table types...');

  const russianType = await prisma.tableType.upsert({
    where: { name: 'russian' },
    update: {},
    create: {
      name: 'russian',
      displayName: 'Русский бильярд',
      sortOrder: 1,
      color: '#8B5CF6' // Purple
    }
  });

  const americanType = await prisma.tableType.upsert({
    where: { name: 'american_pool' },
    update: {},
    create: {
      name: 'american_pool',
      displayName: 'Американский пул',
      sortOrder: 2,
      color: '#F59E0B' // Amber
    }
  });

  console.log('✓ Table types created');

  // Create tables
  console.log('Creating tables...');

  // 5 Russian billiards tables
  for (let i = 1; i <= 5; i++) {
    await prisma.table.upsert({
      where: {
        typeId_number: {
          typeId: russianType.id,
          number: i
        }
      },
      update: {},
      create: {
        typeId: russianType.id,
        number: i,
        isActive: true
      }
    });
  }

  // 10 American pool tables
  for (let i = 1; i <= 10; i++) {
    await prisma.table.upsert({
      where: {
        typeId_number: {
          typeId: americanType.id,
          number: i
        }
      },
      update: {},
      create: {
        typeId: americanType.id,
        number: i,
        isActive: true
      }
    });
  }

  console.log('✓ Tables created');

  // Create default settings
  console.log('Creating default settings...');

  await prisma.setting.upsert({
    where: { key: 'operating_hours' },
    update: {},
    create: {
      key: 'operating_hours',
      value: JSON.stringify({
        opening: '12:00',
        closing: '04:00'
      })
    }
  });

  await prisma.setting.upsert({
    where: { key: 'booking_rules' },
    update: {},
    create: {
      key: 'booking_rules',
      value: JSON.stringify({
        minDurationMinutes: 30,
        maxDurationMinutes: 480,
        allowSameDayBooking: true,
        advanceBookingDays: 30
      })
    }
  });

  console.log('✓ Settings created');

  // Create sample bookings for today
  console.log('Creating sample bookings...');

  const today = new Date();
  today.setHours(12, 0, 0, 0); // Start at 12:00 PM

  const russianTable1 = await prisma.table.findFirst({
    where: {
      typeId: russianType.id,
      number: 1
    }
  });

  if (russianTable1) {
    const startTime = new Date(today);
    startTime.setHours(14, 0, 0, 0); // 2:00 PM

    const endTime = new Date(today);
    endTime.setHours(16, 0, 0, 0); // 4:00 PM

    await prisma.booking.create({
      data: {
        tableId: russianTable1.id,
        businessDate: new Date(today),
        startDatetime: startTime,
        endDatetime: endTime,
        customerName: 'Иван Петров',
        customerPhone: '+7 (999) 123-45-67',
        status: 'ACTIVE'
      }
    });
  }

  const americanTable1 = await prisma.table.findFirst({
    where: {
      typeId: americanType.id,
      number: 1
    }
  });

  if (americanTable1) {
    const startTime = new Date(today);
    startTime.setHours(18, 30, 0, 0); // 6:30 PM

    const endTime = new Date(today);
    endTime.setHours(20, 0, 0, 0); // 8:00 PM

    await prisma.booking.create({
      data: {
        tableId: americanTable1.id,
        businessDate: new Date(today),
        startDatetime: startTime,
        endDatetime: endTime,
        customerName: 'Алексей Сидоров',
        customerPhone: '+7 (999) 987-65-43',
        status: 'ACTIVE'
      }
    });
  }

  console.log('✓ Sample bookings created');

  console.log('\n✅ Database seeded successfully!');
  console.log(`
📊 Summary:
   - Table Types: 2 (Russian, American Pool)
   - Tables: 15 (5 Russian + 10 American)
   - Sample Bookings: 2
  `);
}

main()
  .catch((e) => {
    console.error('❌ Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
