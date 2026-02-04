import Link from 'next/link';
import { Home, Users, ShoppingBag, Settings, LogOut } from 'lucide-react';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex h-screen bg-gray-100 font-sans" dir="rtl">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md hidden md:flex flex-col">
                <div className="p-6 border-b">
                    <h1 className="text-2xl font-bold text-gray-800">الأسر المنتجة</h1>
                    <p className="text-sm text-gray-500">لوحة الإدارة</p>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 text-gray-700 bg-gray-50 rounded-lg hover:bg-green-50 hover:text-green-600 transition-colors">
                        <Home size={20} />
                        <span>الرئيسية</span>
                    </Link>

                    <Link href="/dashboard/users" className="flex items-center gap-3 px-4 py-3 text-gray-600 rounded-lg hover:bg-green-50 hover:text-green-600 transition-colors">
                        <Users size={20} />
                        <span>المستخدمين والأسر</span>
                    </Link>

                    <Link href="/dashboard/orders" className="flex items-center gap-3 px-4 py-3 text-gray-600 rounded-lg hover:bg-green-50 hover:text-green-600 transition-colors">
                        <ShoppingBag size={20} />
                        <span>الطلبات</span>
                    </Link>

                    <Link href="/dashboard/settings" className="flex items-center gap-3 px-4 py-3 text-gray-600 rounded-lg hover:bg-green-50 hover:text-green-600 transition-colors">
                        <Settings size={20} />
                        <span>الإعدادات</span>
                    </Link>
                </nav>

                <div className="p-4 border-t">
                    <button className="flex items-center gap-3 w-full px-4 py-3 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                        <LogOut size={20} />
                        <span>تسجيل خروج</span>
                    </button>
                </div>

                <div className="p-4 text-center text-xs text-gray-400 border-t bg-gray-50">
                    <p>جميع الحقوق محفوظة © {new Date().getFullYear()}</p>
                    <p className="font-bold text-gray-500 mt-1">شركة أثر (Athar Company)</p>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-4 md:p-8">
                {children}
            </main>
        </div>
    );
}
