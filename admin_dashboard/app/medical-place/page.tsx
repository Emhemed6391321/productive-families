'use client';
import { useState } from 'react';
import { Ticket, Search, FileText, Phone } from 'lucide-react';

const PHONE = '0934455422';
const PAGE_URL = 'tripoli-b.ly/medical-place';

const REQUIRED_DOCUMENTS = [
    { label: 'شهادة الميلاد بالرقم الوطني', note: 'نسختين', highlight: true },
    { label: 'جواز السفر' },
    { label: 'التقارير الطبية اللازمة' },
];

const STEPS = [
    { title: 'افتح الرابط', subtitle: 'من هاتفك أو حاسوبك' },
    { title: 'اكتب رقم القرعة', subtitle: 'الخاص بك أو بمرافقك' },
    { title: 'اعرف مكان الكشف', subtitle: 'مكان العيادة المخصصة لك' },
];

export default function MedicalPlacePage() {
    const [lotteryNumber, setLotteryNumber] = useState('');
    const [message, setMessage] = useState('');

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        const value = lotteryNumber.trim();

        if (!/^\d+$/.test(value)) {
            setMessage('أدخل رقم القرعة بالأرقام فقط.');
            return;
        }

        // TODO: ربط البحث بمصدر بيانات الكشف الطبي عند توفره
        setMessage('خدمة الاستعلام قيد التجهيز.');
    };

    return (
        <main
            dir="rtl"
            className="min-h-dvh overflow-x-hidden bg-[#FBF7EC] bg-[radial-gradient(circle_at_top,#FFFFFF_0%,#FBF7EC_45%,#F1E6C9_100%)] text-[#0B4A2B] pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]"
        >
            <div className="mx-auto flex w-full max-w-md flex-col items-center px-4 pb-6 pt-8">

                {/* Brand header (from the poster) */}
                <header className="mb-6 text-center">
                    <p className="text-sm text-[#7A6230]">الهيئة العامة لشؤون الحج والعمرة</p>
                    <p className="mt-1 text-lg font-bold text-[#0B4A2B]">تنسيقية حجاج طرابلس ب</p>
                    <div className="mx-auto mt-3 h-px w-40 bg-gradient-to-l from-transparent via-[#B08A3E] to-transparent" />
                </header>

                {/* Logo tile */}
                <div className="flex h-28 w-28 items-center justify-center rounded-[28px] border border-[#E6D6A8] bg-white shadow-[0_12px_30px_-12px_rgba(11,74,43,0.35)]">
                    <img src="/medical-place/logo.png" alt="شعار تنسيقية حجاج طرابلس" className="h-20 w-auto" />
                </div>

                {/* Service badge */}
                <span className="mt-5 rounded-full border border-[#2E8B62]/40 bg-white/80 px-5 py-2 text-sm font-medium text-[#0B4A2B]">
                    خدمة تابعة لتنسيقية طرابلس (ب)
                </span>

                {/* Title */}
                <h1 className="mt-6 text-center text-4xl font-extrabold leading-tight text-[#0B4A2B]">
                    الكشف الطبي
                </h1>
                <p className="mt-2 text-center text-lg font-semibold text-[#B08A3E]">
                    اعرف مكان عيادتك ومكان مرافقك
                </p>
                <p className="mt-3 text-center text-base leading-relaxed text-[#5B5443]">
                    اكتب رقم القرعة لتعرف المستوصف أو العيادة وموعد الكشف الطبي، للحاج والمرافق.
                </p>

                {/* Search card */}
                <section className="mt-7 w-full rounded-[32px] border border-[#E6D6A8] bg-white p-5 shadow-[0_20px_50px_-20px_rgba(11,74,43,0.25)]">
                    <form onSubmit={handleSearch} className="flex flex-col gap-4">
                        <label htmlFor="lottery-number" className="sr-only">رقم القرعة</label>
                        <div className="relative">
                            <Ticket
                                aria-hidden
                                className="pointer-events-none absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-[#2E8B62]"
                            />
                            <input
                                id="lottery-number"
                                type="text"
                                inputMode="numeric"
                                autoComplete="off"
                                placeholder="رقم القرعة"
                                value={lotteryNumber}
                                onChange={(e) => setLotteryNumber(e.target.value)}
                                className="h-14 w-full rounded-2xl border-2 border-[#E6E1D3] bg-[#FDFBF5] pr-12 pl-4 text-center text-[17px] text-[#0B4A2B] placeholder:text-[#A39C88] focus:border-[#2E8B62] focus:outline-none focus:ring-4 focus:ring-[#2E8B62]/15"
                            />
                        </div>

                        <button
                            type="submit"
                            className="flex h-14 w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-l from-[#0B5E3B] to-[#0E7A6A] text-lg font-bold text-white shadow-[0_12px_24px_-10px_rgba(11,94,59,0.6)] transition active:scale-[0.98]"
                        >
                            <Search aria-hidden className="h-5 w-5" />
                            ابحث عن مكانك
                        </button>

                        {message && (
                            <p role="status" aria-live="polite" className="text-center text-sm font-medium text-[#7A6230]">
                                {message}
                            </p>
                        )}
                    </form>
                </section>

                {/* Required documents */}
                <section className="mt-6 w-full rounded-[28px] border-2 border-[#F0D98C] bg-[#FFFBEA] p-5">
                    <div className="flex items-center justify-between gap-3">
                        <h2 className="text-lg font-bold text-[#8A4B0F]">تنبيه: المستندات المطلوبة</h2>
                        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[#FCEFC2] text-[#C2650A]">
                            <FileText aria-hidden className="h-5 w-5" />
                        </span>
                    </div>
                    <p className="mt-4 text-[#8A4B0F]">يجب على الحاج إحضار:</p>
                    <ul className="mt-3 space-y-3">
                        {REQUIRED_DOCUMENTS.map((doc) => (
                            <li key={doc.label} className="flex items-center gap-3 text-[#2B2A24]">
                                <span className="h-2.5 w-2.5 shrink-0 rounded-full bg-[#F29B1D]" />
                                <span className="font-semibold">
                                    {doc.label}
                                    {doc.note && <span className="text-[#C2650A]">، {doc.note}</span>}
                                </span>
                            </li>
                        ))}
                    </ul>
                </section>

                {/* How it works (from the poster) */}
                <section className="mt-6 w-full rounded-[28px] bg-white/70 p-5 shadow-sm">
                    <ol className="relative space-y-5">
                        {STEPS.map((step, index) => (
                            <li key={step.title} className="flex items-center gap-4">
                                <span className="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 border-[#B08A3E] bg-[#0B4A2B] text-base font-bold text-[#F3E3B0]">
                                    {index + 1}
                                </span>
                                <span className="flex flex-col">
                                    <span className="text-lg font-bold text-[#0B4A2B]">{step.title}</span>
                                    <span className="text-sm text-[#7A6230]">{step.subtitle}</span>
                                </span>
                            </li>
                        ))}
                    </ol>
                </section>

                {/* QR code (from the poster) */}
                <section className="mt-6 flex w-full flex-col items-center rounded-[28px] border border-[#E6D6A8] bg-white p-5 shadow-sm">
                    <div className="rounded-2xl border-2 border-[#B08A3E] bg-white p-3">
                        <img src="/medical-place/qr.svg" alt="رمز QR لفتح صفحة الكشف الطبي" className="h-40 w-40" />
                    </div>
                    <p className="mt-3 text-sm font-bold text-[#0B4A2B]">امسح الرمز</p>
                    <a
                        href="https://tripoli-b.ly/medical-place"
                        className="mt-4 flex w-full items-center justify-center rounded-full bg-gradient-to-l from-[#0B5E3B] to-[#0B4A2B] px-4 py-3 text-center text-base font-bold tracking-wide text-[#F3E3B0] shadow-md break-all"
                        dir="ltr"
                    >
                        {PAGE_URL}
                    </a>
                </section>

                {/* Footer bar (from the poster) */}
                <footer className="mt-6 flex w-full items-center justify-between gap-3 rounded-2xl bg-[#0B4A2B] px-5 py-4 text-[#F3E3B0]">
                    <a href={`tel:${PHONE}`} className="flex items-center gap-2 font-bold" dir="ltr">
                        <Phone aria-hidden className="h-4 w-4" />
                        {PHONE}
                    </a>
                    <span className="text-sm font-semibold">تنسيقية حجاج طرابلس ب</span>
                </footer>
            </div>
        </main>
    );
}
