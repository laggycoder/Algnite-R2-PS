import React from 'react';
import { Heart, XCircle } from 'lucide-react';
import type { ProductDetail } from './ProductModal';

interface WishlistDisplayProps {
  wishlistItems: ProductDetail[];
  onRemoveFromWishlist: (productId: string) => void;
  onProductClick: (product: ProductDetail) => void;
}

const WishlistDisplay: React.FC<WishlistDisplayProps> = ({ wishlistItems, onRemoveFromWishlist, onProductClick }) => {
  if (!wishlistItems.length) {
    return (
      <div className="wishlist-display section empty">
        <h2><Heart /> Your Wishlist</h2>
        <p>Your wishlist is empty. Add items you love by clicking the heart icon!</p>
      </div>
    );
  }

  return (
    <div className="wishlist-display section">
      <h2><Heart /> Your Wishlist ({wishlistItems.length})</h2>
      <ul className="wishlist-items-list">
        {wishlistItems.map((item) => (
          <li key={item.id} className="wishlist-item">
            <img 
              src={item.imageUrl} 
              alt={item.name} 
              className="wishlist-item-image" 
              onClick={() => onProductClick(item)}
              style={{cursor: 'pointer'}}
            />
            <div className="wishlist-item-details" onClick={() => onProductClick(item)} style={{cursor: 'pointer', flexGrow: 1}}>
              <span className="wishlist-item-name">{item.name}</span>
              <span className="wishlist-item-price">{item.price}</span>
            </div>
            <button 
              onClick={() => onRemoveFromWishlist(item.id)} 
              className="wishlist-item-remove-btn btn-icon-subtle danger" /* Ensuring correct classes */
              title={`Remove ${item.name} from wishlist`}
              aria-label={`Remove ${item.name} from wishlist`}
            >
              <XCircle size={22} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
export default WishlistDisplay;
