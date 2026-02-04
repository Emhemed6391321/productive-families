import DashboardLayout from '../../components/DashboardLayout';

export default function DashboardPage() {
    return (
        <DashboardLayout>
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-800">مرحباً بك، المدير</h2>
                <p className="text-gray-500 mt-2">نظرة عامة على أداء المنصة اليوم.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">إجمالي الطلبات</h3>
                    <p className="text-3xl font-bold text-gray-800 mt-2">1,240</p>
                    <span className="text-green-500 text-sm">+12% هذا الأسبوع</span>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">إجمالي المبيعات</h3>
                    <p className="text-3xl font-bold text-gray-800 mt-2">45,000 ر.س</p>
                    <span className="text-green-500 text-sm">+5% هذا الأسبوع</span>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">أسر منتجة جديدة</h3>
                    <p className="text-3xl font-bold text-gray-800 mt-2">12</p>
                    <span className="text-orange-500 text-sm">بانتظار الموافقة</span>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">المستخدمين النشطين</h3>
                    <p className="text-3xl font-bold text-gray-800 mt-2">3,500</p>
                </div>
            </div>

            {/* Recent Activity Table Placeholders */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-xl font-bold text-gray-800 mb-4">آخر الطلبات</h3>
                    <div className="text-center py-8 text-gray-400">لا توجد طلبات حديثة</div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-xl font-bold text-gray-800 mb-4">طلبات انضمام الأسر</h3>
                    <div className="bg-orange-50 p-4 rounded-lg flex justify-between items-center mb-3">
                        <div>
                            <h4 className="font-bold text-gray-800">مطبخ أم خالد</h4>
                            <p className="text-sm text-gray-500">مأكولات شعبية - الرياض</p>
                        </div>
                        <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">مراجعة</button>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg flex justify-between items-center">
                        <div>
                            <h4 className="font-bold text-gray-800">حرف يدوية فاخرة</h4>
                            <p className="text-sm text-gray-500">أشغال يدوية - جدة</p>
                        </div>
                        <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">مراجعة</button>
                    </div>
                </div>
            </div>

        </DashboardLayout>
    );
}
