// --- Globals and State ---
let isDarkMode = localStorage.getItem('darkMode') === 'true';
let uploadedFile = null; // The File object itself
let uploadedFileNameServer = null; // Filename given by server for uploaded file (temp)
let currentRecommendations = [];
let cartItems = [];
let wishlistItems = [];
let detailedProductToShow = null;
let lastPromptUsedForImage = ""; // To remember prompt if image is re-uploaded or cleared

const API_BASE_URL = ''; // Flask serves from root, so relative paths work

// --- DOM Elements ---
const darkModeToggle = document.getElementById('darkModeToggle');
const darkModeIcon = document.getElementById('darkModeIcon'); // Icon within the toggle
const imageFileInput = document.getElementById('imageFile');
const imagePreview = document.getElementById('imagePreview');
const imagePreviewPlaceholder = document.getElementById('imagePreviewPlaceholder');

const promptForm = document.getElementById('promptForm');
const promptInput = document.getElementById('promptInput');
const clearPromptBtn = document.getElementById('clearPromptBtn');
const sendPromptBtn = document.getElementById('sendPromptBtn');
const examplePromptsList = document.getElementById('examplePromptsList');

const aiInsightsSection = document.getElementById('aiInsightsSection');
const openaiDescriptionText = document.getElementById('openaiDescriptionText');
const geminiRefinementText = document.getElementById('geminiRefinementText');

const loadingText = document.getElementById('loadingText');
const noRecommendationsText = document.getElementById('noRecommendationsText');
const initialMessage = document.getElementById('initialMessage');
const recommendationGrid = document.getElementById('recommendationGrid');

const wishlistSection = document.getElementById('wishlistSection');
const wishlistCount = document.getElementById('wishlistCount');
const emptyWishlistMessage = document.getElementById('emptyWishlistMessage');
const wishlistItemsList = document.getElementById('wishlistItemsList');

const checkoutSection = document.getElementById('checkoutSection');
const emptyCartMessage = document.getElementById('emptyCartMessage');
const cartContents = document.getElementById('cartContents');
const cartItemCount = document.getElementById('cartItemCount');
const cartItemsList = document.getElementById('cartItemsList');
const cartTotal = document.getElementById('cartTotal');
const cartTotalPrice = document.getElementById('cartTotalPrice');
const proceedToCheckoutBtn = document.getElementById('proceedToCheckoutBtn');

const productModalOverlay = document.getElementById('productModalOverlay');
const productModal = document.getElementById('productModal');
const productModalCloseBtn = document.getElementById('productModalCloseBtn');
const modalMainImage = document.getElementById('modalMainImage');
const modalThumbnails = document.getElementById('modalThumbnails');
const modalProductName = document.getElementById('modalProductName');
const modalProductPrice = document.getElementById('modalProductPrice');
const modalProductDescription = document.getElementById('modalProductDescription');
const modalProductAttributes = document.getElementById('modalProductAttributes');
const modalRecommendationReason = document.getElementById('modalRecommendationReason');
const modalReasonText = document.getElementById('modalReasonText');
const modalDetailedReasonsList = document.getElementById('modalDetailedReasonsList');
const modalToggleWishlistBtn = document.getElementById('modalToggleWishlistBtn');
const modalWishlistBtnText = document.getElementById('modalWishlistBtnText');
const modalToggleCartBtn = document.getElementById('modalToggleCartBtn');
const modalCartBtnText = document.getElementById('modalCartBtnText');


// --- Utility Functions ---
function showLoading(isLoading) {
    loadingText.style.display = isLoading ? 'block' : 'none';
    if(sendPromptBtn) sendPromptBtn.disabled = isLoading;
    if(imageFileInput) imageFileInput.disabled = isLoading;

    if (isLoading) {
        if(recommendationGrid) recommendationGrid.innerHTML = '';
        if(noRecommendationsText) noRecommendationsText.style.display = 'none';
        if(initialMessage) initialMessage.style.display = 'none';
        // Consider hiding AI insights while new data is loading
        // if(aiInsightsSection) aiInsightsSection.style.display = 'none';
    }
}

function updateIconPlaceholders() {
    // This function can be removed if you implement proper icons in HTML.
}

// --- Dark Mode ---
function applyDarkMode() {
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        if (darkModeIcon) darkModeIcon.textContent = '☀️'; // Sun
    } else {
        document.body.classList.remove('dark-mode');
        if (darkModeIcon) darkModeIcon.textContent = '🌙'; // Moon
    }
    localStorage.setItem('darkMode', isDarkMode);
}

// --- API Calls ---
async function fetchApi(endpoint, options = {}) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! Status: ${response.status}` }));
            console.error(`API Error (${response.status}) for ${endpoint}:`, errorData);
            alert(`Error from server: ${errorData.error || response.statusText}. Check console for details.`);
            // Do not call showLoading(false) here if you want the loading indicator to persist on error
            // or handle error display more gracefully. For now, we'll stop loading.
            showLoading(false);
            return null;
        }
        // showLoading(false) will be called by the calling function (fetchAndDisplayRecommendations)
        return response.json();
    } catch (error) {
        console.error(`Network or other critical error for ${endpoint}:`, error);
        alert('Network error or application issue. Please try again or check console.');
        showLoading(false);
        return null;
    }
}

// --- Recommendations & AI Insights Display ---
function renderProductCard(product) {
    const isInCart = cartItems.some(item => item.id === product.id);
    const isInWishlist = wishlistItems.some(item => item.id === product.id);

    const card = document.createElement('div');
    card.className = 'product-card';
    card.dataset.productId = product.id;

    const wishlistHeartIcon = isInWishlist ? '💖' : '🤍';
    let cartBadgeHTML = isInCart ? `<div class="card-cart-status-badge" title="In Cart">🛒</div>` : '';
    
    let reasonHTML = product.recommendationReason ? `<p class="recommendation-reason">${product.recommendationReason}</p>` : '';
    const whyIconHTML = product.detailedReasons && product.detailedReasons.length > 0 ? 
        `<span class="why-recommendation-icon" title="Why recommended? Click card for details." style="cursor: help;">ℹ️</span>` : '';

    card.innerHTML = `
        <div class="card-actions-overlay">
            ${cartBadgeHTML}
            <button class="card-wishlist-btn" data-product-id="${product.id}" title="${isInWishlist ? 'Remove from' : 'Add to'} Wishlist">
                ${wishlistHeartIcon}
            </button>
        </div>
        <div class="product-card-image-wrapper">
            <img src="${product.imageUrl || 'https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImage'}" alt="${product.name || 'Product Image'}">
        </div>
        <div class="product-info">
            <div class="product-name-wrapper">
                <span class="product-name">${product.name || 'Unnamed Product'}</span>
                ${whyIconHTML}
            </div>
            <p class="product-price">${product.price || '$?.??'}</p>
            ${product.type ? `<span class="product-type">${product.type}</span>` : ''}
            ${reasonHTML}
        </div>
    `;
    card.addEventListener('click', (e) => {
        if (e.target.closest('.card-wishlist-btn')) return;
        handleProductCardClick(product.id);
    });
    card.querySelector('.card-wishlist-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleWishlist(product.id);
    });
    return card;
}

function displayRecommendations(products) {
    currentRecommendations = products || [];
    if(recommendationGrid) recommendationGrid.innerHTML = '';
    
    if (currentRecommendations.length > 0) {
        currentRecommendations.forEach(product => {
            const cardElement = renderProductCard(product);
            if(recommendationGrid) recommendationGrid.appendChild(cardElement);
        });
        if(noRecommendationsText) noRecommendationsText.style.display = 'none';
    } else {
        if(noRecommendationsText) noRecommendationsText.style.display = 'block';
    }
    if(initialMessage) initialMessage.style.display = 'none';
}

function displayAiInsights(openaiDesc, geminiRefine) {
    let insightsVisible = false;
    if (openaiDescriptionText) {
        if (openaiDesc) {
            openaiDescriptionText.textContent = openaiDesc;
            insightsVisible = true;
        } else {
            openaiDescriptionText.textContent = 'N/A';
        }
    }

    if (geminiRefinementText) {
        if (geminiRefine) {
            let geminiStr = ""; // Start with an empty string, not "Gemini Insights:\n"
            if (typeof geminiRefine === 'object' && geminiRefine !== null) {
                if (geminiRefine.error) {
                     geminiStr = `Gemini Error: ${geminiRefine.error}\n`; // Assign directly
                     if(geminiRefine.raw_text) geminiStr += `Raw Details: ${geminiRefine.raw_text}`;
                } else {
                    if (geminiRefine.key_attributes) geminiStr += `Key Attributes: ${(Array.isArray(geminiRefine.key_attributes) ? geminiRefine.key_attributes.join(', ') : geminiRefine.key_attributes)}\n\n`;
                    if (geminiRefine.suggested_search_terms) geminiStr += `Suggested Searches: ${(Array.isArray(geminiRefine.suggested_search_terms) ? geminiRefine.suggested_search_terms.join(', ') : geminiRefine.suggested_search_terms)}\n\n`;
                    if (geminiRefine.catchy_phrase) geminiStr += `Style Idea: "${geminiRefine.catchy_phrase}"\n\n`;
                    if (geminiRefine.complementary_ideas) geminiStr += `Try with: ${(Array.isArray(geminiRefine.complementary_ideas) ? geminiRefine.complementary_ideas.join(', ') : geminiRefine.complementary_ideas)}\n\n`;
                    // Fallback for raw_text only if other structured fields were not present or to add more detail
                    if (geminiRefine.raw_text && (!geminiRefine.key_attributes && !geminiRefine.suggested_search_terms)) {
                         geminiStr += `Raw Gemini Output: ${geminiRefine.raw_text}`;
                    }
                }
            } else if (typeof geminiRefine === 'string') { // If Gemini returns a plain string
                 geminiStr = geminiRefine;
            } else {
                geminiStr = "N/A or unexpected format from Gemini.";
            }
            geminiRefinementText.textContent = geminiStr.trim() || "No specific refinement suggestions from Gemini.";
            insightsVisible = true;
        } else {
            geminiRefinementText.textContent = 'N/A';
        }
    }
    if(aiInsightsSection) aiInsightsSection.style.display = insightsVisible ? 'block' : 'none';
}

async function fetchAndDisplayRecommendations(prompt = '', imageFileForUpload = null) {
    // showLoading(true) is now called within fetchApi
    lastPromptUsedForImage = prompt;

    let data;
    if (imageFileForUpload) {
        const formData = new FormData();
        formData.append('imageFile', imageFileForUpload);
        if (prompt) formData.append('prompt', prompt);
        data = await fetchApi('/upload_image', { method: 'POST', body: formData });
        if (data) uploadedFileNameServer = data.filename_server_temp;
    } else {
        data = await fetchApi('/get_recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt }),
        });
    }
    // showLoading(false) is now called within fetchApi or its error handler

    if (data) {
        displayRecommendations(data.recommendations);
        displayAiInsights(data.openai_description, data.gemini_refinement);
        if (imageFileForUpload && data.image_preview_url) {
            if(imagePreview) imagePreview.src = data.image_preview_url;
            if(imagePreview) imagePreview.style.display = 'block';
            if(imagePreviewPlaceholder) imagePreviewPlaceholder.style.display = 'none';
        }
    } else {
        // fetchApi handles alerts for errors, so just ensure UI reflects empty state
        displayRecommendations([]);
        displayAiInsights(null, { error: "Failed to fetch data or server returned an error." });
    }
}

// --- Image Upload ---
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadedFile = file; // Store the File object
        const reader = new FileReader();
        reader.onload = function(e) {
            if(imagePreview) imagePreview.src = e.target.result;
            if(imagePreview) imagePreview.style.display = 'block';
            if(imagePreviewPlaceholder) imagePreviewPlaceholder.style.display = 'none';
        }
        reader.readAsDataURL(file);
        // Fetch recommendations using the new file and current prompt
        fetchAndDisplayRecommendations(promptInput.value.trim(), uploadedFile);
    }
}

// --- Chat/Prompt ---
function handlePromptSubmit(event) {
    event.preventDefault();
    const promptValue = promptInput.value.trim();
    // If an image is currently displayed (and thus `uploadedFile` is likely set from last upload),
    // send the prompt along with that image context. Otherwise, text-only.
    if (imagePreview && imagePreview.style.display === 'block' && uploadedFile) {
        fetchAndDisplayRecommendations(promptValue, uploadedFile);
    } else {
        fetchAndDisplayRecommendations(promptValue, null); // Text-only search
    }
}

function populateExamplePrompts() {
    if(!examplePromptsList) return;
    const examples = [ "show me something in red", "more formal options", "casual summer wear", "matching accessories"];
    examplePromptsList.innerHTML = ''; // Clear existing
    examples.forEach(ex => {
        const li = document.createElement('li');
        li.textContent = ex;
        li.setAttribute('role', 'button');
        li.tabIndex = 0;
        li.addEventListener('click', () => {
            if(promptInput) promptInput.value = ex;
            if(clearPromptBtn) clearPromptBtn.style.display = 'inline-block';
            // Create a new event object for the submit handler
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            if(promptForm) promptForm.dispatchEvent(submitEvent);
        });
        li.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') li.click(); });
        examplePromptsList.appendChild(li);
    });
}

// --- Wishlist & Cart (Helper: Find Product) ---
function findProductById(productId) {
    // Ensure currentRecommendations is an array before calling find
    const recs = Array.isArray(currentRecommendations) ? currentRecommendations : [];
    const wish = Array.isArray(wishlistItems) ? wishlistItems : [];
    const cart = Array.isArray(cartItems) ? cartItems : [];

    return recs.find(p => p.id === productId) ||
           wish.find(p => p.id === productId) ||
           cart.find(p => p.id === productId) ||
           (detailedProductToShow && detailedProductToShow.id === productId ? detailedProductToShow : null);
}

// --- Wishlist ---
function updateWishlistDisplay() {
    if(!wishlistItemsList || !emptyWishlistMessage || !wishlistCount) return;
    wishlistItemsList.innerHTML = '';
    emptyWishlistMessage.style.display = wishlistItems.length === 0 ? 'block' : 'none';
    
    wishlistItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'wishlist-item';
        li.innerHTML = `
            <img src="${item.imageUrl || '#'}" alt="${item.name || 'Product'}" class="wishlist-item-image">
            <div class="wishlist-item-details">
                <span class="wishlist-item-name">${item.name || 'N/A'}</span>
                <span class="wishlist-item-price">${item.price || 'N/A'}</span>
            </div>
            <button class="wishlist-item-remove-btn btn-icon-subtle danger" data-product-id="${item.id}" title="Remove ${item.name || ''} from wishlist" aria-label="Remove ${item.name || ''} from wishlist">
                <span class="icon-placeholder-small">🗑️</span>
            </button>
        `;
        // Add event listeners to image and details to open modal
        li.querySelector('.wishlist-item-image').addEventListener('click', () => handleProductCardClick(item.id));
        li.querySelector('.wishlist-item-details').addEventListener('click', () => handleProductCardClick(item.id));
        li.querySelector('.wishlist-item-remove-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            toggleWishlist(item.id);
        });
        wishlistItemsList.appendChild(li);
    });
    wishlistCount.textContent = wishlistItems.length;
    displayRecommendations(currentRecommendations); // Re-render product cards for icon updates
    if (detailedProductToShow) updateModalButtons(detailedProductToShow.id);
}

function toggleWishlist(productId) {
    const product = findProductById(productId);
    if (!product) { console.warn("Product not found for wishlist toggle:", productId); return; }
    
    const index = wishlistItems.findIndex(item => item.id === productId);
    if (index > -1) {
        wishlistItems.splice(index, 1);
    } else {
        wishlistItems.push(product);
    }
    updateWishlistDisplay();
}

// --- Cart ---
function updateCartDisplay() {
    if(!cartItemsList || !emptyCartMessage || !cartContents || !proceedToCheckoutBtn || !cartItemCount || !cartTotalPrice) return;
    cartItemsList.innerHTML = '';
    const isEmpty = cartItems.length === 0;
    emptyCartMessage.style.display = isEmpty ? 'block' : 'none';
    cartContents.style.display = isEmpty ? 'none' : 'block';
    proceedToCheckoutBtn.disabled = isEmpty;

    let currentTotal = 0;
    cartItems.forEach(item => {
        const priceVal = parseFloat((item.price || '$0').replace('$', ''));
        if (!isNaN(priceVal)) currentTotal += priceVal;
        
        const li = document.createElement('li');
        li.className = 'cart-item';
        li.innerHTML = `
            <img src="${item.imageUrl || '#'}" alt="${item.name || 'Product'}" class="cart-item-image">
            <div class="cart-item-details">
                <span class="cart-item-name">${item.name || 'N/A'}</span>
                <span class="cart-item-price">${item.price || 'N/A'}</span>
            </div>
            <button class="cart-item-remove-btn btn-icon-subtle danger" data-product-id="${item.id}" title="Remove ${item.name || ''} from cart" aria-label="Remove ${item.name || ''} from cart">
                <span class="icon-placeholder-small">🗑️</span>
            </button>
        `;
        li.querySelector('.cart-item-image').addEventListener('click', () => handleProductCardClick(item.id));
        li.querySelector('.cart-item-details').addEventListener('click', () => handleProductCardClick(item.id));
        li.querySelector('.cart-item-remove-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            toggleCart(item.id);
        });
        cartItemsList.appendChild(li);
    });
    cartItemCount.textContent = cartItems.length;
    cartTotalPrice.textContent = currentTotal.toFixed(2);
    displayRecommendations(currentRecommendations); // Re-render product cards for icon updates
    if (detailedProductToShow) updateModalButtons(detailedProductToShow.id);
}

function toggleCart(productId) {
    const product = findProductById(productId);
    if (!product) { console.warn("Product not found for cart toggle:", productId); return; }

    const index = cartItems.findIndex(item => item.id === productId);
    if (index > -1) {
        cartItems.splice(index, 1);
    } else {
        cartItems.push(product);
        if (detailedProductToShow && detailedProductToShow.id === productId) {
            closeModal(); // Close modal if item added from modal
        }
    }
    updateCartDisplay();
}

// --- Product Modal ---
function updateModalButtons(productId) {
    if(!modalToggleWishlistBtn || !modalToggleCartBtn || !modalWishlistBtnText || !modalCartBtnText) return;
    const isInCart = cartItems.some(item => item.id === productId);
    const isInWishlist = wishlistItems.some(item => item.id === productId);

    modalWishlistBtnText.textContent = isInWishlist ? 'Remove from Wishlist' : 'Add to Wishlist';
    modalToggleWishlistBtn.querySelector('.icon-placeholder-small').textContent = isInWishlist ? '💖' : '🤍';
    
    modalCartBtnText.textContent = isInCart ? 'Remove from Cart' : 'Add to Cart';
    // Ensure class change for styling if you have .remove-from-cart-btn specific styles in modal
    modalToggleCartBtn.classList.remove('add-to-cart-btn', 'remove-from-cart-btn');
    modalToggleCartBtn.classList.add(isInCart ? 'remove-from-cart-btn' : 'add-to-cart-btn');
    modalToggleCartBtn.querySelector('.icon-placeholder-small').textContent = isInCart ? '➖' : '➕';
}

function handleProductCardClick(productId) {
    const product = findProductById(productId);
    if (!product) { console.error("Product not found for modal:", productId); return; }
    detailedProductToShow = product;

    if(modalMainImage) modalMainImage.src = (product.images && product.images.length > 0 ? product.images[0] : product.imageUrl) || '#';
    if(modalProductName) modalProductName.textContent = product.name || 'Product Name';
    if(modalProductPrice) modalProductPrice.textContent = product.price || '$?.??';
    if(modalProductDescription) modalProductDescription.textContent = product.description || "No description available.";

    if(modalProductAttributes) {
        modalProductAttributes.innerHTML = ''; // Clear previous attributes
        if (product.sizes && product.sizes.length) modalProductAttributes.innerHTML += `<p><strong>Sizes:</strong> ${product.sizes.join(', ')}</p>`;
        if (product.colors && product.colors.length) modalProductAttributes.innerHTML += `<p><strong>Colors:</strong> ${product.colors.join(', ')}</p>`;
        if (product.material) modalProductAttributes.innerHTML += `<p><strong>Material:</strong> ${product.material}</p>`;
        // Add other attributes if they exist in product object
    }

    if(modalRecommendationReason && modalReasonText && modalDetailedReasonsList) {
        if (product.recommendationReason || (product.detailedReasons && product.detailedReasons.length)) {
            modalRecommendationReason.style.display = 'block';
            modalReasonText.textContent = product.recommendationReason || "Details below.";
            modalDetailedReasonsList.innerHTML = ''; // Clear previous
            if (product.detailedReasons && product.detailedReasons.length) {
                product.detailedReasons.forEach(reason => {
                    const li = document.createElement('li');
                    li.textContent = reason;
                    modalDetailedReasonsList.appendChild(li);
                });
            }
        } else {
            modalRecommendationReason.style.display = 'none';
        }
    }

    if(modalThumbnails) {
        modalThumbnails.innerHTML = ''; // Clear previous
        if (product.images && product.images.length > 1) {
            product.images.forEach((imgUrl, index) => {
                const thumb = document.createElement('img');
                thumb.src = imgUrl;
                thumb.alt = `View image ${index + 1}`;
                thumb.classList.add(index === 0 ? 'active-thumbnail' : '');
                thumb.addEventListener('click', () => {
                    if(modalMainImage) modalMainImage.src = imgUrl;
                    modalThumbnails.querySelectorAll('img').forEach(t => t.classList.remove('active-thumbnail'));
                    thumb.classList.add('active-thumbnail');
                });
                modalThumbnails.appendChild(thumb);
            });
        }
    }
    
    updateModalButtons(productId);
    if(productModalOverlay) productModalOverlay.style.display = 'flex';
}

function closeModal() {
    if(productModalOverlay) productModalOverlay.style.display = 'none';
    detailedProductToShow = null;
}

// --- Checkout ---
async function handleCheckout() {
    if (cartItems.length === 0) { alert("Your cart is empty."); return; }
    const payload = { cartItems: cartItems.map(item => ({id: item.id, name: item.name, price: item.price })) };
    const result = await fetchApi('/mock_checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (result && result.message) {
        alert(result.message);
        // Optionally clear cart after mock checkout:
        // cartItems = [];
        // updateCartDisplay();
    } else {
        alert("Checkout failed or no message received. Please try again.");
    }
}

// --- Event Listeners & Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Null checks for all DOM elements to prevent errors if HTML structure changes
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            isDarkMode = !isDarkMode;
            applyDarkMode();
        });
    }
    if(imageFileInput) imageFileInput.addEventListener('change', handleImageUpload);
    if(promptForm) promptForm.addEventListener('submit', handlePromptSubmit);

    if(promptInput && clearPromptBtn) {
        promptInput.addEventListener('input', () => {
            clearPromptBtn.style.display = promptInput.value ? 'inline-block' : 'none';
        });
        clearPromptBtn.addEventListener('click', () => {
            promptInput.value = '';
            clearPromptBtn.style.display = 'none';
            uploadedFile = null; // Clear uploaded file context
            uploadedFileNameServer = null;
            if(imagePreview) imagePreview.style.display = 'none';
            if(imagePreviewPlaceholder) imagePreviewPlaceholder.style.display = 'block';
            if(aiInsightsSection) aiInsightsSection.style.display = 'none';
            fetchAndDisplayRecommendations('', null); // Fetch initial/generic recommendations
        });
    }

    if(productModalCloseBtn) productModalCloseBtn.addEventListener('click', closeModal);
    if(productModalOverlay) {
        productModalOverlay.addEventListener('click', (event) => {
            if (event.target === productModalOverlay) closeModal(); // Close if overlay (backdrop) is clicked
        });
    }
    
    if(modalToggleWishlistBtn && modalToggleCartBtn) {
        modalToggleWishlistBtn.addEventListener('click', () => {
            if (detailedProductToShow) toggleWishlist(detailedProductToShow.id);
        });
        modalToggleCartBtn.addEventListener('click', () => {
            if (detailedProductToShow) toggleCart(detailedProductToShow.id);
        });
    }

    if(proceedToCheckoutBtn) proceedToCheckoutBtn.addEventListener('click', handleCheckout);

    // Initial Setup
    applyDarkMode();
    updateIconPlaceholders(); // Call this if you have specific JS logic for icons
    const currentYearEl = document.getElementById('currentYear');
    if(currentYearEl) currentYearEl.textContent = new Date().getFullYear();
    
    if (typeof initialRecommendationsFromServer !== 'undefined' && initialRecommendationsFromServer.length > 0) {
        displayRecommendations(initialRecommendationsFromServer);
    } else {
       if(initialMessage) initialMessage.style.display = 'block';
    }
    populateExamplePrompts();
});