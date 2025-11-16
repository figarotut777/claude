export interface Product {
  name: string
  description?: string
  image_url?: string
  marketplace: string
  price: number
  currency: string
  url: string
  rating?: number
  reviews_count?: number
  in_stock: boolean
  relevance_score?: number
}

export interface SearchResponse {
  query: string
  results: Product[]
  total_results: number
  search_type: string
  source_product?: Product
}

export type SearchType = 'text' | 'image' | 'url'
