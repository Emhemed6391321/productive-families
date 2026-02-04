'use client';
import { useEffect, useState } from 'react';
import Image from "next/image";
import Link from "next/link";
import { AdminService } from "../services/api";

export default function Home() {
  const [featuredAds, setFeaturedAds] = useState<any[]>([]);

  useEffect(() => {
    fetchAds();
  }, []);

  const fetchAds = async () => {
    try {
      const data = await AdminService.getFeaturedAds();
      setFeaturedAds(data);
    } catch (error) {
      console.error("Failed to fetch ads", error);
    }
  };

  return (
    <div className="min-h-screen bg-warm-cream font-sans" dir="rtl">
      {/* Navbar */}
      <header className="bg-white/90 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-accent/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-3xl font-bold text-primary tracking-tight">الأسر المنتجة</Link>
          <nav className="hidden md:flex space-x-8 space-x-reverse">
            <Link href="/" className="text-charcoal hover:text-primary transition font-medium">الرئيسية</Link>
            <Link href="/products" className="text-charcoal hover:text-primary transition font-medium">المنتجات</Link>
            <Link href="#categories" className="text-charcoal hover:text-primary transition font-medium">الأقسام</Link>
            <Link href="#contact" className="text-charcoal hover:text-primary transition font-medium">تواصل معنا</Link>
          </nav>
          <div className="flex gap-4">
            <Link href="/admin/login" className="bg-secondary text-white px-5 py-2.5 rounded-full text-sm font-bold hover:bg-secondary/90 transition shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
              دخول الأسر
            </Link>
            <Link href="/register/family" className="bg-primary text-white px-5 py-2.5 rounded-full text-sm font-bold hover:bg-primary-hover transition shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
              سجل مجاناً
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-secondary text-white py-24 overflow-hidden">
        <div className="absolute inset-0 bg-[url('/pattern-bg.png')] opacity-10"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl -mr-20 -mt-20"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl -ml-20 -mb-20"></div>

        <div className="container mx-auto px-4 text-center relative z-10">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-fade-in-up leading-tight">
            طعم الأصالة <span className="text-accent">بأيدي سعودية</span>
          </h1>
          <p className="text-xl md:text-2xl mb-10 text-accent/90 max-w-2xl mx-auto leading-relaxed">
            منصة تجمع لك أشهى المأكولات وأروع الحرف اليدوية من الأسر المنتجة المبدعة في مكان واحد.
          </p>
          <div className="flex justify-center gap-4 animate-fade-in-up delay-200">
            <Link
              href="/products"
              className="bg-primary text-white px-10 py-4 rounded-full font-bold text-lg shadow-xl hover:bg-primary-hover transform hover:-translate-y-1 transition border-2 border-primary"
            >
              تصفح المنتجات
            </Link>
            <Link
              href="/register/family"
              className="bg-transparent text-white px-10 py-4 rounded-full font-bold text-lg shadow-xl hover:bg-white/10 transform hover:-translate-y-1 transition border-2 border-white/30 backdrop-blur-sm"
            >
              ابدأ البيع معنا
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Ads Section */}
      {featuredAds.length > 0 && (
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-primary mb-2">متاجر مميزة</h2>
              <div className="h-1 w-20 bg-secondary mx-auto rounded-full"></div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {featuredAds.map((ad) => (
                <div key={ad.id} className="group relative rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 cursor-pointer">
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-10 opacity-90 group-hover:opacity-100 transition"></div>
                  {/* Fallback image or actual banner if available */}
                  <div className="h-64 bg-gray-200 w-full relative">
                    {/* <Image src={ad.family.banner_url || '/placeholder.jpg'} fill className="object-cover" alt={ad.family.business_name} /> */}
                    <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400">
                      {/* Placeholder for now */}
                      <span className="text-4xl">🏪</span>
                    </div>
                  </div>
                  <div className="absolute bottom-0 right-0 p-6 z-20 text-white transform translate-y-2 group-hover:translate-y-0 transition duration-300">
                    <h3 className="text-2xl font-bold mb-2">{ad.family.business_name}</h3>
                    <p className="text-gray-200 text-sm line-clamp-2 mb-4">{ad.family.description}</p>
                    <Link href={`/products?family=${ad.family.id}`} className="inline-block bg-primary px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary-hover transition">
                      زيارة المتجر ←
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Categories Section */}
      <section id="categories" className="py-20 bg-warm-cream relative">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {['مأكولات شعبية', 'حلويات ومعجنات', 'حرف يدوية', 'أزياء وتطريز'].map((cat, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl shadow-sm hover:shadow-lg transition text-center border border-accent/50 cursor-pointer group">
                <div className="w-16 h-16 bg-warm-cream rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary group-hover:text-white transition duration-300">
                  <span className="text-2xl">🍽️</span>
                </div>
                <h3 className="font-bold text-charcoal group-hover:text-primary transition">{cat}</h3>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-charcoal text-white py-12 border-t-4 border-secondary">
        <div className="container mx-auto px-4 text-center">
          <p className="text-accent/60">جميع الحقوق محفوظة &copy; 2024 منصة الأسر المنتجة</p>
        </div>
      </footer>
    </div>
  );
}
