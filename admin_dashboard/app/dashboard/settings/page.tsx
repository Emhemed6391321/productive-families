'use client';
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Save, Bell, Lock, Palette } from 'lucide-react';

export default function SettingsPage() {
    const [siteName, setSiteName] = useState('الأسر المنتجة');
    const [maintenanceMode, setMaintenanceMode] = useState(false);

    return (
        <DashboardLayout>
            <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-800">إعدادات النظام</h2>
                <p className="text-gray-500">تحكم في خصائص المنصة والمظهر العام</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* General Settings */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Palette size={20} /></div>
                        <h3 className="font-bold text-lg">إعدادات عامة</h3>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">اسم المنصة</label>
                            <input
                                type="text"
                                value={siteName}
                                onChange={(e) => setSiteName(e.target.value)}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                            />
                        </div>

                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                                <p className="font-medium text-gray-800">وضع الصيانة</p>
                                <p className="text-xs text-gray-500">إيقاف الموقع مؤقتاً للزوار</p>
                            </div>
                            <div
                                onClick={() => setMaintenanceMode(!maintenanceMode)}
                                className={`w-12 h-6 rounded-full p-1 cursor-pointer transition-colors ${maintenanceMode ? 'bg-green-500' : 'bg-gray-300'}`}
                            >
                                <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${maintenanceMode ? '-translate-x-6' : 'translate-x-0'}`}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Account Security */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b">
                        <div className="p-2 bg-orange-50 text-orange-600 rounded-lg"><Lock size={20} /></div>
                        <h3 className="font-bold text-lg">الأمان والحساب</h3>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">البريد الإلكتروني للإدارة</label>
                            <input type="email" value="admin@example.com" disabled
                                className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-500"
                            />
                        </div>

                        <button className="w-full border border-gray-300 py-2 rounded-lg text-gray-700 hover:bg-gray-50 font-medium">
                            تغيير كلمة المرور
                        </button>
                    </div>
                </div>

                {/* Notifications */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center gap-3 mb-6 pb-4 border-b">
                        <div className="p-2 bg-purple-50 text-purple-600 rounded-lg"><Bell size={20} /></div>
                        <h3 className="font-bold text-lg">الإشعارات</h3>
                    </div>

                    <div className="space-y-2">
                        {['طلبات جديدة', 'تسجيل أسرة جديدة', 'شكاوى العملاء'].map((item, idx) => (
                            <label key={idx} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer">
                                <input type="checkbox" defaultChecked className="w-4 h-4 text-green-600 rounded focus:ring-green-500" />
                                <span className="text-gray-700">{item}</span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            <div className="mt-8 flex justify-end">
                <button className="flex items-center gap-2 bg-green-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-green-700 shadow-lg hover:shadow-green-200 transition-all">
                    <Save size={20} />
                    <span>حفظ التغييرات</span>
                </button>
            </div>

            <div className="mt-12 text-center border-t pt-8 text-gray-400 text-sm">
                <p>Productive Families System v1.0.0</p>
                <p className="mt-1">Developed by <span className="font-bold text-gray-600">Athar Company</span></p>
            </div>
        </DashboardLayout>
    );
}
