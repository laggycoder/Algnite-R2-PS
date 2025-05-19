import React from 'react';
import { ShoppingCart, CreditCard, XCircle } from 'lucide-react';
import type { ProductDetail } from './ProductModal';

interface CheckoutProps {
  onCheckout: () => void;
  cartItems: ProductDetail[];
  onRemoveItem: (productId: string) => void;
  onProductClick: (product: ProductDetail) => void;
}

const Checkout: React.FC<CheckoutProps> = ({ onCheckout, cartItems, onRemoveItem, onProductClick }) => {
  const itemCount = cartItems.length;

  const calculateTotalPrice = () => {
    return cartItems.reduce((total, item) => {
      const price = parseFloat(item.price.replace('$', ''));
      return total + (isNaN(price) ? 0 : price);
    }, 0).toFixed(2);
  };

  const handleItemClick = (item: ProductDetail) => {
    console.log('[Checkout.tsx] handleItemClick called for:', item.name);
    if (onProductClick) {
        onProductClick(item);
    } else {
        console.error('[Checkout.tsx] onProductClick prop is undefined!');
    }
  };

  return (
    <div className="checkout-area section">
      <h2><CreditCard />Checkout Summary</h2>
      {itemCount > 0 ? (
        <>
          <p className="checkout-summary">
            You have <strong>{itemCount}</strong> item(s) selected for checkout.
          </p>
          <ul className="cart-items-list">
            {cartItems.map((item) => (
              <li key={item.id} className="cart-item">
                <img 
                  src={item.imageUrl} 
                  alt={item.name} 
                  className="cart-item-image"
                  onClick={() => handleItemClick(item)}
                  style={{cursor: 'pointer'}} 
                />
                <div 
                  className="cart-item-details" 
                  onClick={() => handleItemClick(item)}
                  style={{cursor: 'pointer'}}
                >
                  <span className="cart-item-name">{item.name}</span>
                  <span className="cart-item-price">{item.price}</span>
                </div>
                <button 
                  onClick={() => onRemoveItem(item.id)} 
                  className="cart-item-remove-btn btn-icon-subtle danger" /* ADDED CLASSES */
                  aria-label={`Remove ${item.name} from cart`}
                >
                  <XCircle size={20} />
                </button>
              </li>
            ))}
          </ul>
          <p className="checkout-total">
            <strong>Total: ${calculateTotalPrice()}</strong>
          </p>
          <button onClick={onCheckout} disabled={itemCount === 0} className="proceed-to-checkout-btn">
            <ShoppingCart size={20} /> Proceed to Checkout
          </button>
        </>
      ) : (
        <p className="checkout-summary">Your cart is empty. Select some products to add them here!</p>
      )}
    </div>
  );
};
export default Checkout;
