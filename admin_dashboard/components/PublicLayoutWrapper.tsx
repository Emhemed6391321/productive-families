'use client';
import { usePathname } from "next/navigation";
import Header from "../components/Header";

export default function PublicLayoutWrapper({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const isDashboard = pathname?.startsWith('/dashboard');
    const isAdminLogin = pathname?.startsWith('/admin/login');

    // Don't show public header on dashboard or admin login (admin login has its own style, or maybe keep it?)
    // Let's keep it clean: no header on dashboard (it has sidebar).
    // Admin login might want to go back to home, but it has its own UI.

    if (isDashboard) return <>{children}</>;

    return (
        <>
            {!isAdminLogin && <Header />}
            {children}
        </>
    );
}
