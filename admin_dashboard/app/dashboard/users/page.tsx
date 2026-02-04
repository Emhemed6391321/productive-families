'use client';
import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { User, Check, X } from 'lucide-react';

export default function UsersPage() {
    const [families, setFamilies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // Mock data for now since backend might not be running
    useEffect(() => {
        // In real app: fetch from API
        setTimeout(() => {
            setFamilies([
                { id: 1, business_name: 'مأكولات أم علي', owner_name: 'فاطمة علي', status: 'pending', city: 'الرياض' },
                { id: 2, business_name: 'حرف يدوية', owner_name: 'أحمد محمد', status: 'active', city: 'جدة' },
                { id: 3, business_name: 'حلويات شرقية', owner_name: 'سارة خالد', status: 'active', city: 'الدمام' },
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    return (
        <DashboardLayout>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">إدارة الأسر المنتجة</h2>
                <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">إضافة أسرة جديدة</button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-right">
                    <thead className="bg-gray-50 text-gray-500 text-sm">
                        <tr>
                            <th className="px-6 py-4 font-medium">اسم المتجر</th>
                            <th className="px-6 py-4 font-medium">اسم المالك</th>
                            <th className="px-6 py-4 font-medium">المدينة</th>
                            <th className="px-6 py-4 font-medium">الحالة</th>
                            <th className="px-6 py-4 font-medium">الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {families.map((family) => (
                            <tr key={family.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4 font-medium text-gray-800">{family.business_name}</td>
                                <td className="px-6 py-4 text-gray-600">{family.owner_name}</td>
                                <td className="px-6 py-4 text-gray-500">{family.city}</td>
                                <td className="px-6 py-4">
                                    {family.status === 'active' ? (
                                        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold">نشط</span>
                                    ) : (
                                        <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-xs font-bold">بانتظار الموافقة</span>
                                    )}
                                </td>
                                <td className="px-6 py-4 flex gap-2">
                                    <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg" title="قبول">
                                        <Check size={18} />
                                    </button>
                                    <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg" title="رفض">
                                        <X size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </DashboardLayout>
    );
}
