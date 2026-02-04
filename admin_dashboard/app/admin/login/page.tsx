'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AdminService } from '../../../services/api';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');



    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const data = await AdminService.login({ email, password });
            // Save token/user to localStorage (simplified for now)
            localStorage.setItem('token', data.token); // Assuming backend returns token
            localStorage.setItem('user', JSON.stringify(data.user));

            router.push('/dashboard');
        } catch (err) {
            setError('بيانات الدخول غير صحيحة أو حدث خطأ ما');
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-warm-cream" dir="rtl">
            <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md border border-accent/30">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-primary mb-2">الأسر المنتجة</h1>
                    <p className="text-charcoal/60">لوحة تحكم الإدارة</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    {error && (
                        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm text-center border border-red-100">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">البريد الإلكتروني</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all hover:border-primary/50"
                            placeholder="admin@example.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">كلمة المرور</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all hover:border-primary/50"
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-primary text-white font-bold py-3 rounded-lg hover:bg-primary-hover transition-colors shadow-md hover:shadow-lg"
                    >
                        دخول
                    </button>
                </form>
            </div>
        </div>
    );
}
