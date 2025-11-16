/**
 * Main Screen - Timeline View
 * Shows booking timeline for selected business date
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { format, addDays } from 'date-fns';
import { ru } from 'date-fns/locale';

import TimelineView from '../src/components/Timeline/TimelineView';
import { bookingService } from '../src/services/bookingService';
import { getBusinessDate, formatBusinessDate } from '../src/utils/businessDate';
import { theme } from '../src/theme';

export default function HomeScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  // Current business date
  const [businessDate, setBusinessDate] = useState(() => getBusinessDate());

  // Fetch timeline data
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['timeline', formatBusinessDate(businessDate)],
    queryFn: () => bookingService.getTimeline(formatBusinessDate(businessDate)),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Navigate to previous day
  const goToPreviousDay = () => {
    setBusinessDate((prev) => addDays(prev, -1));
  };

  // Navigate to next day
  const goToNextDay = () => {
    setBusinessDate((prev) => addDays(prev, 1));
  };

  // Navigate to today
  const goToToday = () => {
    setBusinessDate(getBusinessDate());
  };

  // Handle booking press
  const handleBookingPress = (booking) => {
    router.push(`/booking/${booking.id}`);
  };

  // Handle empty slot press - create new booking
  const handleEmptySlotPress = (table, minutes) => {
    Alert.alert(
      'Создать бронь?',
      `Стол #${table.number}`,
      [
        { text: 'Отмена', style: 'cancel' },
        {
          text: 'Создать',
          onPress: () => {
            router.push({
              pathname: '/booking/create',
              params: {
                tableId: table.id,
                startMinutes: minutes,
                businessDate: formatBusinessDate(businessDate),
              },
            });
          },
        },
      ]
    );
  };

  // Format date for display
  const formatDateDisplay = () => {
    const today = getBusinessDate();
    const isToday = formatBusinessDate(businessDate) === formatBusinessDate(today);

    if (isToday) {
      return 'Сегодня, ' + format(businessDate, 'd MMMM', { locale: ru });
    }

    return format(businessDate, 'd MMMM yyyy', { locale: ru });
  };

  return (
    <View style={styles.container}>
      {/* Date selector */}
      <View style={styles.dateSelector}>
        <TouchableOpacity
          style={styles.dateButton}
          onPress={goToPreviousDay}
        >
          <Text style={styles.dateButtonText}>←</Text>
        </TouchableOpacity>

        <View style={styles.dateDisplay}>
          <Text style={styles.dateText}>{formatDateDisplay()}</Text>
          <TouchableOpacity onPress={goToToday} style={styles.todayButton}>
            <Text style={styles.todayButtonText}>Сегодня</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={styles.dateButton}
          onPress={goToNextDay}
        >
          <Text style={styles.dateButtonText}>→</Text>
        </TouchableOpacity>
      </View>

      {/* Timeline */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary[500]} />
          <Text style={styles.loadingText}>Загрузка...</Text>
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>
            Ошибка загрузки данных
          </Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => refetch()}
          >
            <Text style={styles.retryButtonText}>Повторить</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TimelineView
          data={data}
          onBookingPress={handleBookingPress}
          onEmptySlotPress={handleEmptySlotPress}
        />
      )}

      {/* Floating action button */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => router.push('/booking/create')}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {/* Admin button */}
      <TouchableOpacity
        style={styles.adminButton}
        onPress={() => router.push('/admin/index')}
      >
        <Text style={styles.adminButtonText}>⚙️</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },

  // Date selector
  dateSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    ...theme.shadows.sm,
  },
  dateButton: {
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.gray[100],
  },
  dateButtonText: {
    fontSize: theme.typography.fontSize.xl,
    color: theme.colors.text.primary,
  },
  dateDisplay: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
  },
  dateText: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
  },
  todayButton: {
    marginTop: theme.spacing.xs,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 4,
  },
  todayButtonText: {
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.primary[600],
    fontWeight: theme.typography.fontWeight.medium,
  },

  // Loading
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: theme.spacing.md,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
  },

  // Error
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  errorText: {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.error,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  retryButton: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.primary[500],
    borderRadius: theme.borderRadius.md,
  },
  retryButtonText: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.inverse,
  },

  // Floating action button
  fab: {
    position: 'absolute',
    right: theme.spacing.lg,
    bottom: theme.spacing.lg,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: theme.colors.primary[500],
    justifyContent: 'center',
    alignItems: 'center',
    ...theme.shadows.lg,
  },
  fabText: {
    fontSize: 32,
    color: theme.colors.text.inverse,
    fontWeight: theme.typography.fontWeight.bold,
  },

  // Admin button
  adminButton: {
    position: 'absolute',
    left: theme.spacing.lg,
    bottom: theme.spacing.lg,
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: theme.colors.secondary[500],
    justifyContent: 'center',
    alignItems: 'center',
    ...theme.shadows.lg,
  },
  adminButtonText: {
    fontSize: 24,
  },
});
