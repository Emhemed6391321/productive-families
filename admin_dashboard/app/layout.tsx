import type { Metadata } from "next";
import { IBM_Plex_Sans_Arabic } from "next/font/google"; // Using IBM Plex Sans Arabic as requested
import "./globals.css";

const ibmPlexSansArabic = IBM_Plex_Sans_Arabic({
  variable: "--font-ibm-plex-sans-arabic",
  subsets: ["arabic"],
  weight: ["100", "200", "300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Productive Families",
  description: "Platform for productive families",
};

import { CartProvider } from "../context/CartContext";
import CartSidebar from "../components/CartSidebar";
import PublicLayoutWrapper from "../components/PublicLayoutWrapper";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body
        className={`${ibmPlexSansArabic.variable} antialiased font-sans`}
      >
        <CartProvider>
          {/* We can conditionally render Header if we want to hide it on Admin Login, 
               but strictly speaking standard layout is easier. 
               However, Admin Dashboard usually has its own layout. 
               Let's render Header only for public pages if possible, or usually 
               we separate layouts. For now, let's keep it simple: 
               Header shows everywhere but maybe different links. 
               Actually, the Header component links to admin login, so it's fine for public.
               But for /dashboard routes, they have their own layout? 
               Yes, /dashboard/layout.tsx exists.
               Next.js RootLayout wraps EVERYTHING. 
               So if we put Header here, it appears in Dashboard too?
               Yes. We might want to hide it for /dashboard routes.
           */}
          <PublicLayoutWrapper>{children}</PublicLayoutWrapper>
          <CartSidebar />
        </CartProvider>
      </body>
    </html>
  );
}

// Helper to conditionally render Header
// Note: In Server Components we can't use usePathname easily in the root layout directly 
// without making it a client component.
// Let's make a small client wrapper or just make the whole layout client? 
// Actually, RootLayout is server by default (metadata export).
// Better approach: Move the Header/Cart logic to a "Providers" client component.

