import axios from 'axios'
import { SearchResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchByText = async (
  query: string,
  options?: {
    category?: string
    min_price?: number
    max_price?: number
  }
): Promise<SearchResponse> => {
  const response = await api.post('/api/search/text', {
    query,
    ...options,
  })
  return response.data
}

export const searchByImage = async (
  imageUrl?: string,
  imageBase64?: string
): Promise<SearchResponse> => {
  const response = await api.post('/api/search/image', {
    image_url: imageUrl,
    image_base64: imageBase64,
  })
  return response.data
}

export const searchByURL = async (url: string): Promise<SearchResponse> => {
  const response = await api.post('/api/search/url', {
    url,
  })
  return response.data
}

export default api
