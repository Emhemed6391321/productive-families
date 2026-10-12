// Demo stand-in for the real completion util (requirement list is illustrative).
export interface PilgrimCompletionResult { percentage: number; isComplete: boolean; fulfilledCount: number; totalRequirements: number; sections: { id: string; title: string; isComplete: boolean; fulfilled: number; total: number }[]; missingFields: { field: string; label: string; sectionId: string }[]; }
export const calculatePilgrimCompletion = (p: any, h: any): PilgrimCompletionResult => {
  const dig = (v?: string) => (v || '').replace(/\D/g, '');
  const defs: { sec: string; title: string; sectionId: string; field: string; label: string; ok: boolean }[] = [
    { sec: 'passport', title: 'الجواز', sectionId: 'section-passport', field: 'passportNumber', label: 'رقم الجواز', ok: !!p.passportNumber },
    { sec: 'passport', title: 'الجواز', sectionId: 'section-passport', field: 'passportExpiryDate', label: 'تاريخ انتهاء الجواز', ok: !!p.passportExpiryDate },
    { sec: 'passport', title: 'الجواز', sectionId: 'section-passport', field: 'passportImageUrl', label: 'صورة الجواز', ok: !!p.passportImageUrl },
    { sec: 'health', title: 'الإفصاح الصحي', sectionId: 'section-health', field: 'legal', label: 'الإقرار القانوني الصحي', ok: !!h.legalDeclarationAcknowledged },
    { sec: 'contact', title: 'التواصل', sectionId: 'section-contact', field: 'phoneNumber', label: 'رقم الهاتف الأساسي', ok: dig(p.phoneNumber).length >= 9 },
    { sec: 'contact', title: 'التواصل', sectionId: 'section-contact', field: 'primaryPhoneHasWhatsapp', label: 'حالة واتساب للرقم الأساسي', ok: !!p.primaryPhoneHasWhatsapp && p.primaryPhoneHasWhatsapp !== 'UNSPECIFIED' },
    { sec: 'contact', title: 'التواصل', sectionId: 'section-contact', field: 'whatsappNumber', label: 'رقم الواتساب الإضافي', ok: dig(p.whatsappNumber).length >= 9 },
    { sec: 'contact', title: 'التواصل', sectionId: 'section-contact', field: 'office', label: 'المكتب التابع له', ok: !!p.office },
    { sec: 'address', title: 'السكن', sectionId: 'section-address', field: 'city', label: 'المدينة', ok: !!p.city },
    { sec: 'address', title: 'السكن', sectionId: 'section-address', field: 'region', label: 'المنطقة / المحلة', ok: !!p.region },
  ];
  const secs: Record<string, any> = {};
  defs.forEach(d => { const s = (secs[d.sec] ||= { id: d.sec, title: d.title, fulfilled: 0, total: 0 }); s.total++; if (d.ok) s.fulfilled++; });
  const fulfilled = defs.filter(d => d.ok).length;
  return { percentage: Math.round(fulfilled / defs.length * 100), isComplete: fulfilled === defs.length, fulfilledCount: fulfilled, totalRequirements: defs.length,
    sections: Object.values(secs).map((s: any) => ({ ...s, isComplete: s.fulfilled === s.total })),
    missingFields: defs.filter(d => !d.ok).map(d => ({ field: d.field, label: d.label, sectionId: d.sectionId })) };
};
