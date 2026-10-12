// Demo stand-in: simulates the MRZ reader with a fake sample passport (no real data).
export interface PassportOcrResult { success: boolean; error?: string; passportNumber?: string; passportExpiryDate?: string; birthDate?: string; fullNameEnglish?: string; nationality?: string; verified?: boolean; }
export const readPassportImage = async (_img: string, onProgress: (pct: number, text: string) => void): Promise<PassportOcrResult> => {
  const steps: [number, string][] = [[15, 'جاري تحسين الصورة...'], [40, 'جاري البحث عن شريط الجواز (MRZ)...'], [70, 'جاري قراءة الأسطر السفلية...'], [92, 'جاري التحقق من خانات التدقيق...']];
  for (const [p, t] of steps) { onProgress(p, t); await new Promise(r => setTimeout(r, (window as any).__ocrDelay ?? 700)); }
  return { success: true, passportNumber: 'XD0123456', passportExpiryDate: '2031-05-18', birthDate: '1985-03-12', fullNameEnglish: 'ABDULLAH MOHAMED ALI ALAMEEN', nationality: 'LBY', verified: true };
};
