'use client';
import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

export default function OrdersPage() {
    const [orders, setOrders] = useState<any[]>([]);

    useEffect(() => {
        // Mock data
        setOrders([
            { id: 101, customer: 'محمد سالم', family: 'مأكولات أم علي', total: 150, status: 'PENDING', date: '2023-10-01' },
            { id: 102, customer: 'نورة سعد', family: 'حلويات شرقية', total: 320, status: 'DELIVERED', date: '2023-09-28' },
        ]);
    }, []);

    return (
        <DashboardLayout>
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800">إدارة الطلبات</h2>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-right">
                    <thead className="bg-gray-50 text-gray-500 text-sm">
                        <tr>
                            <th className="px-6 py-4">رقم الطلب</th>
                            <th className="px-6 py-4">العميل</th>
                            <th className="px-6 py-4">الأسرة المنتجة</th>
                            <th className="px-6 py-4">الإجمالي</th>
                            <th className="px-6 py-4">الحالة</th>
                            <th className="px-6 py-4">التاريخ</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {orders.map((order) => (
                            <tr key={order.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 font-bold text-gray-800">#{order.id}</td>
                                <td className="px-6 py-4 text-gray-600">{order.customer}</td>
                                <td className="px-6 py-4 text-gray-600">{order.family}</td>
                                <td className="px-6 py-4 font-bold text-green-600">{order.total} ر.س</td>
                                <td className="px-6 py-4">
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${order.status === 'DELIVERED' ? 'bg-green-100 text-green-700' :
                                        order.status === 'PENDING' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'
                                        }`}>
                                        {order.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-gray-400 text-sm">{order.date}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </DashboardLayout>
    );
}
