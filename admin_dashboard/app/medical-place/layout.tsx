import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "مكان الكشف الطبي | تنسيقية حجاج طرابلس ب",
  description: "اكتب رقم القرعة لتعرف مكان الكشف الطبي أو العيادة للحاج والمرافق.",
};

export const viewport: Viewport = {
  themeColor: "#0B4A2B",
};

export default function MedicalPlaceLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
