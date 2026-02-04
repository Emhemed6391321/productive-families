'use client';
import { useCart } from '../context/CartContext';
import Link from 'next/link';
import Image from 'next/image';

export default function CartSidebar() {
    const { items, removeFromCart, totalAmount, isOpen, toggleCart } = useCart();

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex justify-end">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 transition-opacity"
                onClick={toggleCart}
            ></div>

            {/* Sidebar */}
            <div className="relative w-full max-w-md bg-white h-full shadow-2xl flex flex-col animate-slide-in-right">
                <div className="p-4 border-b flex justify-between items-center bg-warm-cream border-accent/20">
                    <h2 className="text-xl font-bold text-charcoal">سلة المشتريات ({items.length})</h2>
                    <button
                        onClick={toggleCart}
                        className="p-2 hover:bg-accent/20 rounded-full transition text-charcoal"
                    >
                        ✕
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {items.length === 0 ? (
                        <div className="text-center py-20 text-gray-500">
                            <span className="text-6xl block mb-4">🛒</span>
                            <p>السلة فارغة</p>
                            <button
                                onClick={toggleCart}
                                className="mt-4 text-primary font-bold hover:underline"
                            >
                                تصفح المنتجات
                            </button>
                        </div>
                    ) : (
                        items.map((item) => (
                            <div key={item.product.id} className="flex gap-4 bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
                                <div className="w-20 h-20 bg-gray-100 rounded-md relative overflow-hidden flex-shrink-0">
                                    {item.product.image_url ? (
                                        <img src={item.product.image_url} alt={item.product.name} className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-gray-400">📦</div>
                                    )}
                                </div>
                                <div className="flex-1 flex flex-col justify-between">
                                    <div>
                                        <h3 className="font-bold text-charcoal line-clamp-1">{item.product.name}</h3>
                                        <p className="text-sm text-secondary font-medium">{item.product.family?.business_name}</p>
                                    </div>
                                    <div className="flex justify-between items-end">
                                        <span className="font-bold text-primary">{item.product.price} ر.س × {item.quantity}</span>
                                        <button
                                            onClick={() => removeFromCart(item.product.id)}
                                            className="text-red-500 text-sm hover:underline"
                                        >
                                            حذف
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {items.length > 0 && (
                    <div className="p-4 border-t bg-warm-cream border-accent/20">
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-charcoal font-medium">المجموع الكلي:</span>
                            <span className="text-2xl font-bold text-primary">{totalAmount.toFixed(2)} ر.س</span>
                        </div>
                        <Link
                            href="/checkout"
                            onClick={toggleCart}
                            className="block w-full bg-primary text-white text-center py-4 rounded-xl font-bold text-lg hover:bg-primary-hover transition shadow-lg"
                        >
                            إتمام الطلب
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
}
