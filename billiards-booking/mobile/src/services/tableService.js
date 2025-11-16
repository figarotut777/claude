import api from '../config/api';

export const tableService = {
  // Get all table types
  getTableTypes: async () => {
    const response = await api.get('/table-types');
    return response.data;
  },

  // Get all tables
  getTables: async (typeId = null) => {
    const response = await api.get('/tables', {
      params: typeId ? { typeId } : {}
    });
    return response.data;
  },

  // Create a new table
  createTable: async (tableData) => {
    const response = await api.post('/tables', tableData);
    return response.data;
  },

  // Update a table
  updateTable: async (id, updates) => {
    const response = await api.put(`/tables/${id}`, updates);
    return response.data;
  },

  // Delete a table
  deleteTable: async (id, hard = false) => {
    const response = await api.delete(`/tables/${id}`, {
      params: { hard }
    });
    return response.data;
  },

  // Bulk update table count for a type
  bulkUpdateTableCount: async (typeId, count) => {
    const response = await api.post('/tables/bulk-update-count', {
      typeId,
      count
    });
    return response.data;
  }
};

export default tableService;
