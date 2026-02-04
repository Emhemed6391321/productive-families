'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AdminService } from '../../../services/api';
import Link from 'next/link';

export default function FamilyRegistrationPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Combined form state
    const [formData, setFormData] = useState({
        // User Data
        full_name: '',
        email: '',
        password: '',
        phone_number: '',

        // Family Data
        business_name: '',
        description: '',
        min_order_amount: 0
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const value = e.target.type === 'number' ? Number(e.target.value) : e.target.value;
        setFormData({ ...formData, [e.target.name]: value });
    };

    const handleNext = (e: React.FormEvent) => {
        e.preventDefault();
        setStep(2);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Step 1: Register User
            const userResponse = await AdminService.registerUser({
                full_name: formData.full_name,
                email: formData.email,
                password: formData.password,
                phone_number: formData.phone_number,
                role: 'BUYER' // Will be upgraded by family creation
            });

            if (!userResponse || !userResponse.user) {
                throw new Error('فشل إنشاء حساب المستخدم');
            }

            // Step 2: Create Family Profile
            await AdminService.createFamily({
                user_id: userResponse.user.id,
                business_name: formData.business_name,
                description: formData.description,
                min_order_amount: formData.min_order_amount,
                delivery_fee: 0 // Free delivery or handled elsewhere
            });

            alert('تم تسجيل حسابك كأسرة منتجة بنجاح! يمكنك الآن تسجيل الدخول.');
            router.push('/admin/login');

        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.message || 'حدث خطأ أثناء التسجيل. حاول مرة أخرى.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-warm-cream bg-[url('/pattern-bg.png')] bg-repeat flex items-center justify-center p-4" dir="rtl">
            <div className="bg-white/95 backdrop-blur-sm p-8 rounded-3xl shadow-2xl w-full max-w-2xl border border-accent/40 relative overflow-hidden">
                {/* Decorative Elements */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full -mr-16 -mt-16 blur-2xl"></div>
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-primary/10 rounded-full -ml-16 -mb-16 blur-2xl"></div>

                <div className="relative text-center mb-10">
                    <h1 className="text-4xl font-bold text-primary mb-3">انضم لعائلة المنتجات</h1>
                    <p className="text-charcoal/70 text-lg">سجل الآن وابدأ رحلتك في بيع منتجاتك المميزة</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm text-center border border-red-100 mb-8 flex items-center justify-center gap-2">
                        <span>⚠️</span> {error}
                    </div>
                )}

                {/* Stepper */}
                <div className="flex justify-center mb-10 relative">
                    <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 rounded-full"></div>
                    <div
                        className={`absolute top-1/2 right-0 h-1 bg-primary -z-10 rounded-full transition-all duration-500`}
                        style={{ width: step === 1 ? '50%' : '100%' }}
                    ></div>

                    <div className="flex justify-between w-2/3">
                        <div className={`flex flex-col items-center gap-2 ${step >= 1 ? 'text-primary' : 'text-gray-400'}`}>
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg shadow-md transition-all ${step >= 1 ? 'bg-primary text-white scale-110' : 'bg-white border-2 border-gray-300'}`}>1</div>
                            <span className="text-sm font-bold">حسابك</span>
                        </div>
                        <div className={`flex flex-col items-center gap-2 ${step >= 2 ? 'text-primary' : 'text-gray-400'}`}>
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg shadow-md transition-all ${step >= 2 ? 'bg-primary text-white scale-110' : 'bg-white border-2 border-gray-300'}`}>2</div>
                            <span className="text-sm font-bold">متجرك</span>
                        </div>
                    </div>
                </div>

                {step === 1 ? (
                    <form onSubmit={handleNext} className="space-y-6 animate-fade-in relative">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-bold text-charcoal mb-2">الاسم الكامل</label>
                                <input
                                    type="text"
                                    name="full_name"
                                    required
                                    placeholder="مثال: محمد أحمد"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-charcoal mb-2">رقم الجوال</label>
                                <input
                                    type="tel"
                                    name="phone_number"
                                    required
                                    placeholder="05xxxxxxxx"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                    dir="ltr"
                                    className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm text-right"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-charcoal mb-2">البريد الإلكتروني</label>
                            <input
                                type="email"
                                name="email"
                                required
                                placeholder="name@example.com"
                                value={formData.email}
                                onChange={handleChange}
                                dir="ltr"
                                className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm text-right"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-charcoal mb-2">كلمة المرور</label>
                            <input
                                type="password"
                                name="password"
                                required
                                minLength={6}
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={handleChange}
                                dir="ltr"
                                className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm text-right"
                            />
                        </div>
                        <button
                            type="submit"
                            className="w-full bg-primary text-white font-bold py-4 rounded-xl hover:bg-primary-hover transition shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-2"
                        >
                            <span>متابعة</span>
                            <span>←</span>
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleSubmit} className="space-y-6 animate-fade-in relative">
                        <div>
                            <label className="block text-sm font-bold text-charcoal mb-2">اسم المتجر / الأسرة</label>
                            <input
                                type="text"
                                name="business_name"
                                required
                                placeholder="مثال: مطبخ أم خالد"
                                value={formData.business_name}
                                onChange={handleChange}
                                className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-charcoal mb-2">وصف النشاط</label>
                            <textarea
                                name="description"
                                required
                                rows={4}
                                placeholder="صف منتجاتك وما يميزها..."
                                value={formData.description}
                                onChange={handleChange}
                                className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm"
                            ></textarea>
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-charcoal mb-2">الحد الأدنى للطلب (ر.س)</label>
                            <input
                                type="number"
                                name="min_order_amount"
                                min={0}
                                value={formData.min_order_amount}
                                onChange={handleChange}
                                className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all shadow-sm"
                            />
                        </div>
                        {/* Delivery fee removed as requested */}

                        <div className="flex gap-4 mt-8">
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="w-1/3 bg-gray-100 text-gray-700 font-bold py-4 rounded-xl hover:bg-gray-200 transition"
                            >
                                رجوع
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-2/3 bg-primary text-white font-bold py-4 rounded-xl hover:bg-primary-hover transition shadow-lg hover:shadow-xl transform hover:-translate-y-1 disabled:opacity-70 disabled:transform-none"
                            >
                                {loading ? 'جاري التسجيل...' : 'إتمام التسجيل ✨'}
                            </button>
                        </div>
                    </form>
                )}

                <div className="mt-8 text-center text-sm text-gray-500">
                    لديك حساب بالفعل؟{' '}
                    <Link href="/admin/login" className="text-primary font-bold hover:underline">
                        تسجيل الدخول
                    </Link>
                </div>
            </div>
        </div>
    );
}
