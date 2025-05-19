import { useState, useEffect, useCallback } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import RecommendationDisplay from './components/RecommendationDisplay';
import ProductModal from './components/ProductModal';
import type { ProductDetail } from './components/ProductModal'; // Will now include detailedReasons
import ChatInput from './components/ChatInput';
import Checkout from './components/Checkout';
import WishlistDisplay from './components/WishlistDisplay';
import { Bot, Moon, Sun } from 'lucide-react';

// Updated generateMockProducts
const generateMockProducts = (context: 'initial' | 'image' | 'prompt', promptText?: string, baseImageName?: string): ProductDetail[] => {
    const baseProductTemplates: Omit<ProductDetail, 'id' | 'name' | 'imageUrl' | 'recommendationReason' | 'detailedReasons' | 'isInCart' | 'isInWishlist'>[] = [
        { price: '$49.99', type: 'similar', description: 'A comfortable and stylish item, perfect for daily wear.', images: [`https://via.placeholder.com/400x450/A7C7E7/333?Text=ComfyV1`, `https://via.placeholder.com/400x450/B1D8B7/333?Text=ComfyV2`], sizes: ['S', 'M', 'L', 'XL'], colors: ['Sky Blue', 'Mint Green', 'Black'] },
        { price: '$79.50', type: 'complementary', description: 'High-quality accessory to complete your look.', images: [`https://via.placeholder.com/400x450/F8C8DC/333?Text=AccV1`], sizes: ['One Size'], colors: ['Rose Gold', 'Silver'] },
        { price: '$120.00', type: 'similar', description: 'Premium quality product with a unique design.', images: [`https://via.placeholder.com/400x450/C4A484/333?Text=PremiumV1`, `https://via.placeholder.com/400x450/A0A0A0/333?Text=PremiumV2`], sizes: ['M', 'L'], colors: ['Mocha', 'Charcoal Gray'] },
        { price: '$35.00', type: 'similar', description: 'A basic essential for any wardrobe.', images: [`https://via.placeholder.com/400x450/E6E6FA/333?Text=BasicV1`], sizes: ['S', 'M', 'L'], colors: ['Lavender', 'White'] },
        { price: '$89.00', type: 'complementary', description: 'Elegant and versatile, perfect for any occasion.', images: [`https://via.placeholder.com/400x450/FFDAB9/333?Text=ElegantV1`], sizes: ['S', 'M'], colors: ['Peach', 'Cream'] },
        { price: '$65.00', type: 'similar', description: 'Sporty and functional for an active lifestyle.', images: [`https://via.placeholder.com/400x450/77DD77/333?Text=SportyV1`, `https://via.placeholder.com/400x450/8ECDDD/333?Text=SportyV2`], sizes: ['M', 'L', 'XL'], colors: ['Pastel Green', 'Light Blue'] },
    ];
    let specificProducts: ProductDetail[] = [];
    const pText = promptText?.toLowerCase() || "";
    const numToGenerate = 8 + Math.floor(Math.random() * 5);

    const mockDetailedReasonsPool = [
        ["Matches color 'Red'", "Category: Dress", "Style: Casual"],
        ["Pairs with 'Blue Jeans'", "Accessory Type: Belt", "Material: Leather"],
        ["Similar pattern detected", "Brand vibe: Sporty", "Feature: Breathable fabric"],
        ["Vibe: Minimalist", "Color family: Neutrals", "Often bought with: White Sneakers"],
        ["Texture: Smooth Silk", "Occasion: Formal Event", "Complements: Silver Jewelry"]
    ];

    for (let i = 0; i < numToGenerate; i++) {
        const template = baseProductTemplates[i % baseProductTemplates.length];
        let name = `Item ${context.charAt(0).toUpperCase()}${i + 1}`;
        let reason = `Recommended for you.`;
        let imgText = `Item${i + 1}`;
        const detailedReasons = mockDetailedReasonsPool[i % mockDetailedReasonsPool.length];

        if (context === 'initial') { 
            name = `Featured Style ${i + 1}`; 
            reason = `Popular with our shoppers.`; 
            imgText = `Featured${i+1}`; 
        } else if (context === 'image') { 
            name = `Match for ${baseImageName ? baseImageName.substring(0,8) : 'Upload'} #${i + 1}`; 
            reason = `Visually similar to your image${pText ? ` and prompt "${pText.substring(0,10)}..."` : ''}.`; 
            imgText = `ImgMatch${i+1}`; 
        } else if (context === 'prompt') { 
            name = `For "${pText.substring(0,10)}..." #${i + 1}`; 
            reason = `Based on your prompt: "${pText}"`; 
            imgText = `Prompt${i+1}`; 
        }
        specificProducts.push({ 
            ...template, 
            id: `${context}_${i + 1}_${Date.now() % 10000}_${Math.random().toString(36).substr(2, 5)}`, 
            name: name, 
            imageUrl: `https://via.placeholder.com/260x250/${(Math.random()*0xFFFFFF<<0).toString(16).padStart(6, '0')}/FFF?Text=${imgText}`, 
            recommendationReason: reason, 
            detailedReasons: detailedReasons, // Add detailed reasons
            isInCart: false, 
            isInWishlist: false 
        });
    }
    return specificProducts;
};

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : false;
  });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [recommendationsData, setRecommendationsData] = useState<ProductDetail[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [initialRecommendationsFetched, setInitialRecommendationsFetched] = useState(false);
  const [currentSearchType, setCurrentSearchType] = useState<'initial' | 'image' | 'prompt'>('initial');
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [cartItems, setCartItems] = useState<ProductDetail[]>([]);
  const [wishlistItems, setWishlistItems] = useState<ProductDetail[]>([]);
  const [detailedProductToShow, setDetailedProductToShow] = useState<ProductDetail | null>(null);
  const [lastAddedToCartId, setLastAddedToCartId] = useState<string | null>(null);

  const cartItemCount = cartItems.length;

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(prevMode => !prevMode);
  };

  const fetchRecs = useCallback(async (file: File | null, prompt: string, searchContext: 'initial' | 'image' | 'prompt') => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
      const newMockProducts = generateMockProducts(searchContext, prompt, file?.name);
      setRecommendationsData(newMockProducts);
    } catch (error) { console.error('Error fetching recommendations:', error); setRecommendationsData([]); }
    finally { setIsLoading(false); }
  }, []);

  useEffect(() => {
    if (!initialRecommendationsFetched && !uploadedFile) {
      fetchRecs(null, '', 'initial').then(() => {
        setInitialRecommendationsFetched(true);
        setCurrentSearchType('initial');
      });
    }
  }, [initialRecommendationsFetched, uploadedFile, fetchRecs]);

  const handleProductCardClick = (product: ProductDetail) => {
    console.log('[App.tsx] handleProductCardClick called for:', product.name);
    setDetailedProductToShow(product);
  };
  
  const handleCloseModal = () => {
    setDetailedProductToShow(null);
    setLastAddedToCartId(null);
  }

  const handleToggleCart = (productToToggle: ProductDetail) => {
    setCartItems(prevCartItems => {
      const existingItemIndex = prevCartItems.findIndex(item => item.id === productToToggle.id);
      if (existingItemIndex > -1) {
        console.log(`${productToToggle.name} removed from cart.`);
        if (lastAddedToCartId === productToToggle.id) {
            setLastAddedToCartId(null);
        }
        return prevCartItems.filter((_, index) => index !== existingItemIndex);
      } else {
        console.log(`${productToToggle.name} added to cart.`);
        setLastAddedToCartId(productToToggle.id);
        return [...prevCartItems, productToToggle];
      }
    });
  };

  useEffect(() => {
    if (lastAddedToCartId && detailedProductToShow && detailedProductToShow.id === lastAddedToCartId) {
      handleCloseModal();
    }
  }, [lastAddedToCartId, detailedProductToShow]); 

  const handleToggleWishlist = (productToToggle: ProductDetail) => {
    setWishlistItems(prevWishlistItems => {
      const existingItemIndex = prevWishlistItems.findIndex(item => item.id === productToToggle.id);
      if (existingItemIndex > -1) {
        return prevWishlistItems.filter((_, index) => index !== existingItemIndex);
      } else {
        return [...prevWishlistItems, productToToggle];
      }
    });
  };
  
  const handleToggleWishlistOnCard = (productId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    const product = recommendationsData.find(p => p.id === productId) || 
                    cartItems.find(p => p.id === productId) || 
                    wishlistItems.find(p => p.id === productId) ||
                    (detailedProductToShow?.id === productId ? detailedProductToShow : null);
    if (product) {
        handleToggleWishlist(product);
    } else {
        console.warn("Could not find product to toggle wishlist on card:", productId);
    }
  };

  const handleRemoveFromCartInCheckout = (productIdToRemove: string) => {
    setCartItems(prevCartItems => prevCartItems.filter(item => item.id !== productIdToRemove));
  };
  
  const handleRemoveFromWishlistInDisplay = (productIdToRemove: string) => {
    setWishlistItems(prevWishlistItems => prevWishlistItems.filter(item => item.id !== productIdToRemove));
  };

  const handleImageUpload = (file: File) => {
    setUploadedFile(file); setCurrentSearchType('image');
    const newPrompt = currentPrompt || "items similar to this image";
    fetchRecs(file, newPrompt, 'image');
  };

  const handlePromptSubmit = async (promptValue: string) => {
    if (!promptValue.trim()) { alert("Please enter a prompt."); return; }
    setCurrentPrompt(promptValue); setCurrentSearchType('prompt');
    await fetchRecs(uploadedFile, promptValue, uploadedFile ? 'image' : 'prompt');
  };
  
  const handleCheckout = () => {
    if (cartItemCount === 0) { alert("Your cart is empty."); return; }
    let summary = `Checkout for ${cartItemCount} item(s):\n`; 
    cartItems.forEach(item => { summary += `- ${item.name} (${item.price})\n`; });
    console.log(summary); alert(summary + "\n(This is a demo checkout)");
  };
  
  const recommendationsWithStatus = recommendationsData.map(rec => ({
    ...rec,
    isInCart: cartItems.some(cartItem => cartItem.id === rec.id),
    isInWishlist: wishlistItems.some(wishlistItem => wishlistItem.id === rec.id)
  }));
  const showInitialMessage = !isLoading && !uploadedFile && recommendationsData.length === 0 && !initialRecommendationsFetched;

  return (
    <div className="app-container"> 
      <header>
        <h1><Bot size={30} />ShopSmarter AI Assistant</h1>
        <button onClick={toggleDarkMode} className="dark-mode-toggle" title="Toggle Dark Mode">
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>
      <main className="main-content">
        <div className="top-interaction-area">
          <ImageUpload onImageUpload={handleImageUpload} />
          <ChatInput onPromptSubmit={handlePromptSubmit} disabled={isLoading} initialPrompt={currentPrompt} />
        </div>
        
        {isLoading && <p className="loading-text">Searching for perfect matches...</p>}
        {!isLoading && recommendationsData.length === 0 && (currentSearchType !== 'initial' || initialRecommendationsFetched) && (
          <div className="no-recommendations-text"><p>No recommendations found. Try another search!</p></div>
        )}
        {showInitialMessage && (
          <div className="no-recommendations-text"><p>Upload an image or use a prompt. Initial suggestions are loading...</p></div>
        )}

        {!isLoading && recommendationsData.length > 0 && (
          <RecommendationDisplay 
            products={recommendationsWithStatus} 
            onProductClick={handleProductCardClick}
            onToggleWishlistOnCard={handleToggleWishlistOnCard} 
          />
        )}

        <WishlistDisplay 
            wishlistItems={wishlistItems.map(item => ({...item, isInCart: cartItems.some(ci => ci.id === item.id)}))}
            onRemoveFromWishlist={handleRemoveFromWishlistInDisplay}
            onProductClick={handleProductCardClick}
        />

        <Checkout 
            onCheckout={handleCheckout} 
            cartItems={cartItems} 
            onRemoveItem={handleRemoveFromCartInCheckout}
            onProductClick={handleProductCardClick} 
        />
      </main>
      {detailedProductToShow && (
        <ProductModal 
          product={{ 
            ...detailedProductToShow, 
            isInCart: cartItems.some(ci => ci.id === detailedProductToShow.id),
            isInWishlist: wishlistItems.some(wi => wi.id === detailedProductToShow.id)
          }} 
          onClose={handleCloseModal}
          onToggleCart={handleToggleCart}
          onToggleWishlist={handleToggleWishlist}
        />
      )}
      <footer><p>© {new Date().getFullYear()} ShopSmarter AI. All rights reserved.</p></footer>
    </div>
  );
}
export default App;
