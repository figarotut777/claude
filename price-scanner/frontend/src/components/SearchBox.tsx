import { useState, useRef } from 'react'
import { searchByText, searchByImage, searchByURL } from '@/utils/api'
import { Product } from '@/utils/types'

interface SearchBoxProps {
  onSearch: (results: Product[], query: string) => void
  setIsLoading: (loading: boolean) => void
}

export default function SearchBox({ onSearch, setIsLoading }: SearchBoxProps) {
  const [activeTab, setActiveTab] = useState<'text' | 'image' | 'url'>('text')
  const [textQuery, setTextQuery] = useState('')
  const [urlQuery, setUrlQuery] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleTextSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!textQuery.trim()) {
      setError('Please enter a search query')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      const response = await searchByText(textQuery)
      onSearch(response.results, textQuery)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleImageSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!imageFile) {
      setError('Please select an image')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      // Convert image to base64
      const reader = new FileReader()
      reader.onloadend = async () => {
        const base64 = reader.result as string
        const base64Data = base64.split(',')[1]

        const response = await searchByImage(undefined, base64Data)
        onSearch(response.results, 'Image Search')
      }
      reader.readAsDataURL(imageFile)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Image search failed. Please try again.')
      setIsLoading(false)
    }
  }

  const handleURLSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!urlQuery.trim()) {
      setError('Please enter a URL')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      const response = await searchByURL(urlQuery)
      onSearch(response.results, response.query)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'URL search failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0])
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          className={`px-6 py-3 font-medium ${
            activeTab === 'text'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          onClick={() => setActiveTab('text')}
        >
          Text Search
        </button>
        <button
          className={`px-6 py-3 font-medium ${
            activeTab === 'image'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          onClick={() => setActiveTab('image')}
        >
          Image Search
        </button>
        <button
          className={`px-6 py-3 font-medium ${
            activeTab === 'url'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          onClick={() => setActiveTab('url')}
        >
          URL Search
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Text Search */}
      {activeTab === 'text' && (
        <form onSubmit={handleTextSearch} className="space-y-4">
          <div>
            <input
              type="text"
              value={textQuery}
              onChange={(e) => setTextQuery(e.target.value)}
              placeholder="Search for products..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Search
          </button>
        </form>
      )}

      {/* Image Search */}
      {activeTab === 'image' && (
        <form onSubmit={handleImageSearch} className="space-y-4">
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 transition-colors"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />
            {imageFile ? (
              <div>
                <p className="text-gray-700 font-medium">{imageFile.name}</p>
                <p className="text-gray-500 text-sm mt-1">
                  Click to change image
                </p>
              </div>
            ) : (
              <div>
                <p className="text-gray-700 font-medium">
                  Click to upload image
                </p>
                <p className="text-gray-500 text-sm mt-1">
                  or drag and drop
                </p>
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={!imageFile}
            className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Search by Image
          </button>
        </form>
      )}

      {/* URL Search */}
      {activeTab === 'url' && (
        <form onSubmit={handleURLSearch} className="space-y-4">
          <div>
            <input
              type="url"
              value={urlQuery}
              onChange={(e) => setUrlQuery(e.target.value)}
              placeholder="Paste product URL (Amazon, eBay, etc.)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Find Similar Products
          </button>
        </form>
      )}
    </div>
  )
}
