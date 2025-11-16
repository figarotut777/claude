import api from '../config/api';

export const bookingService = {
  // Get timeline for a specific business date
  getTimeline: async (businessDate) => {
    const response = await api.get('/bookings/timeline', {
      params: { businessDate }
    });
    return response.data;
  },

  // Get all bookings (with optional filters)
  getBookings: async (filters = {}) => {
    const response = await api.get('/bookings', { params: filters });
    return response.data;
  },

  // Get a single booking
  getBooking: async (id) => {
    const response = await api.get(`/bookings/${id}`);
    return response.data;
  },

  // Create a new booking
  createBooking: async (bookingData) => {
    const response = await api.post('/bookings', bookingData);
    return response.data;
  },

  // Update a booking
  updateBooking: async (id, updates) => {
    const response = await api.put(`/bookings/${id}`, updates);
    return response.data;
  },

  // Cancel a booking
  cancelBooking: async (id) => {
    const response = await api.delete(`/bookings/${id}`);
    return response.data;
  },

  // Complete a booking
  completeBooking: async (id) => {
    const response = await api.post(`/bookings/${id}/complete`);
    return response.data;
  }
};

export default bookingService;
