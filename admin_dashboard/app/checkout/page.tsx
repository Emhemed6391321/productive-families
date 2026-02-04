'use client';
import { useState } from 'react';
import { useCart } from '../../context/CartContext';
import { AdminService } from '../../services/api';
import { useRouter } from 'next/navigation';

export default function CheckoutPage() {
    const { items, totalAmount, clearCart } = useCart();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        address: '',
        phone: '',
        notes: ''
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (items.length === 0) return;

        setLoading(true);
        try {
            // Group items by family to create multiple orders if needed, or backend handles it?
            // For now, let's assume backend takes simple list and creates one order maybe?
            // The mobile app loops and creates one order per family? 
            // The mobile app ApiService.createOrder takes familyId and buyerId.
            // Complex scenario: Multiple families in cart? 
            // My CartContext allows mixed families.
            // Let's implement robust logic: One order per family.

            const itemsByFamily: Record<number, any[]> = {};
            items.forEach(item => {
                const famId = item.familyId;
                if (!itemsByFamily[famId]) itemsByFamily[famId] = [];
                itemsByFamily[famId].push({
                    product_id: item.product.id,
                    quantity: item.quantity
                });
            });

            // Create order for each family
            // Ideally should be a transaction but we will do loop for prototype
            const promises = Object.keys(itemsByFamily).map(async (familyId) => {
                await AdminService.createOrder({
                    buyer_id: 1, // Mock buyer ID
                    family_id: Number(familyId),
                    items: itemsByFamily[Number(familyId)],
                    delivery_address: `${formData.address} - Phone: ${formData.phone}`,
                    notes: formData.notes
                });
            });

            await Promise.all(promises);

            clearCart();
            alert('تم استلام طلبك بنجاح! سيتم التواصل معك قريباً.');
            router.push('/');
        } catch (error) {
            console.error(error);
            alert('حدث خطأ أثناء إتمام الطلب. يرجى المحاولة مرة أخرى.');
        } finally {
            setLoading(false);
        }
    };

    if (items.length === 0) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-warm-cream">
                <h1 className="text-3xl font-bold text-charcoal mb-4">سلة المشتريات فارغة</h1>
                <p className="text-gray-500 mb-8">أضف بعض المنتجات اللذيذة أولاً!</p>
                <button
                    onClick={() => router.push('/products')}
                    className="bg-primary text-white px-8 py-3 rounded-full font-bold hover:bg-primary-hover transition"
                >
                    تصفح المنتجات
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-warm-cream py-12" dir="rtl">
            <div className="container mx-auto px-4 max-w-4xl">
                <h1 className="text-3xl font-bold text-charcoal mb-8 border-b border-primary/20 pb-4">إتمام الطلب</h1>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Order Summary */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-accent/30 h-fit">
                        <h2 className="text-xl font-bold text-charcoal mb-6">ملخص الطلب</h2>
                        <div className="space-y-4 mb-6">
                            {items.map((item) => (
                                <div key={item.product.id} className="flex justify-between items-center text-sm">
                                    <span className="text-charcoal/80">
                                        <span className="font-bold">{item.quantity}x</span> {item.product.name}
                                    </span>
                                    <span className="font-bold text-secondary">
                                        {(Number(item.product.price) * item.quantity).toFixed(2)} ر.س
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div className="border-t border-gray-100 pt-4 flex justify-between items-center text-lg font-bold">
                            <span className="text-charcoal">الإجمالي</span>
                            <span className="text-primary">{totalAmount.toFixed(2)} ر.س</span>
                        </div>
                    </div>

                    {/* Checkout Form */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-accent/30">
                        <h2 className="text-xl font-bold text-charcoal mb-6">بيانات التوصيل</h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">الاسم الكامل</label>
                                <input
                                    type="text"
                                    name="name"
                                    required
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-primary outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">رقم الجوال</label>
                                <input
                                    type="tel"
                                    name="phone"
                                    required
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-primary outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">العنوان بالتفصيل</label>
                                <textarea
                                    name="address"
                                    required
                                    rows={3}
                                    value={formData.address}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-primary outline-none"
                                ></textarea>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات (اختياري)</label>
                                <textarea
                                    name="notes"
                                    rows={2}
                                    value={formData.notes}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-primary outline-none"
                                ></textarea>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-primary text-white font-bold py-4 rounded-xl hover:bg-primary-hover transition shadow-lg mt-4 disabled:bg-gray-400"
                            >
                                {loading ? 'جاري التنفيذ...' : `تأكيد الطلب (${totalAmount.toFixed(2)} ر.س)`}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
