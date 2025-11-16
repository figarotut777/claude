/**
 * TimelineView Component
 * Main visual timeline showing table availability
 * Y-axis: Tables (grouped by type)
 * X-axis: Time (12:00 - 04:00)
 */

import React, { useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { theme } from '../../theme';
import {
  getMinutesSinceOpening,
  getTotalOperatingMinutes,
  getTimeLabels,
  formatTime,
} from '../../utils/businessDate';

const SCREEN_WIDTH = Dimensions.get('window').width;
const TABLE_LABEL_WIDTH = 80;
const MINUTE_WIDTH = 1.5; // pixels per minute
const TIMELINE_WIDTH = getTotalOperatingMinutes() * MINUTE_WIDTH; // 960 * 1.5 = 1440px
const ROW_HEIGHT = 60;
const TIME_HEADER_HEIGHT = 40;

export default function TimelineView({ data, onBookingPress, onEmptySlotPress }) {
  const scrollViewRef = useRef(null);

  if (!data || !data.tableTypes) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>Нет данных для отображения</Text>
      </View>
    );
  }

  const { tableTypes } = data;

  // Render time header
  const renderTimeHeader = () => {
    const timeLabels = getTimeLabels();

    return (
      <View style={styles.timeHeaderContainer}>
        <View style={[styles.tableLabel, { width: TABLE_LABEL_WIDTH }]} />
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          scrollEnabled={false}
          style={styles.timeHeaderScroll}
        >
          <View style={[styles.timeHeader, { width: TIMELINE_WIDTH }]}>
            {timeLabels.map((time) => (
              <View
                key={time.label}
                style={[
                  styles.timeLabel,
                  { left: time.minutes * MINUTE_WIDTH }
                ]}
              >
                <Text style={styles.timeLabelText}>{time.label}</Text>
              </View>
            ))}
          </View>
        </ScrollView>
      </View>
    );
  };

  // Render booking block
  const renderBooking = (booking, table) => {
    const start = getMinutesSinceOpening(new Date(booking.startDatetime));
    const end = getMinutesSinceOpening(new Date(booking.endDatetime));
    const duration = end - start;
    const width = duration * MINUTE_WIDTH;
    const left = start * MINUTE_WIDTH;

    return (
      <TouchableOpacity
        key={booking.id}
        style={[
          styles.bookingBlock,
          {
            left,
            width,
            backgroundColor:
              booking.status === 'CANCELLED'
                ? theme.colors.gray[300]
                : theme.colors.primary[500],
          },
        ]}
        onPress={() => onBookingPress && onBookingPress(booking)}
        activeOpacity={0.7}
      >
        <View style={styles.bookingContent}>
          <Text style={styles.bookingTime} numberOfLines={1}>
            {formatTime(new Date(booking.startDatetime))} -{' '}
            {formatTime(new Date(booking.endDatetime))}
          </Text>
          {booking.customerName && (
            <Text style={styles.bookingCustomer} numberOfLines={1}>
              {booking.customerName}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  // Render table row
  const renderTableRow = (table, tableType) => {
    return (
      <View key={table.id} style={styles.tableRow}>
        {/* Table label */}
        <View
          style={[
            styles.tableLabel,
            { width: TABLE_LABEL_WIDTH, backgroundColor: tableType.color + '20' },
          ]}
        >
          <Text style={styles.tableLabelText}>Стол #{table.number}</Text>
        </View>

        {/* Timeline area */}
        <ScrollView
          ref={scrollViewRef}
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.timelineScroll}
        >
          <TouchableOpacity
            style={[styles.timelineArea, { width: TIMELINE_WIDTH }]}
            onPress={(e) => {
              if (onEmptySlotPress) {
                const x = e.nativeEvent.locationX;
                const minutes = Math.round(x / MINUTE_WIDTH);
                onEmptySlotPress(table, minutes);
              }
            }}
            activeOpacity={1}
          >
            {/* Grid lines (hourly) */}
            {getTimeLabels().map((time) => (
              <View
                key={time.label}
                style={[
                  styles.gridLine,
                  { left: time.minutes * MINUTE_WIDTH }
                ]}
              />
            ))}

            {/* Bookings */}
            {table.bookings?.map((booking) => renderBooking(booking, table))}
          </TouchableOpacity>
        </ScrollView>
      </View>
    );
  };

  // Render table type section
  const renderTableTypeSection = (tableType) => {
    if (!tableType.tables || tableType.tables.length === 0) {
      return null;
    }

    return (
      <View key={tableType.id} style={styles.tableTypeSection}>
        {/* Type header */}
        <View
          style={[
            styles.tableTypeHeader,
            { backgroundColor: tableType.color + '15' },
          ]}
        >
          <Text style={[styles.tableTypeTitle, { color: tableType.color }]}>
            {tableType.displayName} ({tableType.tables.length})
          </Text>
        </View>

        {/* Table rows */}
        {tableType.tables.map((table) => renderTableRow(table, tableType))}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Time header */}
      {renderTimeHeader()}

      {/* Table sections */}
      <ScrollView
        style={styles.contentScroll}
        showsVerticalScrollIndicator={false}
      >
        {tableTypes.map((tableType) => renderTableTypeSection(tableType))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  emptyText: {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
  },

  // Time header
  timeHeaderContainer: {
    flexDirection: 'row',
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  timeHeaderScroll: {
    flex: 1,
  },
  timeHeader: {
    height: TIME_HEADER_HEIGHT,
    position: 'relative',
  },
  timeLabel: {
    position: 'absolute',
    top: 0,
    height: TIME_HEADER_HEIGHT,
    justifyContent: 'center',
    paddingHorizontal: theme.spacing.sm,
  },
  timeLabelText: {
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.text.secondary,
    fontWeight: theme.typography.fontWeight.medium,
  },

  // Content
  contentScroll: {
    flex: 1,
  },

  // Table type section
  tableTypeSection: {
    marginBottom: theme.spacing.md,
  },
  tableTypeHeader: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  tableTypeTitle: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.bold,
  },

  // Table row
  tableRow: {
    flexDirection: 'row',
    height: ROW_HEIGHT,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  tableLabel: {
    justifyContent: 'center',
    alignItems: 'center',
    borderRightWidth: 2,
    borderRightColor: theme.colors.border,
  },
  tableLabelText: {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
  },

  // Timeline area
  timelineScroll: {
    flex: 1,
  },
  timelineArea: {
    height: ROW_HEIGHT,
    position: 'relative',
    backgroundColor: theme.colors.gray[50],
  },
  gridLine: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    width: 1,
    backgroundColor: theme.colors.gray[200],
  },

  // Booking block
  bookingBlock: {
    position: 'absolute',
    top: 6,
    bottom: 6,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.xs,
    justifyContent: 'center',
    ...theme.shadows.sm,
  },
  bookingContent: {
    flex: 1,
  },
  bookingTime: {
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.inverse,
  },
  bookingCustomer: {
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.text.inverse,
    marginTop: 2,
    opacity: 0.9,
  },
});
