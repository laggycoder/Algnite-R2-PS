import React from 'react';
import { ShoppingBag, Heart, CheckSquare, Info } from 'lucide-react'; // Added Info icon

// Ensure Product interface here matches ProductDetail from ProductModal.tsx for detailedReasons
export interface Product {
  id: string;
  name: string;
  imageUrl: string;
  price: string;
  type: 'similar' | 'complementary';
  description?: string;
  images?: string[];
  sizes?: string[];
  colors?: string[];
  recommendationReason?: string;
  detailedReasons?: string[]; // Added here
  isInCart?: boolean;
  isInWishlist?: boolean;
}

interface RecommendationDisplayProps {
  products: Product[];
  onProductClick: (product: Product) => void;
  onToggleWishlistOnCard: (productId: string, e: React.MouseEvent) => void;
}

const RecommendationDisplay: React.FC<RecommendationDisplayProps> = ({ products, onProductClick, onToggleWishlistOnCard }) => {
  if (!products.length) return null; 

  return (
    <div className="recommendation-display section">
      <h2><ShoppingBag />Product Recommendations</h2>
      <div className="recommendation-grid">
        {products.map((product) => (
          <div 
            key={product.id} 
            className="product-card"
          >
            <div className="product-card-image-wrapper" onClick={() => onProductClick(product)}>
              <img src={product.imageUrl} alt={product.name} />
              <div className="card-actions-overlay">
                <button 
                    className="card-wishlist-btn" 
                    onClick={(e) => onToggleWishlistOnCard(product.id, e)}
                    title={product.isInWishlist ? "Remove from Wishlist" : "Add to Wishlist"}
                    aria-pressed={product.isInWishlist}
                >
                    <Heart size={20} fill={product.isInWishlist ? "var(--danger-color)" : "none"} color={product.isInWishlist ? "var(--danger-color)" : "var(--text-secondary)"}/>
                </button>
                {product.isInCart && (
                  <div className="card-cart-status-badge" title="In Cart">
                    <CheckSquare size={18}/>
                  </div>
                )}
              </div>
            </div>
            <div className="product-info" onClick={() => onProductClick(product)}>
                <div className="product-name-wrapper">
                    <p className="product-name">{product.name}</p>
                    {/* "Why?" Icon and Tooltip */}
                    {product.detailedReasons && product.detailedReasons.length > 0 && (
                        <span 
                            className="why-recommendation-icon" 
                            title={`Why this item?\n- ${product.detailedReasons.join('\n- ')}\n\nSummary: ${product.recommendationReason || ''}`}
                            aria-label="More information about this recommendation"
                        >
                            <Info size={16} />
                        </span>
                    )}
                </div>
                {product.recommendationReason && (!product.detailedReasons || product.detailedReasons.length === 0) && 
                    <p className="recommendation-reason">{product.recommendationReason.substring(0,50)}...</p>
                }
                <p className="product-price">{product.price}</p>
                <p><span className="product-type">{product.type}</span></p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
export default RecommendationDisplay;
