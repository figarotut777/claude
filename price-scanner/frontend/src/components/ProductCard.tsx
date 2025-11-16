import { Product } from '@/utils/types'
import Image from 'next/image'

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const {
    name,
    description,
    image_url,
    marketplace,
    price,
    currency,
    url,
    rating,
    reviews_count,
    in_stock,
  } = product

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      {/* Product Image */}
      <div className="relative h-48 bg-gray-100">
        {image_url ? (
          <Image
            src={image_url}
            alt={name}
            fill
            className="object-cover"
            unoptimized
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            No Image
          </div>
        )}
        {/* Marketplace Badge */}
        <div className="absolute top-2 right-2">
          <span className="bg-white px-2 py-1 rounded-full text-xs font-medium text-gray-700 shadow-sm">
            {marketplace}
          </span>
        </div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-gray-900 line-clamp-2 mb-2">
          {name}
        </h3>

        {/* Description */}
        {description && (
          <p className="text-sm text-gray-600 line-clamp-2 mb-3">
            {description}
          </p>
        )}

        {/* Rating */}
        {rating && (
          <div className="flex items-center mb-2">
            <div className="flex items-center">
              <span className="text-yellow-400 text-sm">★</span>
              <span className="ml-1 text-sm font-medium text-gray-700">
                {rating.toFixed(1)}
              </span>
            </div>
            {reviews_count && (
              <span className="ml-2 text-sm text-gray-500">
                ({reviews_count.toLocaleString()} reviews)
              </span>
            )}
          </div>
        )}

        {/* Price */}
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-2xl font-bold text-gray-900">
              {currency === 'USD' ? '$' : currency}
              {price.toFixed(2)}
            </span>
          </div>
          {!in_stock && (
            <span className="text-sm text-red-600 font-medium">
              Out of Stock
            </span>
          )}
        </div>

        {/* CTA Button */}
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className={`block w-full text-center px-4 py-2 rounded-lg font-medium transition-colors ${
            in_stock
              ? 'bg-primary-600 text-white hover:bg-primary-700'
              : 'bg-gray-300 text-gray-600 cursor-not-allowed'
          }`}
        >
          {in_stock ? 'View on ' + marketplace : 'Out of Stock'}
        </a>
      </div>
    </div>
  )
}
