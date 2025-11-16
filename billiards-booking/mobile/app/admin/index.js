/**
 * Admin Panel - Table Management
 * Manage table counts for each type
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { tableService } from '../../src/services/tableService';
import { theme } from '../../src/theme';

export default function AdminScreen() {
  const queryClient = useQueryClient();

  // Fetch table types with counts
  const { data: tableTypesData, isLoading } = useQuery({
    queryKey: ['tableTypes'],
    queryFn: tableService.getTableTypes,
  });

  // Fetch all tables
  const { data: tablesData } = useQuery({
    queryKey: ['tables'],
    queryFn: () => tableService.getTables(),
  });

  // Update table count mutation
  const updateCountMutation = useMutation({
    mutationFn: ({ typeId, count }) =>
      tableService.bulkUpdateTableCount(typeId, count),
    onSuccess: () => {
      queryClient.invalidateQueries(['tableTypes']);
      queryClient.invalidateQueries(['tables']);
      queryClient.invalidateQueries(['timeline']);
      Alert.alert('Успешно', 'Количество столов обновлено');
    },
    onError: (error) => {
      Alert.alert(
        'Ошибка',
        error?.error?.message || 'Не удалось обновить'
      );
    },
  });

  const handleUpdateCount = (typeId, currentCount, delta) => {
    const newCount = Math.max(0, currentCount + delta);

    if (newCount === currentCount) return;

    if (delta < 0) {
      Alert.alert(
        'Уменьшить количество столов?',
        `Это уменьшит количество столов с ${currentCount} до ${newCount}`,
        [
          { text: 'Отмена', style: 'cancel' },
          {
            text: 'Уменьшить',
            style: 'destructive',
            onPress: () => updateCountMutation.mutate({ typeId, count: newCount }),
          },
        ]
      );
    } else {
      updateCountMutation.mutate({ typeId, count: newCount });
    }
  };

  const tableTypes = tableTypesData?.data || [];
  const tables = tablesData?.data || [];

  // Count active tables by type
  const getActiveTableCount = (typeId) => {
    return tables.filter((t) => t.typeId === typeId && t.isActive).length;
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary[500]} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Управление столами</Text>
        <Text style={styles.subtitle}>
          Настройте количество столов каждого типа
        </Text>

        {tableTypes.map((type) => {
          const count = getActiveTableCount(type.id);

          return (
            <View
              key={type.id}
              style={[
                styles.typeCard,
                { borderLeftColor: type.color, borderLeftWidth: 4 },
              ]}
            >
              <View style={styles.typeHeader}>
                <Text style={styles.typeName}>{type.displayName}</Text>
                <View
                  style={[
                    styles.countBadge,
                    { backgroundColor: type.color + '20' },
                  ]}
                >
                  <Text style={[styles.countText, { color: type.color }]}>
                    {count} {count === 1 ? 'стол' : 'столов'}
                  </Text>
                </View>
              </View>

              <View style={styles.controls}>
                <TouchableOpacity
                  style={[
                    styles.controlButton,
                    styles.decreaseButton,
                    count === 0 && styles.controlButtonDisabled,
                  ]}
                  onPress={() => handleUpdateCount(type.id, count, -1)}
                  disabled={count === 0 || updateCountMutation.isPending}
                >
                  <Text style={styles.controlButtonText}>-</Text>
                </TouchableOpacity>

                <View style={styles.countDisplay}>
                  <Text style={styles.countDisplayText}>{count}</Text>
                </View>

                <TouchableOpacity
                  style={[styles.controlButton, styles.increaseButton]}
                  onPress={() => handleUpdateCount(type.id, count, 1)}
                  disabled={updateCountMutation.isPending}
                >
                  <Text style={styles.controlButtonText}>+</Text>
                </TouchableOpacity>
              </View>

              {/* Quick presets */}
              <View style={styles.presets}>
                <Text style={styles.presetsLabel}>Быстрый выбор:</Text>
                {[5, 10, 15, 20].map((preset) => (
                  <TouchableOpacity
                    key={preset}
                    style={[
                      styles.presetButton,
                      count === preset && styles.presetButtonActive,
                    ]}
                    onPress={() =>
                      updateCountMutation.mutate({ typeId: type.id, count: preset })
                    }
                    disabled={updateCountMutation.isPending}
                  >
                    <Text
                      style={[
                        styles.presetButtonText,
                        count === preset && styles.presetButtonTextActive,
                      ]}
                    >
                      {preset}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          );
        })}

        {/* Operating hours info */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>График работы</Text>
          <Text style={styles.infoText}>Открытие: 12:00</Text>
          <Text style={styles.infoText}>Закрытие: 04:00 (следующего дня)</Text>
        </View>
      </View>
    </ScrollView>
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
  title: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xl,
  },
  typeCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    ...theme.shadows.md,
  },
  typeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  typeName: {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
  },
  countBadge: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
  },
  countText: {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  controls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.md,
  },
  controlButton: {
    width: 60,
    height: 60,
    borderRadius: theme.borderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
    ...theme.shadows.sm,
  },
  increaseButton: {
    backgroundColor: theme.colors.primary[500],
  },
  decreaseButton: {
    backgroundColor: theme.colors.error,
  },
  controlButtonDisabled: {
    opacity: 0.3,
  },
  controlButtonText: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.inverse,
  },
  countDisplay: {
    marginHorizontal: theme.spacing.xl,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.gray[100],
    borderRadius: theme.borderRadius.md,
    minWidth: 80,
    alignItems: 'center',
  },
  countDisplayText: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
  },
  presets: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  presetsLabel: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
    marginRight: theme.spacing.sm,
  },
  presetButton: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.gray[100],
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  presetButtonActive: {
    backgroundColor: theme.colors.primary[100],
    borderColor: theme.colors.primary[500],
  },
  presetButtonText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.primary,
  },
  presetButtonTextActive: {
    color: theme.colors.primary[700],
    fontWeight: theme.typography.fontWeight.semibold,
  },
  infoCard: {
    marginTop: theme.spacing.xl,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.primary[50],
    borderRadius: theme.borderRadius.lg,
    borderWidth: 1,
    borderColor: theme.colors.primary[200],
  },
  infoTitle: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.primary[900],
    marginBottom: theme.spacing.sm,
  },
  infoText: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.primary[800],
    marginBottom: theme.spacing.xs,
  },
});
