/**
 * Create Booking Screen
 * Form to create a new booking
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';

import { bookingService } from '../../src/services/bookingService';
import { tableService } from '../../src/services/tableService';
import {
  getBusinessDate,
  formatBusinessDate,
  getOpeningTime,
  minutesToDatetime,
} from '../../src/utils/businessDate';
import { theme } from '../../src/theme';

export default function CreateBookingScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const queryClient = useQueryClient();

  // Form state
  const [selectedTypeId, setSelectedTypeId] = useState(null);
  const [selectedTableId, setSelectedTableId] = useState(params.tableId || null);
  const [businessDate, setBusinessDate] = useState(
    params.businessDate ? new Date(params.businessDate) : getBusinessDate()
  );
  const [startTime, setStartTime] = useState('14:00');
  const [endTime, setEndTime] = useState('16:00');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');

  // Fetch table types and tables
  const { data: tableTypesData } = useQuery({
    queryKey: ['tableTypes'],
    queryFn: tableService.getTableTypes,
  });

  const { data: tablesData } = useQuery({
    queryKey: ['tables', selectedTypeId],
    queryFn: () => tableService.getTables(selectedTypeId),
    enabled: !!selectedTypeId,
  });

  // Create booking mutation
  const createMutation = useMutation({
    mutationFn: bookingService.createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries(['timeline']);
      Alert.alert('Успешно', 'Бронь создана', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    },
    onError: (error) => {
      Alert.alert(
        'Ошибка',
        error?.error?.message || 'Не удалось создать бронь'
      );
    },
  });

  // Parse time string to datetime
  const parseTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const dt = getOpeningTime(businessDate);
    dt.setHours(hours, minutes, 0, 0);

    // If hours are 00-03 (next day), add 1 day
    if (hours >= 0 && hours < 4) {
      dt.setDate(dt.getDate() + 1);
    }

    return dt;
  };

  // Handle submit
  const handleSubmit = () => {
    if (!selectedTableId) {
      Alert.alert('Ошибка', 'Выберите стол');
      return;
    }

    if (!startTime || !endTime) {
      Alert.alert('Ошибка', 'Укажите время начала и окончания');
      return;
    }

    const startDatetime = parseTime(startTime);
    const endDatetime = parseTime(endTime);

    createMutation.mutate({
      tableId: parseInt(selectedTableId),
      startDatetime: startDatetime.toISOString(),
      endDatetime: endDatetime.toISOString(),
      customerName: customerName || null,
      customerPhone: customerPhone || null,
    });
  };

  const tableTypes = tableTypesData?.data || [];
  const tables = tablesData?.data || [];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Date */}
        <View style={styles.section}>
          <Text style={styles.label}>Дата</Text>
          <View style={styles.dateDisplay}>
            <Text style={styles.dateText}>
              {format(businessDate, 'dd.MM.yyyy')}
            </Text>
          </View>
        </View>

        {/* Table Type */}
        <View style={styles.section}>
          <Text style={styles.label}>Тип стола</Text>
          <View style={styles.optionsContainer}>
            {tableTypes.map((type) => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.optionButton,
                  selectedTypeId === type.id && styles.optionButtonSelected,
                  { borderColor: type.color },
                ]}
                onPress={() => {
                  setSelectedTypeId(type.id);
                  setSelectedTableId(null);
                }}
              >
                <Text
                  style={[
                    styles.optionButtonText,
                    selectedTypeId === type.id && styles.optionButtonTextSelected,
                  ]}
                >
                  {type.displayName}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Table */}
        {selectedTypeId && (
          <View style={styles.section}>
            <Text style={styles.label}>Стол №</Text>
            <View style={styles.optionsContainer}>
              {tables
                .filter((t) => t.typeId === selectedTypeId)
                .map((table) => (
                  <TouchableOpacity
                    key={table.id}
                    style={[
                      styles.tableButton,
                      selectedTableId == table.id && styles.tableButtonSelected,
                    ]}
                    onPress={() => setSelectedTableId(table.id)}
                  >
                    <Text
                      style={[
                        styles.tableButtonText,
                        selectedTableId == table.id &&
                          styles.tableButtonTextSelected,
                      ]}
                    >
                      {table.number}
                    </Text>
                  </TouchableOpacity>
                ))}
            </View>
          </View>
        )}

        {/* Time */}
        <View style={styles.section}>
          <Text style={styles.label}>Время начала</Text>
          <TextInput
            style={styles.input}
            value={startTime}
            onChangeText={setStartTime}
            placeholder="14:00"
            keyboardType="numbers-and-punctuation"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Время окончания</Text>
          <TextInput
            style={styles.input}
            value={endTime}
            onChangeText={setEndTime}
            placeholder="16:00"
            keyboardType="numbers-and-punctuation"
          />
        </View>

        {/* Customer info */}
        <View style={styles.section}>
          <Text style={styles.label}>Имя клиента (опционально)</Text>
          <TextInput
            style={styles.input}
            value={customerName}
            onChangeText={setCustomerName}
            placeholder="Иван Петров"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Телефон (опционально)</Text>
          <TextInput
            style={styles.input}
            value={customerPhone}
            onChangeText={setCustomerPhone}
            placeholder="+7 (999) 123-45-67"
            keyboardType="phone-pad"
          />
        </View>

        {/* Submit button */}
        <TouchableOpacity
          style={[
            styles.submitButton,
            createMutation.isPending && styles.submitButtonDisabled,
          ]}
          onPress={handleSubmit}
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? (
            <ActivityIndicator color={theme.colors.text.inverse} />
          ) : (
            <Text style={styles.submitButtonText}>Забронировать</Text>
          )}
        </TouchableOpacity>
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
  section: {
    marginBottom: theme.spacing.lg,
  },
  label: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  dateDisplay: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  dateText: {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.primary,
  },
  input: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
  },
  optionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  optionButton: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    borderWidth: 2,
    borderColor: theme.colors.border,
  },
  optionButtonSelected: {
    backgroundColor: theme.colors.primary[50],
  },
  optionButtonText: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
  },
  optionButtonTextSelected: {
    color: theme.colors.primary[700],
    fontWeight: theme.typography.fontWeight.semibold,
  },
  tableButton: {
    width: 60,
    height: 60,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    borderWidth: 2,
    borderColor: theme.colors.border,
  },
  tableButtonSelected: {
    backgroundColor: theme.colors.primary[500],
    borderColor: theme.colors.primary[600],
  },
  tableButtonText: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
  },
  tableButtonTextSelected: {
    color: theme.colors.text.inverse,
  },
  submitButton: {
    marginTop: theme.spacing.xl,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.primary[500],
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    ...theme.shadows.md,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.inverse,
  },
});
