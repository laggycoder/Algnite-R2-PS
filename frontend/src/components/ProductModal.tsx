import React, { useState, useEffect } from 'react';
import { X, ShoppingCart, ArrowLeftCircle, ArrowRightCircle, Trash2, Heart } from 'lucide-react';
import type { Product as ProductTypeFromRecDisplay } from './RecommendationDisplay'; 

export interface ProductDetail extends ProductTypeFromRecDisplay {
  description?: string;
  images?: string[];
  sizes?: string[];
  colors?: string[];
  detailedReasons?: string[]; // New field for granular reasons
  isInWishlist?: boolean;
}

interface ProductModalProps {
  product: ProductDetail | null;
  onClose: () => void;
  onToggleCart: (product: ProductDetail) => void;
  onToggleWishlist: (product: ProductDetail) => void;
}

const ProductModal: React.FC<ProductModalProps> = ({ product, onClose, onToggleCart, onToggleWishlist }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => { setCurrentImageIndex(0); }, [product]);

  if (!product) return null;

  const productImages = product.images && product.images.length > 0 ? product.images : [product.imageUrl];
  const mainImageSrc = productImages[currentImageIndex];

  const nextImage = () => setCurrentImageIndex((prev) => (prev + 1) % productImages.length);
  const prevImage = () => setCurrentImageIndex((prev) => (prev - 1 + productImages.length) % productImages.length);

  return (
    <div className="product-modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="product-modal-title">
      <div className="product-modal" onClick={(e) => e.stopPropagation()}>
        <button className="product-modal-close-button" onClick={onClose} aria-label="Close product details"><X size={28} /></button>
        <div className="product-modal-content">
          <div className="product-modal-image-section">
            <div style={{ position: 'relative', marginBottom: '15px' }}>
                <img src={mainImageSrc} alt={product.name} className="main-image" />
                {productImages.length > 1 && (
                    <>
                        <button onClick={prevImage} className="modal-image-nav-btn prev" aria-label="Previous image"><ArrowLeftCircle size={24}/></button>
                        <button onClick={nextImage} className="modal-image-nav-btn next" aria-label="Next image"><ArrowRightCircle size={24}/></button>
                    </>
                )}
            </div>
            {productImages.length > 1 && (
              <div className="product-modal-thumbnails">
                {productImages.map((imgUrl, index) => (
                  <img key={index} src={imgUrl} alt={`${product.name} view ${index + 1}`}
                    className={index === currentImageIndex ? 'active-thumbnail' : ''}
                    onClick={() => setCurrentImageIndex(index)} />
                ))}
              </div>
            )}
          </div>
          <div className="product-modal-details-section">
            <h3 id="product-modal-title">{product.name}</h3>
            <p className="price">{product.price}</p>
            {product.description && <p className="description">{product.description}</p>}
            
            {/* Displaying detailed reasons in the modal */}
            {product.recommendationReason && !product.detailedReasons?.length && (
              <p className="recommendation-reason">
                <strong>Why this item?</strong> {product.recommendationReason}
              </p>
            )}
            {product.detailedReasons && product.detailedReasons.length > 0 && (
              <div className="recommendation-reason detailed-reasons-modal">
                <strong>Why this item?</strong>
                <ul>
                  {product.detailedReasons.map((reason, idx) => <li key={idx}>{reason}</li>)}
                </ul>
                {product.recommendationReason && <p style={{marginTop: '8px', fontSize: '0.85em'}}><em>Summary: {product.recommendationReason}</em></p>}
              </div>
            )}

            {product.sizes && product.sizes.length > 0 && (<div className="attributes"><p><strong>Sizes:</strong> {product.sizes.join(', ')}</p></div>)}
            {product.colors && product.colors.length > 0 && (<div className="attributes"><p><strong>Colors:</strong> {product.colors.join(', ')}</p></div>)}
            
            <div className="product-modal-actions">
              <button 
                onClick={() => onToggleWishlist(product)} 
                className="wishlist-btn"
                title={product.isInWishlist ? "Remove from Wishlist" : "Add to Wishlist"}
                aria-pressed={product.isInWishlist}
              >
                <Heart size={20} fill={product.isInWishlist ? "var(--danger-color)" : "none"} color={product.isInWishlist ? "var(--danger-color)" : "var(--text-secondary)"}/>
              </button>
              <button 
                onClick={() => onToggleCart(product)} 
                className={product.isInCart ? "remove-from-cart-btn" : "add-to-cart-btn"}
                style={{flexGrow: 1}}
              >
                {product.isInCart ? <><Trash2 size={20} /> Remove from Cart</> : <><ShoppingCart size={20} /> Add to Cart</>}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ProductModal;
