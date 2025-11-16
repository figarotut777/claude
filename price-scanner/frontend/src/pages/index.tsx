import { useState } from 'react'
import Head from 'next/head'
import SearchBox from '@/components/SearchBox'
import ProductGrid from '@/components/ProductGrid'
import { Product } from '@/utils/types'

export default function Home() {
  const [searchResults, setSearchResults] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = async (results: Product[], query: string) => {
    setSearchResults(results)
    setSearchQuery(query)
  }

  return (
    <>
      <Head>
        <title>Price-Scanner - Compare Prices Across Marketplaces</title>
        <meta name="description" content="Find the best prices across multiple marketplaces" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <h1 className="text-3xl font-bold text-gray-900">
                Price-Scanner
              </h1>
              <nav className="flex space-x-4">
                <a href="#" className="text-gray-600 hover:text-gray-900">
                  Home
                </a>
                <a href="#" className="text-gray-600 hover:text-gray-900">
                  History
                </a>
                <a href="#" className="text-gray-600 hover:text-gray-900">
                  About
                </a>
              </nav>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
              Find the Best Prices
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Search by image, text, or URL across multiple marketplaces
            </p>
          </div>

          {/* Search Box */}
          <SearchBox onSearch={handleSearch} setIsLoading={setIsLoading} />

          {/* Results */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4 text-gray-600">Searching marketplaces...</p>
            </div>
          )}

          {!isLoading && searchResults.length > 0 && (
            <div className="mt-12">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  Results for "{searchQuery}"
                </h3>
                <p className="text-gray-600">
                  Found {searchResults.length} products
                </p>
              </div>
              <ProductGrid products={searchResults} />
            </div>
          )}

          {!isLoading && searchResults.length === 0 && searchQuery && (
            <div className="text-center py-12">
              <p className="text-gray-600">No results found. Try a different search.</p>
            </div>
          )}
        </section>

        {/* Features */}
        {searchResults.length === 0 && !searchQuery && (
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6 bg-white rounded-lg shadow-sm">
                <div className="text-4xl mb-4">🖼️</div>
                <h3 className="text-xl font-semibold mb-2">Search by Image</h3>
                <p className="text-gray-600">
                  Upload a photo and find similar products instantly
                </p>
              </div>
              <div className="text-center p-6 bg-white rounded-lg shadow-sm">
                <div className="text-4xl mb-4">📝</div>
                <h3 className="text-xl font-semibold mb-2">Search by Text</h3>
                <p className="text-gray-600">
                  Type what you're looking for with smart fuzzy matching
                </p>
              </div>
              <div className="text-center p-6 bg-white rounded-lg shadow-sm">
                <div className="text-4xl mb-4">🔗</div>
                <h3 className="text-xl font-semibold mb-2">Search by URL</h3>
                <p className="text-gray-600">
                  Paste a product link and find it cheaper elsewhere
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="bg-gray-50 border-t mt-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p className="text-center text-gray-600">
              © 2024 Price-Scanner. All rights reserved.
            </p>
          </div>
        </footer>
      </main>
    </>
  )
}
