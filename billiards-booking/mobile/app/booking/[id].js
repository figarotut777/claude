/**
 * Booking Details Screen
 * View and manage a specific booking
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

import { bookingService } from '../../src/services/bookingService';
import { theme } from '../../src/theme';

export default function BookingDetailsScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const queryClient = useQueryClient();

  // Fetch booking details
  const { data, isLoading, error } = useQuery({
    queryKey: ['booking', id],
    queryFn: () => bookingService.getBooking(id),
  });

  // Cancel booking mutation
  const cancelMutation = useMutation({
    mutationFn: () => bookingService.cancelBooking(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['booking', id]);
      queryClient.invalidateQueries(['timeline']);
      Alert.alert('Успешно', 'Бронь отменена', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    },
    onError: (error) => {
      Alert.alert('Ошибка', error?.error?.message || 'Не удалось отменить бронь');
    },
  });

  const handleCancel = () => {
    Alert.alert(
      'Отменить бронь?',
      'Это действие нельзя будет отменить',
      [
        { text: 'Нет', style: 'cancel' },
        {
          text: 'Да, отменить',
          style: 'destructive',
          onPress: () => cancelMutation.mutate(),
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary[500]} />
      </View>
    );
  }

  if (error || !data?.data) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Бронь не найдена</Text>
      </View>
    );
  }

  const booking = data.data;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Status badge */}
        <View
          style={[
            styles.statusBadge,
            {
              backgroundColor:
                booking.status === 'ACTIVE'
                  ? theme.colors.success + '20'
                  : booking.status === 'CANCELLED'
                  ? theme.colors.error + '20'
                  : theme.colors.gray[200],
            },
          ]}
        >
          <Text
            style={[
              styles.statusText,
              {
                color:
                  booking.status === 'ACTIVE'
                    ? theme.colors.success
                    : booking.status === 'CANCELLED'
                    ? theme.colors.error
                    : theme.colors.gray[600],
              },
            ]}
          >
            {booking.status === 'ACTIVE'
              ? 'Активна'
              : booking.status === 'CANCELLED'
              ? 'Отменена'
              : 'Завершена'}
          </Text>
        </View>

        {/* Booking info */}
        <View style={styles.infoCard}>
          <InfoRow
            label="Тип стола"
            value={booking.table.type.displayName}
            color={booking.table.type.color}
          />
          <InfoRow label="Стол №" value={`#${booking.table.number}`} />
          <InfoRow
            label="Дата"
            value={format(new Date(booking.businessDate), 'dd MMMM yyyy', {
              locale: ru,
            })}
          />
          <InfoRow
            label="Время начала"
            value={format(new Date(booking.startDatetime), 'HH:mm')}
          />
          <InfoRow
            label="Время окончания"
            value={format(new Date(booking.endDatetime), 'HH:mm')}
          />
        </View>

        {/* Customer info */}
        {(booking.customerName || booking.customerPhone) && (
          <View style={styles.infoCard}>
            <Text style={styles.cardTitle}>Информация о клиенте</Text>
            {booking.customerName && (
              <InfoRow label="Имя" value={booking.customerName} />
            )}
            {booking.customerPhone && (
              <InfoRow label="Телефон" value={booking.customerPhone} />
            )}
          </View>
        )}

        {/* Actions */}
        {booking.status === 'ACTIVE' && (
          <TouchableOpacity
            style={[
              styles.cancelButton,
              cancelMutation.isPending && styles.cancelButtonDisabled,
            ]}
            onPress={handleCancel}
            disabled={cancelMutation.isPending}
          >
            {cancelMutation.isPending ? (
              <ActivityIndicator color={theme.colors.text.inverse} />
            ) : (
              <Text style={styles.cancelButtonText}>Отменить бронь</Text>
            )}
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}

function InfoRow({ label, value, color }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={[styles.infoValue, color && { color }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: theme.spacing.lg,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  errorText: {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.error,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.full,
    marginBottom: theme.spacing.lg,
  },
  statusText: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  infoCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    ...theme.shadows.sm,
  },
  cardTitle: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.gray[100],
  },
  infoLabel: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
  },
  infoValue: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
  },
  cancelButton: {
    marginTop: theme.spacing.xl,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.error,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    ...theme.shadows.md,
  },
  cancelButtonDisabled: {
    opacity: 0.6,
  },
  cancelButtonText: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.inverse,
  },
});
