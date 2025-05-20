// --- Globals and State ---
let isDarkMode = localStorage.getItem('darkMode') === 'true';
let uploadedFile = null;
let uploadedFileNameServer = null; // To store filename received from server
let currentRecommendations = [];
let cartItems = [];
let wishlistItems = [];
let detailedProductToShow = null; // Store the product data for the modal
let lastPromptUsedForImage = "";

const API_BASE_URL = ''; // Flask serves from root, so relative paths work

// --- DOM Elements ---
const darkModeToggle = document.getElementById('darkModeToggle');
const imageFileInput = document.getElementById('imageFile');
const imagePreview = document.getElementById('imagePreview');
const imagePreviewPlaceholder = document.getElementById('imagePreviewPlaceholder');
const currentPromptForImageUploadInput = document.getElementById('currentPromptForImageUpload');


const promptForm = document.getElementById('promptForm');
const promptInput = document.getElementById('promptInput');
const clearPromptBtn = document.getElementById('clearPromptBtn');
const sendPromptBtn = document.getElementById('sendPromptBtn');
const examplePromptsList = document.getElementById('examplePromptsList');

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
const cartSummaryText = document.getElementById('cartSummaryText');
const cartItemCount = document.getElementById('cartItemCount');
const cartItemsList = document.getElementById('cartItemsList');
const cartTotal = document.getElementById('cartTotal');
const cartTotalPrice = document.getElementById('cartTotalPrice');
const proceedToCheckoutBtn = document.getElementById('proceedToCheckoutBtn');

const productModalOverlay = document.getElementById('productModalOverlay');
const productModal = document.getElementById('productModal'); // The modal itself for event delegation
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
    if (isLoading) {
        recommendationGrid.innerHTML = ''; // Clear previous recommendations
        noRecommendationsText.style.display = 'none';
        initialMessage.style.display = 'none';
    }
}

function updateIconPlaceholders() {
    // This is a hack. Ideally, use SVGs or an icon font.
    // For now, just to make it visually distinct from text.
    document.querySelectorAll('.icon-placeholder').forEach(el => {
        // el.style.fontFamily = 'monospace'; 
        // el.style.display = 'inline-block';
        // el.style.marginRight = '8px';
    });
     document.querySelectorAll('.icon-placeholder-small').forEach(el => {
        // el.style.marginRight = '5px';
    });
}

// --- Dark Mode ---
function applyDarkMode() {
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        darkModeToggle.innerHTML = '<span class="icon-placeholder">☀️</span>'; // Sun
    } else {
        document.body.classList.remove('dark-mode');
        darkModeToggle.innerHTML = '<span class="icon-placeholder">🌙</span>'; // Moon
    }
    localStorage.setItem('darkMode', isDarkMode);
}

// --- API Calls ---
async function fetchApi(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
            console.error(`API Error (${response.status}): ${errorData.error}`);
            alert(`Error: ${errorData.error || response.statusText}`);
            return null;
        }
        return response.json();
    } catch (error) {
        console.error('Network or other error:', error);
        alert('Network error. Please try again.');
        return null;
    }
}

// --- Recommendations ---
function renderProductCard(product) {
    const isInCart = cartItems.some(item => item.id === product.id);
    const isInWishlist = wishlistItems.some(item => item.id === product.id);

    // Create card HTML string or DOM elements
    const card = document.createElement('div');
    card.className = 'product-card';
    card.dataset.productId = product.id;
    // Add to wishlist button (heart icon)
    const wishlistBtnClass = isInWishlist ? 'active' : ''; // Add 'active' class if in wishlist
    const wishlistHeartIcon = isInWishlist ? '❤️' : '🤍'; // Filled or empty heart

    // Card Cart Status Badge
    let cartBadgeHTML = '';
    if (isInCart) {
        cartBadgeHTML = `<div class="card-cart-status-badge" title="In Cart">🛒</div>`;
    }
    
    // Recommendation reason and detailed reasons icon
    let reasonHTML = '';
    if (product.recommendationReason) {
        reasonHTML = `<p class="recommendation-reason">${product.recommendationReason}</p>`;
    }
    // Simplified why icon for now - you might want a proper SVG
    const whyIconHTML = product.detailedReasons && product.detailedReasons.length > 0 ? 
        `<span class="why-recommendation-icon" title="Why this was recommended? Click card for details." style="cursor: help;">ℹ️</span>` : '';


    card.innerHTML = `
        <div class="card-actions-overlay">
            ${cartBadgeHTML}
            <button class="card-wishlist-btn ${wishlistBtnClass}" data-product-id="${product.id}" title="${isInWishlist ? 'Remove from' : 'Add to'} Wishlist">
                ${wishlistHeartIcon}
            </button>
        </div>
        <div class="product-card-image-wrapper">
            <img src="${product.imageUrl || 'https://via.placeholder.com/260x250/CCCCCC/000000?Text=NoImage'}" alt="${product.name}">
        </div>
        <div class="product-info">
            <div class="product-name-wrapper">
                <span class="product-name">${product.name}</span>
                ${whyIconHTML}
            </div>
            <p class="product-price">${product.price}</p>
            ${product.type ? `<span class="product-type">${product.type}</span>` : ''}
            ${reasonHTML}
        </div>
    `;
    // Event listener for clicking the card to open modal
    card.addEventListener('click', (e) => {
        // Prevent modal opening if the wishlist button itself was clicked
        if (e.target.closest('.card-wishlist-btn')) {
            return;
        }
        handleProductCardClick(product.id);
    });

    // Event listener for wishlist button on card
    const cardWishlistBtn = card.querySelector('.card-wishlist-btn');
    if (cardWishlistBtn) {
        cardWishlistBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card click event
            toggleWishlist(product.id);
        });
    }
    return card;
}

function displayRecommendations(products) {
    currentRecommendations = products;
    recommendationGrid.innerHTML = ''; // Clear previous
    if (products && products.length > 0) {
        products.forEach(product => {
            const cardElement = renderProductCard(product);
            recommendationGrid.appendChild(cardElement);
        });
        noRecommendationsText.style.display = 'none';
    } else {
        noRecommendationsText.style.display = 'block';
    }
    showLoading(false);
}

async function fetchRecommendations(prompt = '', imageFileForUpload = null) {
    showLoading(true);
    lastPromptUsedForImage = prompt; // Store the prompt used with the image
    currentPromptForImageUploadInput.value = prompt; // Update hidden input

    if (imageFileForUpload) { // Prioritize image upload if a file is provided
        const formData = new FormData();
        formData.append('imageFile', imageFileForUpload);
        if (prompt) { // Send prompt along with image if available
             formData.append('prompt', prompt);
        }

        const data = await fetchApi('/upload_image', {
            method: 'POST',
            body: formData,
        });
        if (data && data.recommendations) {
            uploadedFileNameServer = data.filename; // Store server filename for subsequent prompt-only calls
            displayRecommendations(data.recommendations);
            // Display the uploaded image preview from server path
            if (data.filepath_url) {
                imagePreview.src = data.filepath_url;
                imagePreview.style.display = 'block';
                imagePreviewPlaceholder.style.display = 'none';
            }
        } else {
            displayRecommendations([]); // Clear or show error
            uploadedFileNameServer = null;
        }
    } else { // Text prompt based search (potentially using a previously uploaded image context)
        const payload = { prompt: prompt };
        if (uploadedFileNameServer) { // If an image was uploaded in this session
            payload.image_filename = uploadedFileNameServer;
        }
        const data = await fetchApi('/get_recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (data && data.recommendations) {
            displayRecommendations(data.recommendations);
        } else {
            displayRecommendations([]);
        }
    }
}


// --- Image Upload ---
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadedFile = file; // Store globally
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            imagePreviewPlaceholder.style.display = 'none';
        }
        reader.readAsDataURL(file);
        
        // Fetch recommendations with this image and current prompt
        const currentPromptText = promptInput.value.trim() || lastPromptUsedForImage;
        fetchRecommendations(currentPromptText, uploadedFile);
    } else {
        uploadedFile = null;
        uploadedFileNameServer = null; // Clear server filename if file is cleared
        // Optionally reset preview if no file selected
        // imagePreview.style.display = 'none';
        // imagePreviewPlaceholder.style.display = 'block';
    }
}

// --- Chat/Prompt ---
function handlePromptSubmit(event) {
    event.preventDefault();
    const promptValue = promptInput.value.trim();
    if (!promptValue) {
        alert("Please enter a prompt.");
        return;
    }
    // Fetch recommendations with this prompt (and current image context if any)
    fetchRecommendations(promptValue, null); // Pass null for imageFile to indicate prompt-only (or prompt + existing image)
}

function populateExamplePrompts() {
    const examples = [
        "show me something in red",
        "more formal options",
        "casual summer wear",
        "matching accessories for a blue dress",
    ];
    examples.forEach(ex => {
        const li = document.createElement('li');
        li.textContent = ex;
        li.setAttribute('role', 'button');
        li.tabIndex = 0;
        li.addEventListener('click', () => {
            promptInput.value = ex;
            clearPromptBtn.style.display = 'inline-block';
            fetchRecommendations(ex, null); // Fetch immediately on click
        });
        li.addEventListener('keydown', (e) => e.key === 'Enter' && li.click());
        examplePromptsList.appendChild(li);
    });
}

// --- Wishlist ---
function updateWishlistDisplay() {
    wishlistItemsList.innerHTML = '';
    if (wishlistItems.length === 0) {
        emptyWishlistMessage.style.display = 'block';
    } else {
        emptyWishlistMessage.style.display = 'none';
        wishlistItems.forEach(item => {
            const li = document.createElement('li');
            li.className = 'wishlist-item';
            li.innerHTML = `
                <img src="${item.imageUrl}" alt="${item.name}" class="wishlist-item-image">
                <div class="wishlist-item-details">
                    <span class="wishlist-item-name">${item.name}</span>
                    <span class="wishlist-item-price">${item.price}</span>
                </div>
                <button class="wishlist-item-remove-btn btn-icon-subtle danger" data-product-id="${item.id}" title="Remove ${item.name} from wishlist">
                    <span class="icon-placeholder-small">🗑️</span>
                </button>
            `;
            // Make item clickable to open modal
            li.querySelector('.wishlist-item-image').addEventListener('click', () => handleProductCardClick(item.id));
            li.querySelector('.wishlist-item-details').addEventListener('click', () => handleProductCardClick(item.id));

            li.querySelector('.wishlist-item-remove-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                toggleWishlist(item.id);
            });
            wishlistItemsList.appendChild(li);
        });
    }
    wishlistCount.textContent = wishlistItems.length;
    // Re-render product cards in main display to reflect wishlist status
    displayRecommendations(currentRecommendations); 
    // If modal is open, update its wishlist button
    if (detailedProductToShow) updateModalButtons(detailedProductToShow.id);
}

function toggleWishlist(productId) {
    const productIndex = wishlistItems.findIndex(item => item.id === productId);
    if (productIndex > -1) {
        wishlistItems.splice(productIndex, 1);
    } else {
        const product = findProductById(productId);
        if (product) wishlistItems.push(product);
    }
    updateWishlistDisplay();
}


// --- Cart ---
function updateCartDisplay() {
    cartItemsList.innerHTML = '';
    if (cartItems.length === 0) {
        emptyCartMessage.style.display = 'block';
        cartContents.style.display = 'none';
        proceedToCheckoutBtn.disabled = true;
    } else {
        emptyCartMessage.style.display = 'none';
        cartContents.style.display = 'block';
        proceedToCheckoutBtn.disabled = false;
        let currentTotal = 0;
        cartItems.forEach(item => {
            const price = parseFloat(item.price.replace('$', ''));
            if (!isNaN(price)) currentTotal += price;

            const li = document.createElement('li');
            li.className = 'cart-item';
            li.innerHTML = `
                <img src="${item.imageUrl}" alt="${item.name}" class="cart-item-image">
                <div class="cart-item-details">
                    <span class="cart-item-name">${item.name}</span>
                    <span class="cart-item-price">${item.price}</span>
                </div>
                <button class="cart-item-remove-btn btn-icon-subtle danger" data-product-id="${item.id}" title="Remove ${item.name} from cart">
                     <span class="icon-placeholder-small">🗑️</span>
                </button>
            `;
            // Make item clickable to open modal
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
    }
    // Re-render product cards to reflect cart status
    displayRecommendations(currentRecommendations);
    // If modal is open, update its cart button
    if (detailedProductToShow) updateModalButtons(detailedProductToShow.id);
}

function toggleCart(productId) {
    const productIndex = cartItems.findIndex(item => item.id === productId);
    const product = findProductById(productId); // Get full product details
    if (productIndex > -1) {
        cartItems.splice(productIndex, 1);
    } else {
        if (product) cartItems.push(product);
    }
    updateCartDisplay();
}

// --- Product Modal ---
function findProductById(productId) {
    // Search in current recommendations, then wishlist, then cart
    return currentRecommendations.find(p => p.id === productId) ||
           wishlistItems.find(p => p.id === productId) ||
           cartItems.find(p => p.id === productId) ||
           (detailedProductToShow && detailedProductToShow.id === productId ? detailedProductToShow : null);
}

function updateModalButtons(productId) {
    const isInCart = cartItems.some(item => item.id === productId);
    const isInWishlist = wishlistItems.some(item => item.id === productId);

    modalWishlistBtnText.textContent = isInWishlist ? 'Remove from Wishlist' : 'Add to Wishlist';
    modalToggleWishlistBtn.querySelector('.icon-placeholder-small').textContent = isInWishlist ? '💖' : '❤️'; // Example with different hearts
    
    modalCartBtnText.textContent = isInCart ? 'Remove from Cart' : 'Add to Cart';
    modalToggleCartBtn.className = isInCart ? 'remove-from-cart-btn' : 'add-to-cart-btn'; // Dynamic class for styling
    modalToggleCartBtn.querySelector('.icon-placeholder-small').textContent = isInCart ? '➖' : '➕';
}


function handleProductCardClick(productId) {
    const product = findProductById(productId);
    if (!product) {
        console.error("Product not found for modal:", productId);
        return;
    }
    detailedProductToShow = product; // Store the product

    modalMainImage.src = product.images && product.images.length > 0 ? product.images[0] : product.imageUrl;
    modalProductName.textContent = product.name;
    modalProductPrice.textContent = product.price;
    modalProductDescription.textContent = product.description || "No description available.";

    // Attributes (sizes, colors)
    modalProductAttributes.innerHTML = '';
    if (product.sizes && product.sizes.length > 0) {
        const p = document.createElement('p');
        p.innerHTML = `<strong>Sizes:</strong> ${product.sizes.join(', ')}`;
        modalProductAttributes.appendChild(p);
    }
    if (product.colors && product.colors.length > 0) {
        const p = document.createElement('p');
        p.innerHTML = `<strong>Colors:</strong> ${product.colors.join(', ')}`;
        modalProductAttributes.appendChild(p);
    }
    
    // Recommendation Reason
    if (product.recommendationReason || (product.detailedReasons && product.detailedReasons.length > 0)) {
        modalRecommendationReason.style.display = 'block';
        modalReasonText.textContent = product.recommendationReason || "See details below.";
        modalDetailedReasonsList.innerHTML = '';
        if (product.detailedReasons && product.detailedReasons.length > 0) {
            product.detailedReasons.forEach(reason => {
                const li = document.createElement('li');
                li.textContent = reason;
                modalDetailedReasonsList.appendChild(li);
            });
        }
    } else {
        modalRecommendationReason.style.display = 'none';
    }


    // Thumbnails (if product.images is an array of multiple images)
    modalThumbnails.innerHTML = '';
    if (product.images && product.images.length > 1) {
        product.images.forEach((imgUrl, index) => {
            const thumb = document.createElement('img');
            thumb.src = imgUrl;
            thumb.alt = `Thumbnail ${index + 1}`;
            thumb.classList.add(index === 0 ? 'active-thumbnail' : ''); // Mark first as active
            thumb.addEventListener('click', () => {
                modalMainImage.src = imgUrl;
                modalThumbnails.querySelectorAll('img').forEach(t => t.classList.remove('active-thumbnail'));
                thumb.classList.add('active-thumbnail');
            });
            modalThumbnails.appendChild(thumb);
        });
    }
    
    updateModalButtons(productId);
    productModalOverlay.style.display = 'flex';
}

function closeModal() {
    productModalOverlay.style.display = 'none';
    detailedProductToShow = null;
}

// --- Checkout ---
async function handleCheckout() {
    if (cartItems.length === 0) {
        alert("Your cart is empty.");
        return;
    }
    const payload = { cartItems: cartItems.map(item => ({id: item.id, name: item.name, price: item.price })) }; // Send minimal data
    const result = await fetchApi('/mock_checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (result && result.message) {
        alert(result.message);
        // Optionally clear cart after successful mock checkout
        // cartItems = [];
        // updateCartDisplay();
    } else {
        alert("Checkout failed. Please try again.");
    }
}


// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    applyDarkMode(); // Apply on load
    updateIconPlaceholders(); // Update icon placeholders
    document.getElementById('currentYear').textContent = new Date().getFullYear();
    
    // Load initial recommendations passed from server
    if (typeof initialRecommendationsFromServer !== 'undefined' && initialRecommendationsFromServer.length > 0) {
        displayRecommendations(initialRecommendationsFromServer);
    } else {
        // Fallback or display initial message if no server-side recs
        initialMessage.style.display = 'block';
    }

    populateExamplePrompts();

    darkModeToggle.addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        applyDarkMode();
    });

    imageFileInput.addEventListener('change', handleImageUpload);
    promptForm.addEventListener('submit', handlePromptSubmit);

    promptInput.addEventListener('input', () => {
        clearPromptBtn.style.display = promptInput.value ? 'inline-block' : 'none';
    });
    clearPromptBtn.addEventListener('click', () => {
        promptInput.value = '';
        clearPromptBtn.style.display = 'none';
        // Optionally, if clearing prompt should reset to initial state or fetch generic recs:
        // uploadedFile = null; // Clear file context too if needed
        // uploadedFileNameServer = null;
        // imagePreview.style.display = 'none';
        // imagePreviewPlaceholder.style.display = 'block';
        // fetchRecommendations('', null); // Fetch initial/generic recs
    });

    productModalCloseBtn.addEventListener('click', closeModal);
    productModalOverlay.addEventListener('click', (event) => { // Close if overlay is clicked
        if (event.target === productModalOverlay) {
            closeModal();
        }
    });
    
    // Modal action buttons
    modalToggleWishlistBtn.addEventListener('click', () => {
        if (detailedProductToShow) {
            toggleWishlist(detailedProductToShow.id);
            // updateModalButtons(detailedProductToShow.id); // toggleWishlist calls updateWishlistDisplay which calls this
        }
    });
    modalToggleCartBtn.addEventListener('click', () => {
        if (detailedProductToShow) {
            toggleCart(detailedProductToShow.id);
            // updateModalButtons(detailedProductToShow.id); // toggleCart calls updateCartDisplay which calls this
             if (!cartItems.some(item => item.id === detailedProductToShow.id)) { // If item was removed
                // Do nothing specific here, or close modal if desired
             } else { // If item was added
                closeModal(); // Close modal after adding to cart
             }
        }
    });

    proceedToCheckoutBtn.addEventListener('click', handleCheckout);
});