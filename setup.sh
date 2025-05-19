#!/bin/bash
set -e

APP_CSS_PATH="frontend/src/App.css"

echo "Reverting specific Product Modal button hover effects..."
echo "WARNING: This will overwrite $APP_CSS_PATH."
echo "Press Enter to continue, or Ctrl+C to abort."
read -r

# --- Rewrite App.css with the targeted reversions ---
echo "Rewriting $APP_CSS_PATH..."
cat <<'EOF_CSS' > "$APP_CSS_PATH"
/* --- Base & Typography --- */
:root {
  /* Light Theme (Default) */
  --bg-primary: #f4f7f9;
  --bg-secondary: #ffffff;
  --bg-tertiary: #e2e8f0; 
  --bg-accent: #f8fafc; 

  --text-primary: #3d4852;
  --text-secondary: #718096;
  --text-accent: #2d3748; 
  --text-inverted: #ffffff; 

  --border-primary: #e8eef3;
  --border-secondary: #cbd5e0; 
  --border-accent: #3490dc; 

  --link-color: #3490dc;
  --link-hover-color: #2779bd;

  --success-color: #38a169;
  --success-hover-color: #2f855a;
  --danger-color: #e53e3e;
  --danger-hover-color: #c53030;
  --danger-bg-hover: rgba(229, 62, 62, 0.1);


  --shadow-color-light: rgba(0, 0, 0, 0.06);
  --shadow-color-medium: rgba(45, 55, 72, 0.1);

  --button-bg: #3490dc;
  --button-text: #ffffff;
  --button-hover-bg: #2779bd;

  --header-bg: #2d3748;
  --header-text: #ffffff;
  
  --cart-badge-bg: #38a169;
  --cart-badge-text: #ffffff;
}

.dark-mode {
  /* Dark Theme Overrides */
  --bg-primary: #1a202c;        
  --bg-secondary: #2d3748;      
  --bg-tertiary: #4a5568;       
  --bg-accent: #2d3748;         

  --text-primary: #e2e8f0;      
  --text-secondary: #a0aec0;    
  --text-accent: #f7fafc;       
  --text-inverted: #1a202c;     

  --border-primary: #4a5568;    
  --border-secondary: #718096;  
  --border-accent: #63b3ed;     

  --link-color: #63b3ed;
  --link-hover-color: #90cdf4;

  --success-color: #48bb78;
  --success-hover-color: #38a169;
  --danger-color: #f56565;  
  --danger-hover-color: #e53e3e;
  --danger-bg-hover: rgba(245, 101, 101, 0.15);


  --shadow-color-light: rgba(0, 0, 0, 0.4);
  --shadow-color-medium: rgba(0, 0, 0, 0.5);

  --button-bg: #63b3ed;
  --button-text: #1a202c;
  --button-hover-bg: #4299e1;

  --header-bg: #1A202C; 
  --header-text: #E2E8F0;

  --cart-badge-bg: #48bb78; 
  --cart-badge-text: #1a202c; 
}

html { overflow-y: scroll; }
body { 
  font-family: 'Nunito Sans', 'Segoe UI', Helvetica, Arial, sans-serif; 
  margin: 0; 
  background-color: var(--bg-primary); 
  color: var(--text-primary); 
  line-height: 1.65; 
  -webkit-font-smoothing: antialiased; 
  -moz-osx-font-smoothing: grayscale; 
  transition: background-color 0.3s ease, color 0.3s ease;
}
.app-container { 
  display: flex; 
  flex-direction: column; 
  min-height: 100vh; 
  max-width: 1400px; 
  margin: 0 auto; 
  padding: 25px 30px; 
  box-sizing: border-box; 
}

/* --- Header --- */
header { 
  background-color: var(--header-bg); 
  color: var(--header-text); 
  padding: 20px 30px; 
  text-align: center; 
  border-radius: 10px; 
  margin-bottom: 35px; 
  box-shadow: 0 5px 15px var(--shadow-color-medium); 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  position: relative; 
}
header h1 { 
  margin: 0; 
  font-size: 1.9em; 
  font-weight: 700; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
}
header h1 svg { 
  margin-right: 15px; 
  width: 30px; 
  height: 30px; 
  opacity: 0.9; 
}
.dark-mode-toggle {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8em;
}
.dark-mode-toggle:hover {
  background-color: var(--bg-tertiary);
}

/* --- Main Content Layout --- */
.main-content { display: flex; flex-direction: column; gap: 35px; flex-grow: 1; }
.top-interaction-area { display: flex; flex-direction: row; gap: 35px; align-items: stretch; }
.top-interaction-area > .section { flex: 1; display: flex; flex-direction: column; }

/* --- Sections --- */
.section { 
  background-color: var(--bg-secondary); 
  padding: 30px 35px; 
  border-radius: 10px; 
  box-shadow: 0 4px 12px var(--shadow-color-light); 
}
.section h2 { 
  margin-top: 0; 
  margin-bottom: 25px; 
  color: var(--link-color); 
  border-bottom: 1px solid var(--border-primary); 
  padding-bottom: 15px; 
  font-size: 1.45em; 
  font-weight: 600; 
  display: flex; 
  align-items: center; 
}
.section h2 svg { 
  margin-right: 12px; 
  width: 24px; 
  height: 24px; 
  opacity: 0.85; 
  color: var(--link-color); 
}

/* --- Image Upload & Preview --- */
.image-upload-area input[type='file'] { padding: 15px; border: 2px dashed var(--border-secondary); border-radius: 8px; display: block; width: 100%; box-sizing: border-box; margin-bottom: 20px; background-color: var(--bg-accent); cursor: pointer; transition: border-color 0.2s, background-color 0.2s; color: var(--text-secondary); }
.image-upload-area input[type='file']:hover { border-color: var(--link-color); background-color: var(--bg-tertiary); }
.image-preview-container { flex-grow: 1; display: flex; align-items: center; justify-content: center; background-color: var(--bg-accent); border-radius: 8px; padding: 15px; min-height: 280px; border: 1px solid var(--border-primary); }
.image-preview { max-width: 100%; max-height: 350px; object-fit: contain; border-radius: 6px; }


/* --- Chat Input --- */
.chat-input-area { display: flex; flex-direction: column; }
.chat-input-area form { display: flex; flex-direction: column; gap: 15px; margin-bottom: auto; }
.prompt-input-wrapper { 
  position: relative;
  display: flex; 
  width: 100%; 
}
.prompt-input { 
  padding: 14px 18px; 
  border: 1px solid var(--border-primary); 
  border-radius: 8px; 
  font-size: 1em; 
  background-color: var(--bg-secondary); 
  color: var(--text-primary); 
  flex-grow: 1; 
  width: 100%; 
  box-sizing: border-box; 
  padding-right: 40px; 
}
.prompt-input::placeholder { color: var(--text-secondary); } 
.prompt-input:focus { 
  outline: none; 
  border-color: var(--link-color); 
  box-shadow: 0 0 0 3.5px var(--link-color-transparent, rgba(52, 144, 220, 0.15)); 
}
.dark-mode .prompt-input:focus {
  box-shadow: 0 0 0 3.5px var(--link-color-transparent, rgba(99, 179, 237, 0.25)); 
}
.prompt-clear-btn { 
  position: absolute;
  right: 10px; 
  top: 50%;   
  transform: translateY(-50%); 
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 5px; 
  display: flex; 
  align-items: center;
  justify-content: center;
  line-height: 1; 
  transition: color 0.2s, transform 0.1s ease; /* Added transition */
}
.prompt-clear-btn:hover { 
  color: var(--text-primary);
  /* transform: translateY(-50%) scale(1.1); /* Keep Y centering for absolute, subtle scale */
  transform: scale(1.1); /* Simpler scale as Y is already handled by initial transform */

}
.prompt-clear-btn svg {
  width: 18px;
  height: 18px;
}

.chat-input-area form button[type="submit"] { 
  align-self: flex-end; 
  padding: 12px 25px; 
}
.prompt-examples { margin-top: 20px; font-size: 0.85em; color: var(--text-secondary); border-top: 1px solid var(--border-primary); padding-top: 15px; }
.prompt-examples strong { display: block; margin-bottom: 8px; color: var(--text-primary); }
.prompt-examples ul { list-style: none; padding-left: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.prompt-examples li { background-color: var(--bg-tertiary); color: var(--text-accent); padding: 6px 10px; border-radius: 15px; cursor: pointer; transition: background-color 0.2s, color 0.2s; font-size: 0.9em;}
.prompt-examples li:hover { background-color: var(--link-color); color: var(--button-text); }

/* --- Buttons --- */
button { 
  background-color: var(--button-bg); 
  color: var(--button-text); 
  border: none; 
  padding: 11px 22px; 
  border-radius: 8px; 
  cursor: pointer; 
  font-size: 1em; 
  display: inline-flex; 
  align-items: center; 
  justify-content: center; 
  gap: 10px; 
  transition: background-color 0.2s ease-in-out, transform 0.1s ease, box-shadow 0.2s ease-in-out, color 0.2s ease;
  font-weight: 600; 
  transform: translateY(0px); 
}
button:hover:not(.btn-icon-subtle):not(.prompt-clear-btn):not(.dark-mode-toggle):not(.modal-image-nav-btn):not(.product-modal-close-button):not(.product-modal-actions .wishlist-btn) { 
  background-color: var(--button-hover-bg); 
  box-shadow: 0 2px 5px var(--link-color-transparent, rgba(52, 144, 220, 0.2)); 
  transform: translateY(-1px); 
}

.btn-icon-subtle { 
  background: none !important; 
  border: none !important;
  padding: 8px !important; 
  color: var(--text-secondary);
  border-radius: 50%; 
  box-shadow: none !important;
  transform: translateY(0px); 
  transition: color 0.2s, background-color 0.2s, transform 0.1s ease;
}
.btn-icon-subtle:hover {
  color: var(--text-accent); 
  background-color: var(--bg-tertiary) !important; 
  transform: translateY(0px) scale(1.1); 
  box-shadow: none !important;
}
.btn-icon-subtle.danger { 
    color: var(--danger-color);
}
.btn-icon-subtle.danger:hover { 
    color: var(--danger-hover-color) !important;
    background-color: var(--danger-bg-hover) !important;
}

.dark-mode button:hover:not(.btn-icon-subtle):not(.prompt-clear-btn):not(.dark-mode-toggle):not(.modal-image-nav-btn):not(.product-modal-close-button):not(.product-modal-actions .wishlist-btn) { 
  box-shadow: 0 2px 5px var(--link-color-transparent, rgba(99, 179, 237, 0.25));
}
.dark-mode .btn-icon-subtle:hover { 
    box-shadow: none !important;
}
.dark-mode .btn-icon-subtle.danger:hover {
    background-color: var(--danger-bg-hover) !important; 
}

button:active { 
  transform: translateY(0px); 
  box-shadow: 0 1px 2px var(--link-color-transparent-light, rgba(52, 144, 220, 0.15)); 
}
.dark-mode button:active {
  box-shadow: 0 1px 2px var(--link-color-transparent-light, rgba(99, 179, 237, 0.15));
}
button:disabled { 
  background-color: var(--bg-tertiary); 
  color: var(--text-secondary);   
  cursor: not-allowed; 
  box-shadow: none; 
  transform: translateY(0); 
}
button svg { width: 18px; height: 18px; }

/* ... (Product Recs, Cards, Loading, etc. - KEEP AS IS ) ... */
.recommendation-grid { display: flex; flex-direction: row; overflow-x: auto; overflow-y: hidden; gap: 25px; padding-top: 5px; padding-bottom: 25px; margin-left: -35px; margin-right: -35px; padding-left: 35px; padding-right: 35px; -webkit-overflow-scrolling: touch; scrollbar-width: thin; scrollbar-color: var(--border-secondary) var(--border-primary); }
.recommendation-grid::-webkit-scrollbar { height: 10px; }
.recommendation-grid::-webkit-scrollbar-track { background: var(--border-primary); border-radius: 10px; }
.recommendation-grid::-webkit-scrollbar-thumb { background: var(--border-secondary); border-radius: 10px; border: 2px solid var(--border-primary); }
.recommendation-grid::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); } 
.product-card { position: relative; min-width: 250px; max-width: 250px; flex-shrink: 0; border: 1px solid var(--border-primary); border-radius: 10px; background-color: var(--bg-secondary); box-shadow: 0 3px 8px var(--shadow-color-light); transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; display: flex; flex-direction: column; overflow: hidden; }
.product-card:hover { transform: translateY(-5px) scale(1.01); box-shadow: 0 6px 16px var(--shadow-color-medium); }
.product-card-image-wrapper { position: relative; width: 100%; height: 240px; cursor: pointer; } 
.product-card img { width: 100%; height: 100%; object-fit: cover; background-color: var(--bg-primary); }
.product-card .product-info { padding: 18px; flex-grow: 1; display: flex; flex-direction: column; text-align: left; cursor: pointer; }
.product-card .product-name { font-weight: 600; color: var(--text-accent); font-size: 1em; margin-bottom: 8px; line-height: 1.4; min-height: 2.8em; }
.product-card .product-price { font-weight: 700; color: var(--success-color); font-size: 1.2em; margin-top: auto; margin-bottom: 10px; }
.product-card .product-type { font-size: 0.78em; color: var(--text-accent); background-color: var(--bg-tertiary); padding: 5px 10px; border-radius: 15px; display: inline-block; align-self: flex-start; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; }
.product-card .recommendation-reason { font-size: 0.75em; color: var(--text-secondary); margin-top: 8px; font-style: italic; }
.card-actions-overlay { position: absolute; top: 10px; right: 10px; display: flex; flex-direction: column; gap: 8px; z-index: 3; }
.card-wishlist-btn { background: var(--bg-secondary-semi-transparent, rgba(255,255,255,0.8)); border: none; border-radius: 50%; width: 38px; height: 38px; padding: 0; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 1px 4px var(--shadow-color-light); transition: background-color 0.2s, transform 0.1s ease; transform: translateY(0px); }
.card-wishlist-btn:hover { transform: translateY(0px) scale(1.1); background-color: var(--bg-secondary); } 
.card-cart-status-badge { background-color: var(--cart-badge-bg); color: var(--cart-badge-text); border: none; border-radius: 50%; width: 38px; height: 38px; padding: 0; display: flex; align-items: center; justify-content: center; font-size: 0.7em; font-weight: bold; cursor: default; box-shadow: 0 1px 4px var(--shadow-color-light);}
.dark-mode .card-wishlist-btn { background: var(--bg-primary-semi-transparent, rgba(26, 32, 44, 0.8));}
.dark-mode .card-wishlist-btn:hover { background: var(--bg-tertiary);}
.card-wishlist-btn svg { width: 20px; height: 20px; }
.product-name-wrapper { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.product-name-wrapper .product-name { flex-grow: 1; }
.why-recommendation-icon { color: var(--link-color); cursor: help; flex-shrink: 0; margin-top: 2px; transform: translateY(0px); transition: transform 0.1s ease; }
.why-recommendation-icon:hover { transform: scale(1.15); }
.why-recommendation-icon svg { display: block; }
.loading-text, .no-recommendations-text { text-align: center; padding: 50px 20px; font-size: 1.2em; color: var(--text-secondary); background-color: var(--bg-secondary); border-radius: 10px; box-shadow: 0 3px 8px var(--shadow-color-light); }
.wishlist-display, .checkout-area { }
.wishlist-display.empty p, .checkout-area .empty-cart-message { color: var(--text-secondary); font-style: italic; text-align: center; padding: 20px 0;}
.wishlist-items-list, .cart-items-list { list-style: none; padding: 10px; margin: 0 0 20px 0; max-height: 300px; overflow-y: auto; border: 1px solid var(--border-primary); border-radius: 8px; background-color: var(--bg-accent); 
  &::-webkit-scrollbar { width: 8px; height: 8px; }
  &::-webkit-scrollbar-track { background: var(--bg-accent); border-radius: 10px; } 
  &::-webkit-scrollbar-thumb { background: var(--border-secondary); border-radius: 10px; border: 2px solid var(--bg-accent); }
  &::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }
  scrollbar-width: thin;
  scrollbar-color: var(--border-secondary) var(--bg-accent); 
}
.wishlist-item, .cart-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border-primary); }
.wishlist-items-list > .wishlist-item:first-child, .cart-items-list > .cart-item:first-child { padding-top: 2px; }
.wishlist-items-list > .wishlist-item:last-child, .cart-items-list > .cart-item:last-child { border-bottom: none; padding-bottom: 2px;}
.wishlist-item-image, .cart-item-image { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; margin-right: 15px; background-color: var(--bg-primary); }
.wishlist-item-details, .cart-item-details { flex-grow: 1; }
.wishlist-item-name, .cart-item-name { display: block; font-weight: 600; color: var(--text-accent); font-size: 1em; margin-bottom: 3px; }
.wishlist-item-price, .cart-item-price { display: block; color: var(--text-secondary); font-size: 0.9em; }
.wishlist-item-remove-btn, .cart-item-remove-btn { margin-left: 10px; /* Specific class btn-icon-subtle handles the rest */ }
.checkout-area .checkout-summary { font-size: 1.1em; margin-bottom: 15px; color: var(--text-primary); }
.checkout-area .checkout-summary strong { color: var(--link-color); }
.checkout-total { font-size: 1.2em; font-weight: bold; margin-top: 15px; margin-bottom: 25px; text-align: right; color: var(--success-color); }
.proceed-to-checkout-btn { width: 100%; padding: 14px 25px; font-size: 1.1em; }
footer { text-align: center; padding: 30px 20px; margin-top: 40px; background-color: var(--bg-tertiary); border-top: 1px solid var(--border-secondary); font-size: 0.92em; color: var(--text-secondary); }

/* --- Product Modal --- */
.product-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--modal-overlay-bg, rgba(45, 55, 72, 0.75)); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; backdrop-filter: blur(5px); }
.dark-mode .product-modal-overlay { background-color: var(--modal-overlay-bg-dark, rgba(26, 32, 44, 0.85));}
.product-modal { background-color: var(--bg-secondary); padding: 30px 35px; border-radius: 12px; box-shadow: 0 10px 30px var(--shadow-color-medium); max-width: 800px; width: 90%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; position: relative; }
.product-modal-content { display: flex; flex-direction: row; gap: 30px; }
.product-modal-image-section { flex: 1.2; }
.product-modal-image-section .main-image { width: 100%; max-height: 400px; object-fit: contain; border-radius: 8px; border: 1px solid var(--border-primary); margin-bottom: 15px; }

.modal-image-nav-btn { 
  position: absolute; 
  top: 50%; 
  transform: translateY(-50%); /* Base centering */
  background:var(--modal-nav-btn-bg, rgba(0,0,0,0.35)); 
  border: none; 
  border-radius: 50%; 
  padding: 8px; 
  cursor: pointer; 
  color: var(--text-inverted); 
  z-index: 1; 
  transition: background-color 0.2s, transform 0.1s ease; 
}
.dark-mode .modal-image-nav-btn { 
  background: var(--modal-nav-btn-bg-dark, rgba(255,255,255,0.2)); 
  color: var(--text-primary);
}
.modal-image-nav-btn.prev { left: 10px; }
.modal-image-nav-btn.next { right: 10px; }
.modal-image-nav-btn:hover { 
  background:var(--modal-nav-btn-hover-bg, rgba(0,0,0,0.5)); 
  transform: translateY(-50%) scale(1.05); /* MODIFIED: Subtle scale only */
}
.dark-mode .modal-image-nav-btn:hover { 
  background:var(--modal-nav-btn-hover-bg-dark, rgba(255,255,255,0.3)); 
}

.product-modal-thumbnails { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 5px; }
.product-modal-thumbnails img { width: 70px; height: 70px; object-fit: cover; border-radius: 6px; cursor: pointer; border: 2px solid transparent; opacity: 0.7; transition: opacity 0.2s, border-color 0.2s; }
.product-modal-thumbnails img:hover, .product-modal-thumbnails img.active-thumbnail { border-color: var(--link-color); opacity: 1; }
.product-modal-details-section { flex: 1; display: flex; flex-direction: column; }
.product-modal-details-section h3 { font-size: 1.8em; margin-top: 0; margin-bottom: 10px; color: var(--text-accent); }
.product-modal-details-section .price { font-size: 1.5em; color: var(--success-color); font-weight: 700; margin-bottom: 15px; }
.product-modal-details-section .description { font-size: 0.95em; color: var(--text-primary); margin-bottom: 20px; line-height: 1.7; }
.product-modal-details-section .attributes { margin-top: 15px; }
.product-modal-details-section .attributes p { margin: 5px 0; font-size: 0.9em; }
.product-modal-details-section .attributes strong { color: var(--text-accent); }
.product-modal-details-section .recommendation-reason { font-size: 0.9em; color: var(--text-accent); background: var(--bg-accent); padding: 10px; border-radius: 6px; margin-top: 15px; border-left: 3px solid var(--link-color);}
.detailed-reasons-modal ul { list-style-type: disc; padding-left: 20px; margin-top: 5px; margin-bottom: 10px; font-size: 0.9em;}
.detailed-reasons-modal li { margin-bottom: 4px;}
.product-modal-actions { margin-top: auto; display: flex; gap: 15px; padding-top: 20px; border-top: 1px solid var(--border-primary); }

.product-modal-actions .wishlist-btn { /* MODIFIED: Reverted to original hover */
  background: none; 
  border: 1px solid var(--border-secondary); 
  color: var(--text-primary); 
  padding: 10px; 
  transition: background-color 0.2s, color 0.2s, border-color 0.2s, transform 0.1s ease; 
  transform: translateY(0px); 
}
.product-modal-actions .wishlist-btn:hover { /* MODIFIED: Reverted to original hover */
  background-color: var(--bg-tertiary); 
  border-color: var(--text-secondary); 
  transform: translateY(0px); /* Ensure no transform or very minimal if desired */
}
.product-modal-actions .wishlist-btn svg { transition: fill 0.2s, color 0.2s; }
.product-modal-actions .add-to-cart-btn { flex-grow: 1; background-color: var(--success-color); }
.product-modal-actions .add-to-cart-btn:hover { background-color: var(--success-hover-color); }
.product-modal-actions .remove-from-cart-btn { flex-grow: 1; background-color: var(--danger-color); }
.product-modal-actions .remove-from-cart-btn:hover { background-color: var(--danger-hover-color); }

.product-modal-close-button { /* Now uses .btn-icon-subtle - we can make it more specific if needed */
  position: absolute; top: 15px; right: 15px; 
  font-size: 1.8em; 
  line-height: 1; 
  /* Base styling from .btn-icon-subtle, specific hover below */
}
.product-modal-close-button:hover { /* MODIFIED: Reverted to original subtle hover */
  color: var(--text-accent); 
  background-color: transparent !important; /* No background change */
  transform: translateY(0px) scale(1.05); /* Only very subtle scale, no bg */
  box-shadow: none !important;
}


@media (max-width: 900px) { .top-interaction-area { flex-direction: column; } }
@media (max-width: 768px) { .product-modal-content { flex-direction: column; } .product-modal-image-section .main-image { max-height: 300px; } }
@media (max-width: 600px) {
  .app-container { padding: 20px 15px; } .section { padding: 20px 25px; } header h1 { font-size: 1.7em; }
  .section h2 { font-size: 1.3em; } .product-card { min-width: calc(50% - 10px); max-width: calc(50% - 10px); }
  .product-card img { height: 190px; }
  .recommendation-grid { gap: 15px; margin-left: -25px; margin-right: -25px; padding-left: 25px; padding-right: 25px; flex-wrap: wrap; justify-content: space-between;}
}
EOF_CSS
echo "$APP_CSS_PATH rewritten."

# --- Rewrite ChatInput.tsx ---
# (Ensuring the .prompt-clear-btn does not get general button hover via CSS)
echo "Rewriting $CHAT_INPUT_TSX_PATH..."
cat <<'EOF_CHAT' > "$CHAT_INPUT_TSX_PATH"
import React, { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Send, MessageSquare, X } from 'lucide-react';

interface ChatInputProps {
  onPromptSubmit: (prompt: string) => void;
  disabled: boolean;
  initialPrompt?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({ onPromptSubmit, disabled, initialPrompt = '' }) => {
  const [prompt, setPrompt] = useState(initialPrompt);

  useEffect(() => {
    setPrompt(initialPrompt);
  }, [initialPrompt]);

  const examplePrompts = [
    "show me something in red",
    "more formal options",
    "casual summer wear",
    "matching accessories",
  ];

  const handleExampleClick = (example: string) => {
    setPrompt(example);
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (prompt.trim()) {
      onPromptSubmit(prompt.trim());
    }
  };

  const clearPrompt = () => {
    setPrompt('');
  };

  return (
    <div className="chat-input-area section">
      <h2><MessageSquare size={24} />Refine with a Prompt</h2>
      <form onSubmit={handleSubmit}>
        <div className="prompt-input-wrapper">
          <input
            type="text"
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., 'dark blue jeans', 'elegant dress'"
            disabled={disabled}
            aria-label="Enter prompt to refine search"
          />
          {prompt && (
            <button 
              type="button" 
              onClick={clearPrompt} 
              className="prompt-clear-btn" /* CSS targets this specifically */
              aria-label="Clear prompt"
              title="Clear prompt"
            >
              <X size={18}/>
            </button>
          )}
        </div>
        <button type="submit" disabled={disabled || !prompt.trim()}>
          <Send size={20}/> Send
        </button>
      </form>
      <div className="prompt-examples">
        <strong>Try:</strong>
        <ul>
          {examplePrompts.map((ex, idx) => (
            <li key={idx} onClick={() => handleExampleClick(ex)} role="button" tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && handleExampleClick(ex)}>
              {ex}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
export default ChatInput;
EOF_CHAT
echo "$CHAT_INPUT_TSX_PATH updated."

# --- Rewrite WishlistDisplay.tsx ---
echo "Rewriting $WISHLIST_DISPLAY_TSX_PATH..."
cat <<'EOF_WISH' > "$WISHLIST_DISPLAY_TSX_PATH"
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
              className="wishlist-item-remove-btn btn-icon-subtle danger" 
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
EOF_WISH
echo "$WISHLIST_DISPLAY_TSX_PATH updated."

# --- Rewrite Checkout.tsx ---
echo "Rewriting $CHECKOUT_TSX_PATH..."
cat <<'EOF_CHECK' > "$CHECKOUT_TSX_PATH"
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
EOF_CHECK
echo "$CHECKOUT_TSX_PATH updated."


echo "---------------------------------------------------------------------"
echo "Final Button Hover Polish attempt complete."
echo ""
echo "Next Steps:"
echo "1. Run your development server."
echo "2. Verify Prompt Clear 'X' button position and its hover (subtle scale)."
echo "3. Verify Product Modal Close 'X' button hover (original: color change, subtle scale)."
echo "4. Verify Product Modal Image Navigation Arrows hover (original: background change, subtle scale)."
echo "5. Verify Product Modal Wishlist button hover (original: bg/border color change)."
echo "6. Verify Wishlist & Checkout 'Remove X' buttons now look identical and use the subtle icon hover."
echo "---------------------------------------------------------------------"