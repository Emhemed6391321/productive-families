'use client';
import { useState, useEffect } from 'react';
import DashboardLayout from '../../../components/DashboardLayout'; // Adjusted path
import { AdminService } from '../../../services/api';

export default function AdminProductsPage() {
    const [editingProduct, setEditingProduct] = useState<any>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleDelete = async (id: number) => {
        if (confirm('هل أنت متأكد من حذف هذا المنتج؟')) {
            try {
                await AdminService.deleteProduct(id);
                fetchProducts();
            } catch (error) {
                alert('فشل في حذف المنتج');
                console.error(error);
            }
        }
    };

    const handleEditClick = (product: any) => {
        setEditingProduct({ ...product });
        setIsModalOpen(true);
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await AdminService.updateProduct(editingProduct.id, {
                name: editingProduct.name,
                description: editingProduct.description,
                price: parseFloat(editingProduct.price),
                preparation_time_minutes: parseInt(editingProduct.preparation_time_minutes)
            });
            setIsModalOpen(false);
            fetchProducts();
        } catch (error) {
            alert('فشل في تحديث المنتج');
            console.error(error);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setEditingProduct({ ...editingProduct, [name]: value });
    };

    const colors = {
        primary: '#CC5500', // Burnt Orange
        secondary: '#556B2F', // Olive Green
        warmCream: '#FFFDD0',
        charcoal: '#333333'
    };

    return (
        <DashboardLayout>
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-2xl font-bold" style={{ color: colors.charcoal }}>إدارة المنتجات</h2>
                    <p className="text-gray-500 text-sm">عرض وإدارة جميع المنتجات المضافة من الأسر</p>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-right">
                        <thead className="bg-gray-50 text-gray-600 font-medium text-sm">
                            <tr>
                                <th className="p-4">اسم المنتج</th>
                                <th className="p-4">الأسرة</th>
                                <th className="p-4">السعر</th>
                                <th className="p-4">الوصف</th>
                                <th className="p-4">وقت التحضير</th>
                                <th className="p-4">الإجراءات</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {products.map((product) => (
                                <tr key={product.id} className="hover:bg-gray-50 transition">
                                    <td className="p-4">
                                        <div className="font-medium text-gray-800">{product.name}</div>
                                    </td>
                                    <td className="p-4 text-gray-600">{product.family?.business_name || '-'}</td>
                                    <td className="p-4 font-bold" style={{ color: colors.secondary }}>{product.price} ر.س</td>
                                    <td className="p-4 text-gray-500 text-sm max-w-xs truncate">{product.description || '-'}</td>
                                    <td className="p-4 text-gray-500">{product.preparation_time_minutes} دقيقة</td>
                                    <td className="p-4">
                                        <button
                                            onClick={() => handleEditClick(product)}
                                            className="text-blue-600 hover:text-blue-800 text-sm ml-2 font-semibold"
                                        >
                                            تعديل
                                        </button>
                                        <button
                                            onClick={() => handleDelete(product.id)}
                                            className="text-red-500 hover:text-red-700 text-sm font-semibold"
                                        >
                                            حذف
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {products.length === 0 && !loading && (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-gray-500">
                                        لا توجد منتجات لعرضها.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                {loading && (
                    <div className="p-8 text-center text-gray-500">
                        جاري التحميل...
                    </div>
                )}
            </div>

            {isModalOpen && editingProduct && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-fade-in border-t-4" style={{ borderColor: colors.primary }}>
                        <h3 className="text-xl font-bold mb-4" style={{ color: colors.charcoal }}>تعديل المنتج</h3>
                        <form onSubmit={handleUpdate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">اسم المنتج</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={editingProduct.name}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:border-transparent outline-none"
                                    style={{ '--tw-ring-color': colors.primary } as any}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">السعر</label>
                                <input
                                    type="number"
                                    name="price"
                                    value={editingProduct.price}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:border-transparent outline-none"
                                    style={{ '--tw-ring-color': colors.primary } as any}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">وقت التحضير (دقيقة)</label>
                                <input
                                    type="number"
                                    name="preparation_time_minutes"
                                    value={editingProduct.preparation_time_minutes}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:border-transparent outline-none"
                                    style={{ '--tw-ring-color': colors.primary } as any}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">الوصف</label>
                                <textarea
                                    name="description"
                                    rows={3}
                                    value={editingProduct.description}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:border-transparent outline-none"
                                    style={{ '--tw-ring-color': colors.primary } as any}
                                ></textarea>
                            </div>
                            <div className="flex justify-end gap-2 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-bold"
                                >
                                    إلغاء
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 text-white rounded-lg font-bold shadow-md hover:shadow-lg transition"
                                    style={{ backgroundColor: colors.primary }}
                                >
                                    حفظ التعديلات
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
}
