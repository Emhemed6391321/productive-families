'use client';
import Link from 'next/link';
import { useCart } from '../context/CartContext';

export default function Header() {
    const { toggleCart, itemCount } = useCart();

    return (
        <header className="bg-white shadow-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                <div className="flex items-center gap-8">
                    <Link href="/" className="text-2xl font-bold text-primary">الأسر المنتجة</Link>
                    <nav className="hidden md:flex gap-6">
                        <Link href="/" className="text-charcoal hover:text-primary font-medium transition">الرئيسية</Link>
                        <Link href="/products" className="text-charcoal hover:text-primary font-medium transition">المنتجات</Link>
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={toggleCart}
                        className="relative p-2 text-charcoal hover:text-primary transition"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {itemCount > 0 && (
                            <span className="absolute top-0 right-0 bg-primary text-white text-xs font-bold w-5 h-5 flex items-center justify-center rounded-full">
                                {itemCount}
                            </span>
                        )}
                    </button>
                    <Link
                        href="/admin/login"
                        className="hidden md:block bg-secondary text-white px-4 py-2 rounded-full text-sm font-bold hover:bg-opacity-90 transition shadow-sm"
                    >
                        دخول الأسر
                    </Link>
                </div>
            </div>
        </header>
    );
}
