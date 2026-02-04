'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useCart } from '../../../context/CartContext';

export default function ProductDetailsPage({ params }: { params: { id: string } }) {
    const { addToCart } = useCart();
    const [product, setProduct] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                // Fetching all products as a temporary solution until single product endpoint is robust
                const response = await fetch('http://localhost:3000/api/shop/products');
                const products = await response.json();
                const found = products.find((p: any) => p.id == params.id);
                setProduct(found);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        if (params.id) fetchProduct();
    }, [params.id]);

    if (loading) return <div className="min-h-screen flex items-center justify-center">جاري التحميل...</div>;
    if (!product) return <div className="min-h-screen flex items-center justify-center">المنتج غير موجود</div>;

    return (
        <div className="min-h-screen bg-gray-50" dir="rtl">
            <header className="bg-white shadow-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Link href="/" className="text-2xl font-bold text-green-700">الأسر المنتجة</Link>
                    </div>
                    <Link href="/products" className="text-gray-500 hover:text-green-600">عودة للمنتجات</Link>
                </div>
            </header>

            <main className="container mx-auto px-4 py-12">
                <div className="bg-white rounded-2xl shadow-lg overflow-hidden grid grid-cols-1 md:grid-cols-2">
                    <div className="bg-warm-cream h-[400px] md:h-auto relative">
                        {product.image_url ? (
                            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-accent">
                                <span className="text-6xl">📦</span>
                            </div>
                        )}
                    </div>
                    <div className="p-8 md:p-12 flex flex-col justify-center">
                        <div className="mb-4">
                            <span className="bg-accent/20 text-secondary px-3 py-1 rounded-full text-sm font-bold border border-secondary/20">
                                {product.family?.business_name || 'أسرة منتجة'}
                            </span>
                        </div>
                        <h1 className="text-4xl font-bold text-charcoal mb-4">{product.name}</h1>
                        <p className="text-gray-500 text-lg mb-8 leading-relaxed">
                            {product.description || 'لا يوجد وصف متاح لهذا المنتج.'}
                        </p>

                        <div className="flex items-center justify-between border-t border-accent/20 pt-8">
                            <div>
                                <p className="text-gray-400 text-sm">السعر</p>
                                <p className="text-3xl font-bold text-primary">{product.price} ر.س</p>
                            </div>
                            <button
                                onClick={() => addToCart(product, 1)}
                                className="bg-primary text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-primary-hover transition shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                            >
                                أضف للسلة
                            </button>
                        </div>
                        <div className="mt-6 flex items-center gap-4 text-secondary text-sm font-medium">
                            <span className="flex items-center gap-1">⏱️ {product.preparation_time_minutes || 30} دقيقة</span>
                            <span className="flex items-center gap-1">⭐ 4.8 تقييم</span>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
