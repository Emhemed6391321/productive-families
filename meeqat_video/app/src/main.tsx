import React from 'react';
import { createRoot } from 'react-dom/client';
import { PublicPilgrimForm } from './components/PublicPilgrimForm';

// ---- in-memory mock of the portal API (ALL DATA IS FICTIONAL) ----
const db: Record<string, any> = {
  '119900000001': { id: 'p1', fullName: 'عبدالله محمد علي الأمين', nationalId: '119900000001', lotteryNumber: '48217', birthDate: '1985-03-12', gender: 'MALE', role: 'PILGRIM', docStatus: 'PENDING', phoneNumber: '', passportNumber: '', office: '', city: '', region: '' },
  '219900000002': { id: 'p2', fullName: 'مريم خالد سالم الأمين', nationalId: '219900000002', lotteryNumber: '48218', birthDate: '1988-07-02', gender: 'FEMALE', role: 'PILGRIM', docStatus: 'PENDING' },
  '119900000003': { id: 'p3', fullName: 'يوسف إبراهيم عمر الفيتوري', nationalId: '119900000003', lotteryNumber: '48230', birthDate: '1979-11-25', gender: 'MALE', role: 'PILGRIM', docStatus: 'VERIFIED', phoneNumber: '0912345678', primaryPhoneHasWhatsapp: 'YES', whatsappNumber: '0923456789', passportNumber: 'XD0765432', passportExpiryDate: '2030-01-10', office: 'مكتب الهضبة', city: 'طرابلس', region: 'الهضبة' },
};
(window as any).__db = db;
const realFetch = window.fetch.bind(window);
window.fetch = async (url: any, init?: any) => {
  const u = String(url);
  const json = (b: any, ok = true) => new Response(JSON.stringify(b), { status: ok ? 200 : 400, headers: { 'Content-Type': 'application/json' } });
  await new Promise(r => setTimeout(r, (window as any).__netDelay ?? 600));
  if (u.startsWith('/api/settings/sort_rules')) return json({ value: JSON.stringify({ enablePassportExpiryCheck: true, minPassportExpiryDate: '2026-11-01' }) });
  if (u.startsWith('/api/pilgrims?nationalId=')) { const id = decodeURIComponent(u.split('=')[1]); return json(db[id] ? [db[id]] : []); }
  const m = u.match(/^\/api\/pilgrims\/public\/(.+)$/);
  if (m && init?.method === 'PUT') {
    const body = JSON.parse(init.body); const rec: any = Object.values(db).find((r: any) => r.id === m[1]);
    const h = body.healthDisclosure || {};
    Object.assign(rec, body, { docStatus: 'RECEIVED' }); delete rec.verifier; delete rec.healthDisclosure;
    rec.healthDisclosure = { has_chronic_disease: h.hasChronicDisease, chronic_diseases: h.chronicDiseases || [], has_mobility_limitation: h.hasMobilityLimitation,
      has_recent_surgery: h.hasRecentSurgery, past_surgeries: h.surgeryDetails || '', has_allergies: h.hasAllergies, allergies: h.allergyDetails || '',
      has_medical_devices: h.hasMedicalDevices, medical_devices_needed: h.deviceDetails || '', is_pregnant: h.isPregnant, gestational_weeks: h.gestationalWeeks,
      regular_medications: h.regularMedications || '', notes: h.notes || '', legal_declaration_acknowledged: h.legalDeclarationAcknowledged };
    return json(rec);
  }
  return realFetch(url, init);
};
(window as any).alert = (msg: string) => { (window as any).__lastAlert = msg; };

createRoot(document.getElementById('root')!).render(
  <PublicPilgrimForm onUpdate={() => {}} coordinationInfo={{ name: 'تنسيقية حجاج طرابلس (ب)', coordinatorName: '', offices: [] }} />
);
