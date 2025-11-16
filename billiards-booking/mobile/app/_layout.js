import { Stack } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

const queryClient = new QueryClient();

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryClientProvider client={queryClient}>
        <Stack
          screenOptions={{
            headerStyle: {
              backgroundColor: '#10B981',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen
            name="index"
            options={{
              title: 'Бронирование столов',
            }}
          />
          <Stack.Screen
            name="booking/create"
            options={{
              title: 'Новая бронь',
              presentation: 'modal',
            }}
          />
          <Stack.Screen
            name="booking/[id]"
            options={{
              title: 'Детали брони',
            }}
          />
          <Stack.Screen
            name="admin/index"
            options={{
              title: 'Управление столами',
            }}
          />
        </Stack>
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}
