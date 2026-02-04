'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { AdminService } from '../../services/api';

export default function ProductsPage() {
    const [products, setProducts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                // In a real scenario you might want a separate public API or filtered list
                // For now, re-using AdminService.getProducts() which calls /shop/products
                const data = await AdminService.getProducts();
                setProducts(data);
            } catch (error) {
                console.error('Error fetching products:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    return (
        <div className="min-h-screen bg-warm-cream" dir="rtl">
            <header className="bg-white/90 backdrop-blur-md shadow-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Link href="/" className="text-2xl font-bold text-primary">الأسر المنتجة</Link>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                <h1 className="text-3xl font-bold text-charcoal mb-8">تسوق منتجات الأسر</h1>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {products.map((product) => (
                            <Link href={`/products/${product.id}`} key={product.id} className="group">
                                <div className="bg-white rounded-xl shadow-sm hover:shadow-xl transition duration-300 overflow-hidden border border-accent/30 h-full flex flex-col">
                                    <div className="relative h-48 bg-gray-200">
                                        {/* Placeholder for Product Image */}
                                        {product.image_url ? (
                                            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover group-hover:scale-105 transition duration-500" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                                                <span className="text-4xl">📦</span>
                                            </div>
                                        )}
                                    </div>
                                    <div className="p-4 flex flex-col flex-1">
                                        <h2 className="font-bold text-lg text-charcoal mb-1 group-hover:text-primary transition">{product.name}</h2>
                                        <p className="text-sm text-gray-500 mb-3">{product.family?.business_name || 'أسرة منتجة'}</p>
                                        <div className="mt-auto flex justify-between items-center">
                                            <span className="text-primary font-bold text-lg">{product.price} ر.س</span>
                                            <span className="text-xs bg-warm-cream text-secondary font-bold px-2 py-1 rounded-full border border-secondary/20">
                                                {product.preparation_time_minutes ? `${product.preparation_time_minutes} دقيقة` : 'جاهز'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        ))}
                        {products.length === 0 && (
                            <div className="col-span-full text-center py-20 text-gray-500">
                                لا توجد منتجات متاحة حالياً.
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
