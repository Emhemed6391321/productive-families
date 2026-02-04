'use client';
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type CartItem = {
    product: any;
    quantity: number;
    familyId: number;
};

type CartContextType = {
    items: CartItem[];
    addToCart: (product: any, quantity: number) => void;
    removeFromCart: (productId: number) => void;
    clearCart: () => void;
    totalAmount: number;
    itemCount: number;
    isOpen: boolean;
    toggleCart: () => void;
};

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
    const [items, setItems] = useState<CartItem[]>([]);
    const [isOpen, setIsOpen] = useState(false);

    // Load from localStorage on mount
    useEffect(() => {
        const savedCart = localStorage.getItem('cart');
        if (savedCart) {
            try {
                setItems(JSON.parse(savedCart));
            } catch (e) {
                console.error("Failed to parse cart", e);
            }
        }
    }, []);

    // Save to localStorage on change
    useEffect(() => {
        localStorage.setItem('cart', JSON.stringify(items));
    }, [items]);

    const addToCart = (product: any, quantity: number) => {
        setItems(prev => {
            const existing = prev.find(item => item.product.id === product.id);
            if (existing) {
                return prev.map(item =>
                    item.product.id === product.id
                        ? { ...item, quantity: item.quantity + quantity }
                        : item
                );
            }
            return [...prev, { product, quantity, familyId: product.family?.id || product.family_id }];
        });
        setIsOpen(true); // Open cart when adding
    };

    const removeFromCart = (productId: number) => {
        setItems(prev => prev.filter(item => item.product.id !== productId));
    };

    const clearCart = () => {
        setItems([]);
    };

    const toggleCart = () => setIsOpen(prev => !prev);

    const totalAmount = items.reduce((sum, item) => sum + (Number(item.product.price) * item.quantity), 0);
    const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

    return (
        <CartContext.Provider value={{ items, addToCart, removeFromCart, clearCart, totalAmount, itemCount, isOpen, toggleCart }}>
            {children}
        </CartContext.Provider>
    );
}

export const useCart = () => {
    const context = useContext(CartContext);
    if (!context) throw new Error('useCart must be used within a CartProvider');
    return context;
};
