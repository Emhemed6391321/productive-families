import React, { useState, useEffect, useMemo } from 'react';
import { Pilgrim, HealthStatus, DocStatus, PilgrimRole } from '../types';
import { 
    Upload, CheckCircle, CheckCircle2, Save, MapPin, Search, Loader2, 
    ShieldCheck, Phone, Heart, Home, AlertCircle, Camera, Check, 
    ArrowRight, User, Users, Cigarette, Wind, HandHeart, Compass, 
    Share2, Info, Lock, Eye, X, Calendar, FileText, Sparkles,
    ScanLine, RefreshCw, AlertTriangle, FileCheck, MessageCircle, Building2,
    HeartPulse, Activity, Baby, Pill, Stethoscope, Plus, Trash2
} from 'lucide-react';
import { BLOOD_TYPES, COORDINATION_OFFICES } from '../constants';
import { readPassportImage, PassportOcrResult } from '../utils/passportOcr';
import { compressImageFile } from '../utils/imageUtils';

import { calculatePilgrimCompletion, PilgrimCompletionResult } from '../utils/pilgrimCompletion';

interface PublicPilgrimFormProps {
    onUpdate: (updatedPilgrim: Pilgrim) => void;
    coordinationInfo: { name: string; coordinatorName: string; offices: string[] };
}

const formatDateForInput = (val: any): string => {
    if (!val) return '';
    const str = String(val).trim();
    if (str.includes('T')) return str.split('T')[0];
    if (/^\d{4}-\d{2}-\d{2}/.test(str)) return str.slice(0, 10);
    return str;
};

export const PublicPilgrimForm: React.FC<PublicPilgrimFormProps> = ({ onUpdate, coordinationInfo }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [pilgrim, setPilgrim] = useState<Pilgrim | null>(null);
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [searchError, setSearchError] = useState<string | null>(null);
    const [formData, setFormData] = useState<Partial<Pilgrim>>({});
    const [originalPhoneNumber, setOriginalPhoneNumber] = useState('');

    // Submission Confirmation Modal & Missing List
    const [showSubmitConfirmModal, setShowSubmitConfirmModal] = useState(false);
    const [showMissingFieldsDetails, setShowMissingFieldsDetails] = useState(false);

    // Electronic Health Disclosure Form State (استمارة الإفصاح الصحي الإلكتروني)
    const [hasChronicDisease, setHasChronicDisease] = useState(false);
    const [chronicConditions, setChronicConditions] = useState<string[]>([]);
    const [customChronicCondition, setCustomChronicCondition] = useState('');
    const [hasMobilityLimitation, setHasMobilityLimitation] = useState(false);
    const [mobilityStatus, setMobilityStatus] = useState<string>('WALKS_LONG');
    const [hasRecentSurgery, setHasRecentSurgery] = useState(false);
    const [surgeryDetails, setSurgeryDetails] = useState('');
    const [hasAllergies, setHasAllergies] = useState(false);
    const [allergyDetails, setAllergyDetails] = useState('');
    const [hasMedicalDevices, setHasMedicalDevices] = useState(false);
    const [deviceDetails, setDeviceDetails] = useState('');
    const [isPregnant, setIsPregnant] = useState(false);
    const [gestationalWeeks, setGestationalWeeks] = useState<number | ''>('');
    const [regularMedications, setRegularMedications] = useState('');
    const [healthNotes, setHealthNotes] = useState('');
    const [legalDeclarationAcknowledged, setLegalDeclarationAcknowledged] = useState(true);

    // Companion linking state
    const [companionQuery, setCompanionQuery] = useState('');
    const [companionLoading, setCompanionLoading] = useState(false);
    const [companionSearchError, setCompanionSearchError] = useState<string | null>(null);
    const [linkedPilgrimName, setLinkedPilgrimName] = useState<string | null>(null);

    // Passport image lightbox modal
    const [previewImage, setPreviewImage] = useState<string | null>(null);

    // Passport Validity Rules from Smart Sorting (قواعد الفرز والتوزيع الذكي)
    const [passportRules, setPassportRules] = useState<{
        enablePassportExpiryCheck: boolean;
        minPassportExpiryDate: string;
        passportExpiryRejectMessage: string;
    }>({
        enablePassportExpiryCheck: true,
        minPassportExpiryDate: '2026-11-01',
        passportExpiryRejectMessage: 'عذراً، جواز السفر الحالي غير صالٍ للاعتماد نظراً لقرب تاريخ انتهائه. الحد الأدنى المقبول لصلاحية الجواز هو {MIN_DATE}. يرجى تجديد الجواز وإعادة المحاولة.'
    });

    // Passport OCR Reader State
    const [ocrLoading, setOcrLoading] = useState(false);
    const [ocrProgress, setOcrProgress] = useState<{ percent: number; text: string }>({ percent: 0, text: '' });
    const [ocrResult, setOcrResult] = useState<PassportOcrResult | null>(null);
    const [showOcrConfirmModal, setShowOcrConfirmModal] = useState(false);

    // Load Passport Rules on Mount from system_settings sort_rules
    useEffect(() => {
        fetch('/api/settings/sort_rules')
            .then(res => res.json())
            .then(data => {
                if (data?.value) {
                    try {
                        const parsed = JSON.parse(data.value);
                        setPassportRules({
                            enablePassportExpiryCheck: parsed.enablePassportExpiryCheck ?? true,
                            minPassportExpiryDate: parsed.minPassportExpiryDate || '2026-11-01',
                            passportExpiryRejectMessage: parsed.passportExpiryRejectMessage || ''
                        });
                    } catch (e) {
                        console.warn('Failed to parse sort_rules in PublicPilgrimForm', e);
                    }
                }
            })
            .catch(err => console.warn('Could not load passport rules', err));
    }, []);

    // Check if current passport is invalid according to minimum expiry rule
    const isPassportExpired = useMemo(() => {
        if (!passportRules.enablePassportExpiryCheck || !passportRules.minPassportExpiryDate) return false;
        if (!formData.passportExpiryDate) return false;
        const curDate = formData.passportExpiryDate.trim();
        const minDate = passportRules.minPassportExpiryDate.trim();
        return curDate < minDate;
    }, [formData.passportExpiryDate, passportRules]);

    const passportExpiryWarning = useMemo(() => {
        if (!isPassportExpired) return null;
        const minStr = passportRules.minPassportExpiryDate;
        const curStr = formData.passportExpiryDate || '';
        if (passportRules.passportExpiryRejectMessage) {
            return passportRules.passportExpiryRejectMessage
                .replace('{EXPIRY_DATE}', curStr)
                .replace('{MIN_DATE}', minStr);
        }
        return `عذراً، جواز السفر الحالي غير صالٍ للاعتماد نظراً لقرب تاريخ انتهائه (${curStr}). الحد الأدنى المقبول لصلاحية الجواز هو (${minStr}). يرجى تجديد الجواز وإعادة المحاولة.`;
    }, [isPassportExpired, formData.passportExpiryDate, passportRules]);

    // Operational rule: Editable until officially verified by coordinator (DocStatus.VERIFIED).
    // Submission (RECEIVED) does NOT lock the form!
    const isLocked = pilgrim?.docStatus === DocStatus.VERIFIED;
    const isSubmittedPendingVerification = pilgrim?.docStatus === DocStatus.RECEIVED;

    // Real-time Unified Completion Calculation
    const completionResult: PilgrimCompletionResult | null = useMemo(() => {
        if (!pilgrim) return null;
        const mergedPilgrim: Pilgrim = {
            ...pilgrim,
            ...formData,
            id: pilgrim.id,
            fullName: pilgrim.fullName,
            nationalId: pilgrim.nationalId,
            phoneNumber: formData.phoneNumber || '',
            primaryPhoneHasWhatsapp: formData.primaryPhoneHasWhatsapp,
            whatsappNumber: formData.whatsappNumber || '',
            passportNumber: formData.passportNumber || '',
            passportExpiryDate: formData.passportExpiryDate,
            passportImageUrl: formData.passportImageUrl,
            office: formData.office || '',
            city: formData.city || '',
            region: formData.region || '',
            emergencyContactPhone: formData.emergencyContactPhone || '',
            emergencyContactName: formData.emergencyContactName || ''
        };
        return calculatePilgrimCompletion(mergedPilgrim, {
            hasChronicDisease,
            chronicConditions,
            hasMobilityLimitation,
            mobilityStatus,
            hasRecentSurgery,
            surgeryDetails,
            hasAllergies,
            allergyDetails,
            hasMedicalDevices,
            deviceDetails,
            isPregnant,
            gestationalWeeks,
            regularMedications,
            legalDeclarationAcknowledged
        });
    }, [
        pilgrim,
        formData,
        hasChronicDisease,
        chronicConditions,
        hasMobilityLimitation,
        mobilityStatus,
        hasRecentSurgery,
        surgeryDetails,
        hasAllergies,
        allergyDetails,
        hasMedicalDevices,
        deviceDetails,
        isPregnant,
        gestationalWeeks,
        regularMedications,
        legalDeclarationAcknowledged
    ]);

    // Check if phone number was modified compared to original
    const hasPhoneChanged = useMemo(() => {
        if (!originalPhoneNumber) return false;
        return (formData.phoneNumber || '').trim() !== originalPhoneNumber.trim();
    }, [formData.phoneNumber, originalPhoneNumber]);

    // Offices enabled by the coordination admin (falls back to the full list), keeping any value already saved
    const officeOptions = useMemo(() => {
        const base = coordinationInfo.offices?.length ? coordinationInfo.offices : COORDINATION_OFFICES;
        return formData.office && !base.includes(formData.office) ? [formData.office, ...base] : base;
    }, [coordinationInfo.offices, formData.office]);

    // Compare the birth date read from the passport with the one registered in the lottery system
    const ocrBirthDateMismatch = useMemo(() => {
        if (!ocrResult?.birthDate || !pilgrim?.birthDate) return false;
        const registered = String(pilgrim.birthDate).slice(0, 10);
        return /^\d{4}-\d{2}-\d{2}$/.test(registered) && registered !== ocrResult.birthDate;
    }, [ocrResult, pilgrim]);

    const handleCompanionSearch = async () => {
        setCompanionSearchError(null);
        if (!companionQuery.trim()) return;

        setCompanionLoading(true);
        try {
            const response = await fetch(`/api/pilgrims?nationalId=${encodeURIComponent(companionQuery.trim())}`);
            if (response.ok) {
                const results: Pilgrim[] = await response.json();
                if (results.length > 0) {
                    setFormData(prev => ({ ...prev, linkedPilgrimId: results[0].id }));
                    setLinkedPilgrimName(results[0].fullName);
                    setCompanionQuery('');
                } else {
                    setCompanionSearchError("لم يتم العثور على حاج بهذا الرقم الوطني.");
                }
            } else {
                setCompanionSearchError("حدث خطأ أثناء البحث، يرجى المحاولة لاحقاً.");
            }
        } catch {
            setCompanionSearchError("تعذر الاتصال بالخادم، يرجى التأكد من اتصال الإنترنت.");
        } finally {
            setCompanionLoading(false);
        }
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setLoading(true);
        setPilgrim(null);
        setSuccessMessage(null);
        setSearchError(null);
        setCompanionSearchError(null);

        try {
            const cleanQuery = searchQuery.trim();
            const response = await fetch(`/api/pilgrims?nationalId=${encodeURIComponent(cleanQuery)}`);
            if (!response.ok) throw new Error('فشل استرجاع البيانات');

            const results: Pilgrim[] = await response.json();

            if (results && results.length > 0) {
                const found = results[0];
                setPilgrim(found);

                setOriginalPhoneNumber(found.phoneNumber || '');
                setFormData({
                    phoneNumber: found.phoneNumber || '',
                    primaryPhoneHasWhatsapp: found.primaryPhoneHasWhatsapp || 'UNSPECIFIED',
                    companionPhoneNumber: found.companionPhoneNumber || '',
                    whatsappNumber: found.whatsappNumber || '',
                    office: found.office || '',
                    city: found.city || '',
                    region: found.region || '',
                    streetName: found.streetName || '',
                    address: found.address || '',
                    nearestLandmark: found.nearestLandmark || '',
                    passportImageUrl: found.passportImageUrl || '',
                    passportNumber: found.passportNumber || '',
                    passportExpiryDate: formatDateForInput(found.passportExpiryDate),
                    healthStatus: found.healthStatus || HealthStatus.FIT,
                    healthNotes: found.healthNotes || '',
                    bloodType: found.bloodType || '',
                    healthRating: found.healthRating || undefined,
                    regularMedication: found.regularMedication || '',
                    emergencyContactName: found.emergencyContactName || '',
                    emergencyContactPhone: found.emergencyContactPhone || '',
                    emergencyContactRelation: found.emergencyContactRelation || '',
                    isSmoker: found.isSmoker || false,
                    toleratesColdAC: found.toleratesColdAC || false,
                    canHelpPilgrims: found.canHelpPilgrims || false,
                    goodWithMaps: found.goodWithMaps || false,
                    goodWithSocialMedia: found.goodWithSocialMedia || false,
                    umrahCount: found.umrahCount || 0,
                    lastUmrahDate: formatDateForInput(found.lastUmrahDate),
                    linkedPilgrimId: found.linkedPilgrimId
                });

                // Populate Electronic Health Disclosure State
                const disc: any = (found as any).healthDisclosure;
                if (disc) {
                    setHasChronicDisease(Boolean(disc.has_chronic_disease));
                    setHasMobilityLimitation(Boolean(disc.has_mobility_limitation));
                    setHasRecentSurgery(Boolean(disc.has_recent_surgery));
                    setHasAllergies(Boolean(disc.has_allergies));
                    setHasMedicalDevices(Boolean(disc.has_medical_devices));
                    setRegularMedications(disc.regular_medications || found.regularMedication || found.medication || '');
                    setHealthNotes(disc.notes || found.healthNotes || '');
                    setIsPregnant(Boolean(disc.is_pregnant));
                    setGestationalWeeks(disc.gestational_weeks || '');
                    setLegalDeclarationAcknowledged(Boolean(disc.legal_declaration_acknowledged ?? true));

                    try {
                        const parsedChronic = typeof disc.chronic_diseases === 'string' ? JSON.parse(disc.chronic_diseases) : disc.chronic_diseases;
                        if (Array.isArray(parsedChronic)) setChronicConditions(parsedChronic);
                        else if (found.chronicDiseaseType) setChronicConditions([found.chronicDiseaseType]);
                    } catch {
                        if (found.chronicDiseaseType) setChronicConditions([found.chronicDiseaseType]);
                    }

                    try {
                        const parsedSurg = typeof disc.past_surgeries === 'string' ? JSON.parse(disc.past_surgeries) : disc.past_surgeries;
                        if (Array.isArray(parsedSurg)) setSurgeryDetails(parsedSurg.join('، '));
                        else if (typeof disc.past_surgeries === 'string') setSurgeryDetails(disc.past_surgeries);
                    } catch {}

                    try {
                        const parsedAllerg = typeof disc.allergies === 'string' ? JSON.parse(disc.allergies) : disc.allergies;
                        if (Array.isArray(parsedAllerg)) setAllergyDetails(parsedAllerg.join('، '));
                        else if (typeof disc.allergies === 'string') setAllergyDetails(disc.allergies);
                    } catch {}

                    try {
                        const parsedDev = typeof disc.medical_devices_needed === 'string' ? JSON.parse(disc.medical_devices_needed) : disc.medical_devices_needed;
                        if (Array.isArray(parsedDev)) setDeviceDetails(parsedDev.join('، '));
                        else if (typeof disc.medical_devices_needed === 'string') setDeviceDetails(disc.medical_devices_needed);
                    } catch {}

                    setMobilityStatus(found.mobilityStatus || (disc.has_mobility_limitation ? 'NEEDS_AID' : 'WALKS_LONG'));
                } else {
                    const isChronic = found.healthStatus === HealthStatus.CHRONIC || Boolean(found.chronicDiseaseType);
                    setHasChronicDisease(isChronic);
                    if (found.chronicDiseaseType) {
                        setChronicConditions(found.chronicDiseaseType.split(/[,،]/).map(s => s.trim()).filter(Boolean));
                    } else {
                        setChronicConditions([]);
                    }
                    const isDisab = found.healthStatus === HealthStatus.DISABLED || ['DIFFICULTY', 'NEEDS_AID', 'CANNOT_WALK'].includes(found.mobilityStatus || '');
                    setHasMobilityLimitation(isDisab);
                    setMobilityStatus(found.mobilityStatus || (isDisab ? 'NEEDS_AID' : 'WALKS_LONG'));
                    setHasRecentSurgery(false);
                    setSurgeryDetails('');
                    setHasAllergies(false);
                    setAllergyDetails('');
                    setHasMedicalDevices(false);
                    setDeviceDetails('');
                    setIsPregnant(false);
                    setGestationalWeeks('');
                    setRegularMedications(found.regularMedication || found.medication || '');
                    setHealthNotes(found.healthNotes || '');
                    setLegalDeclarationAcknowledged(true);
                }
            } else {
                setSearchError("لم يتم العثور على حاج بهذا الرقم الوطني، يرجى التحقق من الرقم والمحاولة مرة أخرى.");
            }
        } catch (error) {
            console.error(error);
            setSearchError("حدث خطأ أثناء البحث. يرجى التأكد من الاتصال بالشبكة والمحاولة مجدداً.");
        } finally {
            setLoading(false);
        }
    };

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            let base64 = '';
            try {
                base64 = await compressImageFile(file, 1280, 0.82);
            } catch (err) {
                console.warn('Compression fallback to raw reader:', err);
                base64 = await new Promise((res) => {
                    const reader = new FileReader();
                    reader.onloadend = () => res(reader.result as string);
                    reader.readAsDataURL(file);
                });
            }

            setFormData(prev => ({ ...prev, passportImageUrl: base64 }));

            // Automatically trigger Passport MRZ scanning
            setOcrResult(null);
            setOcrLoading(true);
            setOcrProgress({ percent: 5, text: 'جاري فحص صورة الجواز...' });
            try {
                const result = await readPassportImage(base64, (pct, statusText) => {
                    setOcrProgress({ percent: pct, text: statusText });
                });

                setOcrResult(result);

                if (result.success) {
                    setFormData(prev => ({
                        ...prev,
                        passportNumber: result.passportNumber || prev.passportNumber,
                        passportExpiryDate: result.passportExpiryDate || prev.passportExpiryDate
                    }));
                    setShowOcrConfirmModal(true);
                }
            } catch (ocrErr) {
                console.error('Passport OCR Reading Failed:', ocrErr);
                setOcrResult({ success: false, error: 'حدث خطأ أثناء قراءة صورة الجواز، يرجى إدخال البيانات يدوياً.' });
            } finally {
                setOcrLoading(false);
            }
        }
        // Allow re-selecting the same file
        e.target.value = '';
    };

    const digitsOnly = (v?: string) => (v || '').replace(/\D/g, '');

    const handleInitiateSubmit = (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!pilgrim) return;

        if (isLocked) {
            alert('عذراً، هذا الملف تم تأكيد مطابقته واعتماده رسمياً ولا يمكن تعديله من خلال البوابة.');
            return;
        }

        // Block submission if passport is expired according to Smart Sorting rules
        if (isPassportExpired) {
            alert(passportExpiryWarning || "عذراً، لا يمكن حفظ الطلب: جواز السفر غير صالح للاعتماد نظراً لقرب تاريخ انتهائه.");
            return;
        }

        const phoneDigits = digitsOnly(formData.phoneNumber);
        if (phoneDigits.length < 9) {
            alert('يرجى إدخال رقم هاتفك الشخصي الأساسي بشكل صحيح (مثال: 0912345678).');
            return;
        }

        // Mandatory Primary Phone WhatsApp selection (المتطلب الرابع: رقم الهاتف الشخصي الأساسي وحساب واتساب)
        if (!formData.primaryPhoneHasWhatsapp || formData.primaryPhoneHasWhatsapp === 'UNSPECIFIED') {
            alert('يرجى تحديد ما إذا كان رقم هاتفك الأساسي يستخدم تطبيق واتساب (نعم أو لا) في قسم «بيانات التواصل والطوارئ» قبل إرسال النموذج للاعتماد.');
            return;
        }

        const whatsappDigits = digitsOnly(formData.whatsappNumber);
        if (whatsappDigits.length < 9 || whatsappDigits.length > 15) {
            alert('يرجى إدخال رقم الواتساب الإضافي بشكل صحيح (مثال: 0912345678 أو 218912345678).');
            return;
        }

        // Advisory confirmation if WhatsApp number is identical to primary phone (not a blocking condition)
        if (whatsappDigits.length >= 9 && digitsOnly(formData.phoneNumber).length >= 9 && whatsappDigits.slice(-9) === digitsOnly(formData.phoneNumber).slice(-9)) {
            const proceed = confirm('تنبيه: رقم الواتساب المدخل مطابق لرقم هاتفك الأساسي.\nيُفضّل استخدام رقم إضافي مختلف إن وُجد لضمان بدائل للتواصل معك في حال تعذر الوصول للرقم الأول.\n\nهل ترغب في المتابعة وحفظ البيانات بهذا الرقم؟');
            if (!proceed) return;
        }

        if (!formData.office) {
            alert('يرجى اختيار المكتب الذي تتبع له.');
            return;
        }

        if (!legalDeclarationAcknowledged) {
            alert('يرجى تأكيد وقبول الصيغة القانونية للإقرار بصحة البيانات الصحية للمتابعة.');
            return;
        }

        // Open Confirmation Modal (المتطلب السادس)
        setShowSubmitConfirmModal(true);
    };

    const executeFinalSubmit = async () => {
        if (!pilgrim || loading) return;

        setLoading(true);
        try {
            const healthDisclosurePayload = {
                hasChronicDisease,
                conditionsDisclosed: chronicConditions,
                chronicDiseases: chronicConditions,
                hasMobilityLimitation,
                mobilityStatus,
                hasRecentSurgery,
                surgeryDetails: surgeryDetails.trim() || undefined,
                pastSurgeries: surgeryDetails.trim() ? [surgeryDetails.trim()] : undefined,
                hasAllergies,
                allergyDetails: allergyDetails.trim() || undefined,
                allergies: allergyDetails.trim() ? [allergyDetails.trim()] : undefined,
                hasMedicalDevices,
                deviceDetails: deviceDetails.trim() || undefined,
                medicalDevicesNeeded: deviceDetails.trim() ? [deviceDetails.trim()] : undefined,
                isPregnant: pilgrim.gender === 'FEMALE' ? isPregnant : false,
                gestationalWeeks: pilgrim.gender === 'FEMALE' && isPregnant && gestationalWeeks ? Number(gestationalWeeks) : undefined,
                regularMedications: regularMedications.trim() || undefined,
                notes: healthNotes.trim() || undefined,
                bloodType: formData.bloodType || undefined,
                legalDeclarationAcknowledged: legalDeclarationAcknowledged,
                declaredByName: pilgrim.fullName
            };

            const updatedData: Partial<Pilgrim> = {
                ...formData,
                healthStatus: hasMobilityLimitation ? HealthStatus.DISABLED : (hasChronicDisease ? HealthStatus.CHRONIC : HealthStatus.FIT),
                chronicDiseaseType: chronicConditions.length > 0 ? chronicConditions.join('، ') : undefined,
                regularMedication: regularMedications.trim() || undefined,
                mobilityStatus: mobilityStatus as any,
                healthNotes: healthNotes.trim() || undefined,
                passportExpiryDate: formatDateForInput(formData.passportExpiryDate) || undefined,
                lastUmrahDate: formatDateForInput(formData.lastUmrahDate) || undefined,
                linkedPilgrimId: formData.linkedPilgrimId ? formData.linkedPilgrimId : undefined,
                docStatus: DocStatus.RECEIVED,
                updatedViaLink: true,
            };

            // Verification uses the record's ORIGINAL identifiers (before any edits in this form)
            const response = await fetch(`/api/pilgrims/public/${pilgrim.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...updatedData,
                    healthDisclosure: healthDisclosurePayload,
                    verifier: { nationalId: pilgrim.nationalId, passportNumber: pilgrim.passportNumber },
                }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                const errMessage = errData.sqlMessage || errData.error || errData.message || 'فشل حفظ البيانات';
                throw new Error(errMessage);
            }

            const updatedPilgrim = await response.json();

            setShowSubmitConfirmModal(false);
            setOriginalPhoneNumber(updatedPilgrim.phoneNumber || '');
            onUpdate(updatedPilgrim);
            setPilgrim(updatedPilgrim);
            setSuccessMessage("تم حفظ وإرسال البيانات بنجاح! طلبك قيد المراجعة ويمكنك مراجعة وتعديل بياناتك في أي وقت حتى يتم تأكيد المطابقة رسمياً.");

            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (error: any) {
            console.error('Error saving pilgrim:', error);
            alert(error?.message ? `حدث خطأ أثناء الإرسال: ${error.message}` : "حدث خطأ أثناء حفظ البيانات، يرجى إعادة المحاولة.");
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        handleInitiateSubmit(e);
    };

    return (
        <div 
            className="min-h-screen bg-gradient-to-b from-stone-100 via-stone-50 to-stone-100 py-3 px-2 sm:py-8 sm:px-4 md:px-6 flex flex-col items-center justify-start text-stone-900 selection:bg-emerald-100 selection:text-emerald-900"
            dir="rtl"
            style={{ fontFamily: '"IBM Plex Sans Arabic", sans-serif' }}
        >
            {/* Top Container */}
            <div className="w-full max-w-4xl bg-white rounded-2xl sm:rounded-3xl shadow-xl shadow-stone-900/5 border border-stone-200/80 overflow-hidden">
                
                {/* Hero Header */}
                <div className="relative bg-gradient-to-br from-stone-900 via-stone-950 to-stone-900 text-white p-5 sm:p-8 text-center overflow-hidden">
                    {/* Ambient Glow */}
                    <div className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div className="absolute bottom-0 left-0 w-64 h-64 bg-teal-500/10 rounded-full blur-2xl pointer-events-none"></div>

                    <div className="relative z-10 flex flex-col items-center">
                        {/* Logo */}
                        <div className="mb-3 transition-transform duration-300 hover:scale-105">
                            <img 
                                src="/assets/meeqat-logo.svg" 
                                alt="ميقات" 
                                className="h-14 sm:h-16 w-auto drop-shadow-[0_4px_12px_rgba(0,0,0,0.4)]"
                                onError={(e) => {
                                    (e.target as HTMLElement).style.display = 'none';
                                }}
                            />
                        </div>

                        {/* Coordination Pill */}
                        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs sm:text-sm font-bold mb-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            <span>{coordinationInfo.name || 'تنسيقية طرابلس (ب)'}</span>
                        </div>

                        {/* Page Title */}
                        <h1 className="text-xl sm:text-2xl md:text-3xl font-black tracking-tight text-white mt-1">
                            استكمال وتحديث بيانات الحاج
                        </h1>

                        <p className="text-stone-300 text-xs sm:text-sm mt-1.5 max-w-lg mx-auto leading-relaxed opacity-90">
                            {pilgrim 
                                ? 'يرجى مراجعة وتحديث البيانات بدقة والتأكد من صحة رقم الهاتف ومرفقات الجواز'
                                : 'أدخل الرقم الوطني للتحقق من ملفك واستكمال الإجراءات الرسمية'
                            }
                        </p>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="p-3.5 sm:p-6 md:p-8">

                    {/* SCREEN 1: Search Form (When No Pilgrim Selected) */}
                    {!pilgrim && (
                        <div className="max-w-xl mx-auto py-2 sm:py-6 space-y-6">
                            
                            {/* Card for Search */}
                            <div className="bg-stone-50/80 rounded-2xl p-4 sm:p-6 border border-stone-200/80 shadow-sm">
                                <form onSubmit={handleSearch} className="space-y-4">
                                    <div className="space-y-1.5">
                                        <label className="text-xs sm:text-sm font-bold text-stone-700 flex items-center gap-1.5">
                                            <Search className="w-4 h-4 text-emerald-600" />
                                            الرقم الوطني للحاج
                                        </label>
                                        <div className="relative">
                                            <input
                                                type="text"
                                                inputMode="numeric"
                                                pattern="[0-9]*"
                                                maxLength={12}
                                                value={searchQuery}
                                                onChange={e => setSearchQuery(e.target.value.replace(/\D/g, ''))}
                                                placeholder="أدخل الرقم الوطني (12 رقماً)..."
                                                className="w-full pl-4 pr-11 py-3.5 sm:py-4 rounded-xl border border-stone-200 bg-white focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-600 focus:outline-none transition-all text-base sm:text-lg font-bold font-mono tracking-wider text-stone-900 placeholder:text-stone-400 placeholder:font-normal placeholder:tracking-normal shadow-sm"
                                                autoFocus
                                            />
                                            <Search className="absolute right-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-5 h-5" />
                                            {searchQuery && (
                                                <button
                                                    type="button"
                                                    onClick={() => setSearchQuery('')}
                                                    className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600 p-1"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    {searchError && (
                                        <div className="bg-rose-50 text-rose-700 p-3 sm:p-4 rounded-xl flex items-start gap-3 border border-rose-200 text-xs sm:text-sm font-semibold animate-in fade-in duration-200">
                                            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                                            <span>{searchError}</span>
                                        </div>
                                    )}

                                    <button
                                        type="submit"
                                        disabled={loading || !searchQuery.trim()}
                                        className="w-full bg-gradient-to-r from-stone-900 to-stone-800 hover:from-black hover:to-stone-900 text-white py-3.5 sm:py-4 rounded-xl font-black text-sm sm:text-base disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-stone-900/10 active:scale-[0.99] transition-all flex items-center justify-center gap-2"
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                <span>جارٍ التحقق والبحث...</span>
                                            </>
                                        ) : (
                                            <>
                                                <Search className="w-5 h-5" />
                                                <span>بحث عن الحاج</span>
                                            </>
                                        )}
                                    </button>
                                </form>
                            </div>

                            {/* Trust & Guidance Badges */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                                <div className="bg-white p-3.5 rounded-xl border border-stone-200/70 shadow-sm flex items-start gap-3">
                                    <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600 shrink-0">
                                        <ShieldCheck className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h4 className="text-xs font-bold text-stone-800">بيانات آمنة ومحمية</h4>
                                        <p className="text-[11px] text-stone-500 mt-0.5 leading-tight">حفظ مشفر وسري وفق معايير الخصوصية</p>
                                    </div>
                                </div>

                                <div className="bg-white p-3.5 rounded-xl border border-stone-200/70 shadow-sm flex items-start gap-3">
                                    <div className="p-2 rounded-lg bg-teal-50 text-teal-600 shrink-0">
                                        <Camera className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h4 className="text-xs font-bold text-stone-800">صورة الجواز</h4>
                                        <p className="text-[11px] text-stone-500 mt-0.5 leading-tight">يرجى تجهيز صورة واضحة لصفحة البيانات</p>
                                    </div>
                                </div>

                                <div className="bg-white p-3.5 rounded-xl border border-stone-200/70 shadow-sm flex items-start gap-3">
                                    <div className="p-2 rounded-lg bg-amber-50 text-amber-600 shrink-0">
                                        <Phone className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h4 className="text-xs font-bold text-stone-800">رقم الهاتف الفعّال</h4>
                                        <p className="text-[11px] text-stone-500 mt-0.5 leading-tight">لإرسال التنبيهات والإشعارات الهامة</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* SCREEN 2: Pilgrim Found & Form Loaded */}
                    {pilgrim && (
                        <form onSubmit={handleSubmit} className="space-y-5 sm:space-y-6 pb-20 sm:pb-6 animate-in fade-in duration-300">
                            
                            {/* Pilgrim Identity Banner (Sticky on Mobile) */}
                            <div className="bg-gradient-to-r from-stone-900 via-stone-800 to-stone-900 text-white rounded-2xl p-4 sm:p-5 shadow-lg border border-stone-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                <div className="flex items-center gap-3.5">
                                    <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-black text-xl flex items-center justify-center shrink-0 shadow-md">
                                        {pilgrim.gender === 'MALE' ? 'ح' : 'ح.ة'}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <h2 className="text-base sm:text-lg font-black text-white">{pilgrim.fullName}</h2>
                                            <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-white/10 text-emerald-300">
                                                {pilgrim.role === PilgrimRole.SUPERVISOR ? 'مشرف' : (pilgrim.role === PilgrimRole.COORDINATOR ? 'منسق' : 'حاج')}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-3 text-xs text-stone-300 mt-1 font-mono">
                                            <span>الوطني: <strong className="text-white">{pilgrim.nationalId}</strong></span>
                                            {pilgrim.lotteryNumber && (
                                                <span>• القرعة: <strong className="text-white">{pilgrim.lotteryNumber}</strong></span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between sm:justify-end gap-2 pt-2 sm:pt-0 border-t sm:border-t-0 border-white/10">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setPilgrim(null);
                                            setSearchQuery('');
                                            setSuccessMessage(null);
                                        }}
                                        className="text-xs font-bold text-stone-300 hover:text-white px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 transition-colors flex items-center gap-1.5"
                                    >
                                        <ArrowRight className="w-3.5 h-3.5 rotate-180" />
                                        <span>تغيير الحاج</span>
                                    </button>
                                </div>
                            </div>

                            {/* Success Notification */}
                            {successMessage && (
                                <div className="bg-emerald-50 text-emerald-900 p-4 rounded-2xl flex items-start gap-3 border border-emerald-200 shadow-sm animate-in fade-in">
                                    <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
                                    <div>
                                        <h4 className="font-black text-sm text-emerald-900">تم حفظ البيانات بنجاح!</h4>
                                        <p className="text-xs text-emerald-800 mt-0.5 leading-relaxed">{successMessage}</p>
                                    </div>
                                </div>
                            )}

                            {/* 1. Verified & Form Officially Locked Banner (المتطلب الثالث.2) */}
                            {isLocked && (
                                <div className="bg-emerald-50 text-emerald-950 p-4 sm:p-5 rounded-2xl flex items-start gap-3.5 border-2 border-emerald-300 shadow-md animate-in fade-in">
                                    <div className="p-2.5 bg-emerald-600 rounded-xl text-white shrink-0 shadow-sm">
                                        <Lock className="w-5 h-5" />
                                    </div>
                                    <div className="space-y-1.5 flex-1">
                                        <div className="flex items-center gap-2 flex-wrap justify-between">
                                            <h3 className="font-black text-sm sm:text-base text-emerald-950">
                                                تم تأكيد المطابقة والاعتماد رسميًا
                                            </h3>
                                            <span className="text-[11px] font-black px-2.5 py-0.5 rounded-full bg-emerald-200 text-emerald-900 border border-emerald-300">
                                                معتمد رسميًا - مقفل
                                            </span>
                                        </div>
                                        <p className="text-xs text-emerald-900/90 leading-relaxed font-medium">
                                            تمت مطابقة وتدقيق بياناتك رسميًا من قبل الموظف المخول في إدارة التنسيقية. النموذج الآن في وضع القراءة فقط ولا يمكن تعديل البيانات حفاظًا على دقة الربط مع السجل الطبي والتأشيرات.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* 2. Submitted & Editable Pending Verification Banner (المتطلب الثالث.1) */}
                            {isSubmittedPendingVerification && !isLocked && !successMessage && (
                                <div className="bg-sky-50 text-sky-950 p-4 sm:p-5 rounded-2xl flex items-start gap-3.5 border-2 border-sky-300 shadow-sm animate-in fade-in">
                                    <div className="p-2.5 bg-sky-600 rounded-xl text-white shrink-0 shadow-sm">
                                        <CheckCircle2 className="w-5 h-5" />
                                    </div>
                                    <div className="space-y-1.5 flex-1">
                                        <div className="flex items-center gap-2 flex-wrap justify-between">
                                            <h3 className="font-black text-sm sm:text-base text-sky-950">
                                                بياناتك محفوظة ومُرسلة للاعتماد
                                            </h3>
                                            <span className="text-[11px] font-black px-2.5 py-0.5 rounded-full bg-sky-200 text-sky-900 border border-sky-300">
                                                قابلة للتعديل حتى تأكيد المطابقة
                                            </span>
                                        </div>
                                        <p className="text-xs text-sky-900/90 leading-relaxed font-medium">
                                            لقد قمت بإرسال بياناتك بنجاح. يمكنك إعادة فتح هذا النموذج، وتعديل أي بيانات أو رفع واستبدال المستندات في أي وقت ما دامت المطابقة لم تُؤكَّد بعد من قبل المنسق الإداري.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* 3. UNIFIED DATA COMPLETION INDICATOR (المتطلب الخامس: مؤشر اكتمال البيانات في بوابة الحاج) */}
                            {completionResult && (
                                <div className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-5 border border-stone-200 shadow-md space-y-3.5">
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2 border-b border-stone-100">
                                        <div className="flex items-center gap-2.5">
                                            <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-black text-sm text-white shrink-0 shadow-sm ${
                                                completionResult.isComplete 
                                                    ? 'bg-emerald-600' 
                                                    : completionResult.percentage >= 70 
                                                    ? 'bg-teal-600' 
                                                    : completionResult.percentage >= 40 
                                                    ? 'bg-amber-600' 
                                                    : 'bg-rose-600'
                                            }`}>
                                                {completionResult.percentage}%
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <h3 className="text-sm sm:text-base font-black text-stone-900">
                                                        مؤشر اكتمال البيانات والمتطلبات
                                                    </h3>
                                                    {completionResult.isComplete ? (
                                                        <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                                                            <Check className="w-3 h-3" /> مكتمل 100%
                                                        </span>
                                                    ) : (
                                                        <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                                                            يتبقى {completionResult.totalRequirements - completionResult.fulfilledCount} متطلبات
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-[11px] text-stone-500 mt-0.5">
                                                    تم استيفاء {completionResult.fulfilledCount} من أصل {completionResult.totalRequirements} متطلباً أساسياً لإرسال ملفك للاعتماد
                                                </p>
                                            </div>
                                        </div>

                                        {!completionResult.isComplete && (
                                            <button
                                                type="button"
                                                onClick={() => setShowMissingFieldsDetails(!showMissingFieldsDetails)}
                                                className="text-xs font-bold text-amber-800 hover:text-amber-900 bg-amber-50 hover:bg-amber-100 px-3 py-1.5 rounded-xl border border-amber-200 transition-colors self-start sm:self-auto flex items-center gap-1.5"
                                            >
                                                <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                                                <span>{showMissingFieldsDetails ? 'إخفاء النواقص' : 'عرض قائمة النواقص'}</span>
                                            </button>
                                        )}
                                    </div>

                                    {/* Visual Progress Bar */}
                                    <div className="space-y-1">
                                        <div className="w-full bg-stone-100 rounded-full h-3 overflow-hidden p-0.5 border border-stone-200">
                                            <div 
                                                className={`h-full rounded-full transition-all duration-500 ${
                                                    completionResult.isComplete 
                                                        ? 'bg-gradient-to-r from-emerald-500 to-teal-600' 
                                                        : completionResult.percentage >= 70 
                                                        ? 'bg-gradient-to-r from-teal-500 to-emerald-600' 
                                                        : completionResult.percentage >= 40 
                                                        ? 'bg-gradient-to-r from-amber-500 to-yellow-500' 
                                                        : 'bg-gradient-to-r from-rose-500 to-red-600'
                                                }`}
                                                style={{ width: `${completionResult.percentage}%` }}
                                            />
                                        </div>
                                    </div>

                                    {/* Sections Breakdown Status Pills */}
                                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1 text-[11px] font-bold">
                                        {completionResult.sections.map((sec) => (
                                            <div 
                                                key={sec.id}
                                                className={`p-2 rounded-xl border flex items-center justify-between gap-1.5 ${
                                                    sec.isComplete 
                                                        ? 'bg-emerald-50/70 border-emerald-200 text-emerald-800' 
                                                        : 'bg-stone-50 border-stone-200 text-stone-700'
                                                }`}
                                            >
                                                <span className="truncate">{sec.title}</span>
                                                {sec.isComplete ? (
                                                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                                                ) : (
                                                    <span className="text-[10px] text-amber-700 bg-amber-100 px-1 rounded shrink-0">
                                                        {sec.fulfilled}/{sec.total}
                                                    </span>
                                                )}
                                            </div>
                                        ))}
                                    </div>

                                    {/* Expandable Missing Fields List (clickable to jump) */}
                                    {showMissingFieldsDetails && !completionResult.isComplete && (
                                        <div className="pt-2 border-t border-stone-100 animate-in fade-in duration-200">
                                            <p className="text-xs font-black text-rose-800 mb-2 flex items-center gap-1.5">
                                                <AlertCircle className="w-4 h-4 text-rose-600" />
                                                <span>الحقول والمتطلبات التي تحتاج إلى استكمال (انقر للانتقال):</span>
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {completionResult.missingFields.map((field) => (
                                                    <button
                                                        key={field.field}
                                                        type="button"
                                                        onClick={() => {
                                                            const el = document.getElementById(field.sectionId);
                                                            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                        }}
                                                        className="px-2.5 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-800 text-xs font-bold transition-colors flex items-center gap-1.5"
                                                    >
                                                        <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                                                        <span>{field.label}</span>
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* SECTION 1: Personal Info (Official Read-Only) */}
                            <div id="section-personal" className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-stone-200 shadow-sm space-y-4 scroll-mt-20">
                                <div className="flex items-center gap-2.5 pb-2 border-b border-stone-100">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-black text-sm shadow-sm shrink-0">
                                        1
                                    </div>
                                    <div>
                                        <h3 className="text-sm sm:text-base font-black text-stone-900">البيانات الشخصية المسجلة</h3>
                                        <p className="text-[11px] text-stone-500">بيانات رسمية مستخرجة من منظومة القرعة الوطنية</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-4">
                                    <div className="bg-stone-50/70 p-3 rounded-xl border border-stone-100">
                                        <span className="text-[11px] font-bold text-stone-400 block mb-0.5">الاسم الرباعي</span>
                                        <div className="font-black text-stone-900 text-xs sm:text-sm truncate">{pilgrim.fullName}</div>
                                    </div>

                                    <div className="bg-stone-50/70 p-3 rounded-xl border border-stone-100">
                                        <span className="text-[11px] font-bold text-stone-400 block mb-0.5">الرقم الوطني</span>
                                        <div className="font-mono font-black text-stone-900 text-xs sm:text-sm tracking-wide">{pilgrim.nationalId}</div>
                                    </div>

                                    <div className="bg-stone-50/70 p-3 rounded-xl border border-stone-100">
                                        <span className="text-[11px] font-bold text-stone-400 block mb-0.5">رقم القرعة</span>
                                        <div className="font-mono font-black text-stone-900 text-xs sm:text-sm">{pilgrim.lotteryNumber || '---'}</div>
                                    </div>

                                    <div className="bg-stone-50/70 p-3 rounded-xl border border-stone-100">
                                        <span className="text-[11px] font-bold text-stone-400 block mb-0.5">تاريخ الميلاد</span>
                                        <div className="font-mono font-black text-stone-900 text-xs sm:text-sm">{pilgrim.birthDate || '---'}</div>
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 2: Passport Information */}
                            <div id="section-passport" className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-stone-200 shadow-sm space-y-4 scroll-mt-20">
                                <div className="flex items-center gap-2.5 pb-2 border-b border-stone-100">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-black text-sm shadow-sm shrink-0">
                                        2
                                    </div>
                                    <div>
                                        <h3 className="text-sm sm:text-base font-black text-stone-900">بيانات جواز السفر</h3>
                                        <p className="text-[11px] text-stone-500">رقم الجواز وتاريخ الصلاحية وصورة واضحة</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                                    <div className="space-y-1">
                                        <div className="flex justify-between items-center">
                                            <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                                <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                                رقم الجواز
                                            </label>
                                            {ocrResult?.passportNumber && formData.passportNumber === ocrResult.passportNumber && (
                                                <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold flex items-center gap-1">
                                                    <ScanLine className="w-2.5 h-2.5" /> مطابق لشريط الجواز
                                                </span>
                                            )}
                                        </div>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.passportNumber || ''}
                                            onChange={e => setFormData({ ...formData, passportNumber: e.target.value.toUpperCase() })}
                                            placeholder="أدخل رقم الجواز..."
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold font-mono text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <div className="flex justify-between items-center">
                                            <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                                <Calendar className="w-3.5 h-3.5 text-emerald-600" />
                                                تاريخ انتهاء الجواز
                                            </label>
                                            {ocrResult?.passportExpiryDate && formData.passportExpiryDate === ocrResult.passportExpiryDate && (
                                                <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold flex items-center gap-1">
                                                    <ScanLine className="w-2.5 h-2.5" /> مطابق لشريط الجواز
                                                </span>
                                            )}
                                        </div>
                                        <input
                                            type="date"
                                            disabled={isLocked}
                                            value={formatDateForInput(formData.passportExpiryDate)}
                                            onChange={e => setFormData({ ...formData, passportExpiryDate: e.target.value })}
                                            className={`w-full px-3.5 py-3 sm:py-3.5 rounded-xl border font-bold font-mono text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all ${isPassportExpired ? 'border-red-500 bg-red-50 text-red-900 focus:ring-red-400' : 'border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-emerald-500/20 focus:border-emerald-600 text-stone-900'}`}
                                        />
                                    </div>
                                </div>

                                {/* Passport Validity Warning Banner if expired */}
                                {isPassportExpired && (
                                    <div className="p-4 rounded-2xl bg-red-50 border-2 border-red-300 text-red-900 space-y-2 animate-in fade-in slide-in-from-top-2">
                                        <div className="flex items-start gap-3">
                                            <AlertTriangle className="w-6 h-6 text-red-600 shrink-0 mt-0.5" />
                                            <div className="flex-1">
                                                <h4 className="font-bold text-sm sm:text-base text-red-800">
                                                    جواز السفر غير مطابق لشروط القبول (منتهي أو قريب الانتهاء)
                                                </h4>
                                                <p className="text-xs sm:text-sm text-red-700 mt-1 leading-relaxed">
                                                    {passportExpiryWarning}
                                                </p>
                                                <div className="mt-2 text-xs font-semibold text-red-800 bg-red-100/70 py-1.5 px-3 rounded-lg inline-block border border-red-200">
                                                    الحد الأدنى المعتمد لصلاحية الجواز: <span className="font-mono font-bold text-red-950">{passportRules.minPassportExpiryDate}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Passport Image Upload Card */}
                                <div className="pt-2">
                                    <div className="flex justify-between items-center mb-1.5">
                                        <label className="text-xs font-bold text-stone-700">
                                            صورة جواز السفر (الصفحة الأولى وبطاقة البيانات)
                                        </label>
                                        <span className="text-[11px] text-teal-700 font-semibold flex items-center gap-1">
                                            <ScanLine className="w-3.5 h-3.5" /> قراءة آلية لشريط الجواز (MRZ)
                                        </span>
                                    </div>

                                    {/* OCR Processing Active Card */}
                                    {ocrLoading && (
                                        <div className="mb-4 p-5 rounded-2xl bg-emerald-50 border-2 border-emerald-300 text-emerald-900 shadow-sm space-y-3 animate-in fade-in">
                                            <div className="flex items-center gap-3">
                                                <Loader2 className="w-6 h-6 text-emerald-600 animate-spin" />
                                                <div className="flex-1">
                                                    <div className="font-bold text-sm text-emerald-950">
                                                        جاري قراءة شريط الجواز (MRZ) والتحقق منه...
                                                    </div>
                                                    <div className="text-xs text-emerald-700 mt-0.5">
                                                        {ocrProgress.text}
                                                    </div>
                                                </div>
                                                <span className="text-sm font-black font-mono text-emerald-700">
                                                    {ocrProgress.percent}%
                                                </span>
                                            </div>
                                            <div className="w-full bg-emerald-200 rounded-full h-2 overflow-hidden">
                                                <div 
                                                    className="bg-emerald-600 h-full rounded-full transition-all duration-300"
                                                    style={{ width: `${ocrProgress.percent}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    )}

                                    {!ocrLoading && ocrResult && !ocrResult.success && (
                                        <div className="mb-4 p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 flex items-start gap-3 animate-in fade-in">
                                            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                                            <div className="text-xs leading-relaxed space-y-1">
                                                <p className="font-bold text-sm">تعذرت القراءة الآلية للجواز</p>
                                                <p>{ocrResult.error}</p>
                                                <p className="text-amber-700">نصيحة: ضع الجواز على سطح داكن، وصوّر الصفحة كاملة بشكل مستقيم وبإضاءة جيدة دون فلاش، مع ظهور السطرين السفليين بوضوح.</p>
                                            </div>
                                        </div>
                                    )}

                                    {!ocrLoading && ocrResult?.success && !ocrResult.verified && (
                                        <div className="mb-4 p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 flex items-start gap-3 animate-in fade-in">
                                            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                                            <div className="text-xs leading-relaxed">
                                                <p className="font-bold text-sm">قراءة جزئية</p>
                                                <p>تم تعبئة الحقول التي تطابقت مع خانات التدقيق فقط. يرجى مراجعة وإكمال باقي الحقول يدوياً من صفحة الجواز.</p>
                                            </div>
                                        </div>
                                    )}

                                    {formData.passportImageUrl ? (
                                        <div className="relative bg-stone-50 rounded-2xl p-3 border border-stone-200 flex flex-col sm:flex-row items-center gap-4">
                                            <div 
                                                onClick={() => setPreviewImage(formData.passportImageUrl || null)}
                                                className="relative w-full sm:w-48 aspect-[3/2] rounded-xl overflow-hidden shadow-sm cursor-pointer group bg-stone-200 shrink-0"
                                            >
                                                <img 
                                                    src={formData.passportImageUrl} 
                                                    alt="Passport Preview" 
                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                                                />
                                                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold gap-1">
                                                    <Eye className="w-4 h-4" />
                                                    <span>معاينة مكبرة</span>
                                                </div>
                                            </div>

                                            <div className="flex-1 text-center sm:text-right space-y-2">
                                                <div className="flex items-center justify-center sm:justify-start gap-2 text-emerald-700 font-bold text-xs">
                                                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                                    <span>تم إرفاق صورة الجواز بنجاح</span>
                                                </div>
                                                <p className="text-[11px] text-stone-500">يمكنك النقر على الصورة لمعاينتها بحجم كامل</p>

                                                {!isLocked && (
                                                    <div className="flex items-center justify-center sm:justify-start gap-2 pt-1">
                                                        <label className="px-3.5 py-2 rounded-xl bg-white border border-stone-300 hover:border-emerald-500 text-stone-700 hover:text-emerald-700 text-xs font-bold cursor-pointer transition-colors flex items-center gap-1.5 shadow-sm">
                                                            <Camera className="w-3.5 h-3.5" />
                                                            <span>تغيير الصورة</span>
                                                            <input
                                                                type="file"
                                                                accept="image/*"
                                                                capture="environment"
                                                                onChange={handleImageUpload}
                                                                className="hidden"
                                                            />
                                                        </label>
                                                        <button
                                                            type="button"
                                                            onClick={() => setFormData({ ...formData, passportImageUrl: '' })}
                                                            className="px-3 py-2 rounded-xl bg-white border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-bold transition-colors shadow-sm"
                                                        >
                                                            حذف
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className={`border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center transition-all ${isLocked ? 'border-stone-200 bg-stone-50 opacity-60' : 'border-stone-300 hover:border-emerald-500 bg-stone-50/50 hover:bg-emerald-50/20 cursor-pointer'} relative group`}>
                                            <input
                                                type="file"
                                                accept="image/*"
                                                capture="environment"
                                                disabled={isLocked}
                                                onChange={handleImageUpload}
                                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10 disabled:cursor-not-allowed"
                                            />
                                            <div className="flex flex-col items-center gap-2.5 text-stone-500">
                                                <div className="w-12 h-12 rounded-2xl bg-white shadow-sm border border-stone-200 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                                                    <Camera className="w-6 h-6" />
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="font-bold text-stone-800 text-sm">
                                                        التقاط صورة بالجوال أو اختيار ملف
                                                    </p>
                                                    <p className="text-[11px] text-stone-500">
                                                        يدعم كاميرا الهاتف وملفات JPG, PNG (صورة واضحة لبيانات الجواز)
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* SECTION 3: Electronic Health Disclosure Form (استمارة الإفصاح الصحي الإلكتروني) */}
                            <div id="section-health" className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border-2 border-rose-200/80 shadow-md space-y-6 relative overflow-hidden scroll-mt-20">
                                {/* Ambient glow */}
                                <div className="absolute top-0 left-0 w-72 h-72 bg-rose-500/5 rounded-full blur-3xl pointer-events-none"></div>

                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-stone-200 relative z-10">
                                    <div className="flex items-center gap-3">
                                        <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-rose-600 to-pink-700 text-white flex items-center justify-center font-black text-sm shadow-md shadow-rose-600/20 shrink-0">
                                            3
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <h3 className="text-base sm:text-lg font-black text-stone-900">استمارة الإفصاح الصحي الإلكتروني</h3>
                                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-black border border-rose-200">
                                                    <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-pulse"></span>
                                                    موسم 1448هـ
                                                </span>
                                            </div>
                                            <p className="text-[11px] text-stone-500 mt-0.5">
                                                يتم ترحيل هذه الإجابات مباشرة إلى سجلك الطبي الرقمي وتطبيق اشتراطات اللياقة الطبية للبعثة
                                            </p>
                                        </div>
                                    </div>

                                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-50 border border-rose-200/80 text-rose-700 text-xs font-bold self-start sm:self-auto">
                                        <Stethoscope className="w-4 h-4 text-rose-600 shrink-0" />
                                        <span>مرتبط بالسجل الطبي الموحد</span>
                                    </div>
                                </div>

                                <div className="space-y-5 relative z-10">

                                    {/* Question 1: Chronic Diseases */}
                                    <div className="bg-stone-50/70 rounded-2xl p-4 border border-stone-200/80 space-y-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <div className="space-y-0.5">
                                                <div className="text-xs sm:text-sm font-black text-stone-900 flex items-center gap-1.5">
                                                    <HeartPulse className="w-4 h-4 text-rose-600 shrink-0" />
                                                    <span>1. هل تعاني من أي أمراض مزمنة أو تتلقى علاجاً دورياً؟</span>
                                                </div>
                                                <p className="text-[11px] text-stone-500">
                                                    مثل: السكري، ضغط الدم، أمراض القلب، الكلى، أو الجهاز التنفسي
                                                </p>
                                            </div>

                                            <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-stone-200 shrink-0">
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasChronicDisease(false)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${!hasChronicDisease ? 'bg-emerald-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    لا
                                                </button>
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasChronicDisease(true)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${hasChronicDisease ? 'bg-rose-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    نعم
                                                </button>
                                            </div>
                                        </div>

                                        {hasChronicDisease && (
                                            <div className="pt-3 border-t border-stone-200 space-y-3 animate-in fade-in duration-200">
                                                <label className="text-xs font-bold text-stone-700 block">
                                                    حدد الأمراض المزمنة المشخصة بدقة:
                                                </label>
                                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                                    {[
                                                        'السكري',
                                                        'ارتفاع ضغط الدم',
                                                        'أمراض القلب / دعامات / قسطرة',
                                                        'قصور في وظائف الكلى',
                                                        'غسيل كلوي دموي',
                                                        'أمراض الجهاز التنفسي / ربو مزمن / تليف',
                                                        'أمراض الكبد',
                                                        'أورام / علاج كيميائي',
                                                        'أمراض عصبية / تشنجات / صرع',
                                                        'روماتيزم / التهاب مفاصل حاد'
                                                    ].map(disease => {
                                                        const isSelected = chronicConditions.includes(disease);
                                                        return (
                                                            <div
                                                                key={disease}
                                                                onClick={() => {
                                                                    if (isLocked) return;
                                                                    if (isSelected) {
                                                                        setChronicConditions(chronicConditions.filter(x => x !== disease));
                                                                    } else {
                                                                        setChronicConditions([...chronicConditions, disease]);
                                                                    }
                                                                }}
                                                                className={`p-2.5 rounded-xl border text-xs font-bold flex items-center justify-between gap-2 transition-all ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.98]'} ${isSelected ? 'bg-rose-50 border-rose-300 text-rose-950 font-black shadow-sm' : 'bg-white border-stone-200 text-stone-700 hover:border-stone-300'}`}
                                                            >
                                                                <span className="truncate">{disease}</span>
                                                                <div className={`w-4 h-4 rounded flex items-center justify-center border shrink-0 transition-colors ${isSelected ? 'bg-rose-600 border-rose-600 text-white' : 'border-stone-300 bg-white'}`}>
                                                                    {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>

                                                {/* Add other condition */}
                                                <div className="flex items-center gap-2 pt-1">
                                                    <input
                                                        type="text"
                                                        disabled={isLocked}
                                                        value={customChronicCondition}
                                                        onChange={e => setCustomChronicCondition(e.target.value)}
                                                        placeholder="إضافة مرض مزمن آخر غير مدرج..."
                                                        className="flex-1 px-3 py-2 rounded-xl border border-stone-300 bg-white text-xs text-stone-800 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-600"
                                                        onKeyDown={e => {
                                                            if (e.key === 'Enter') {
                                                                e.preventDefault();
                                                                if (customChronicCondition.trim() && !chronicConditions.includes(customChronicCondition.trim())) {
                                                                    setChronicConditions([...chronicConditions, customChronicCondition.trim()]);
                                                                    setCustomChronicCondition('');
                                                                }
                                                            }
                                                        }}
                                                    />
                                                    <button
                                                        type="button"
                                                        disabled={isLocked || !customChronicCondition.trim()}
                                                        onClick={() => {
                                                            if (customChronicCondition.trim() && !chronicConditions.includes(customChronicCondition.trim())) {
                                                                setChronicConditions([...chronicConditions, customChronicCondition.trim()]);
                                                                setCustomChronicCondition('');
                                                            }
                                                        }}
                                                        className="px-3 py-2 rounded-xl bg-stone-800 text-white text-xs font-bold hover:bg-stone-900 disabled:opacity-40 transition-colors flex items-center gap-1 shrink-0"
                                                    >
                                                        <Plus className="w-3.5 h-3.5" />
                                                        <span>إضافة</span>
                                                    </button>
                                                </div>

                                                {chronicConditions.length > 0 && (
                                                    <div className="flex flex-wrap gap-1.5 pt-1">
                                                        {chronicConditions.map(item => (
                                                            <span key={item} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-rose-100 text-rose-900 text-xs font-bold border border-rose-200">
                                                                <span>{item}</span>
                                                                {!isLocked && (
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => setChronicConditions(chronicConditions.filter(x => x !== item))}
                                                                        className="hover:text-rose-600"
                                                                    >
                                                                        <X className="w-3 h-3" />
                                                                    </button>
                                                                )}
                                                            </span>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Question 2: Mobility and Walking Assessment */}
                                    <div className="bg-stone-50/70 rounded-2xl p-4 border border-stone-200/80 space-y-3">
                                        <div className="space-y-0.5">
                                            <div className="text-xs sm:text-sm font-black text-stone-900 flex items-center gap-1.5">
                                                <Activity className="w-4 h-4 text-emerald-600 shrink-0" />
                                                <span>2. تقييم القدرة الحركية والمشي لمسافات طويلة</span>
                                            </div>
                                            <p className="text-[11px] text-stone-500">
                                                يحدد خطة التسكين، قربه من الحرم والمصاعد، واشتراط مرافق مساعد
                                            </p>
                                        </div>

                                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                                            {[
                                                { id: 'WALKS_LONG', label: 'طبيعي - يمشي مسافات طويلة', desc: 'بدون عكاز أو صعوبة', icon: '🚶‍♂️' },
                                                { id: 'WALKS_SHORT', label: 'يمشي مسافات قصيرة فقط', desc: 'يتعب سريعاً في المسافات الطويلة', icon: '🚶' },
                                                { id: 'DIFFICULTY', label: 'صعوبة في المشي', desc: 'يحتاج راحة متكررة ومساعدة خفيفة', icon: '⚠️' },
                                                { id: 'NEEDS_AID', label: 'يحتاج عكاز أو عصا للمشي', desc: 'يعتمد على وسيلة مساعدة', icon: '🦯' },
                                                { id: 'CANNOT_WALK', label: 'كرسي متحرك دائماً / مقعد', desc: 'لا يستطيع المشي إطلاقاً', icon: '♿' }
                                            ].map(opt => {
                                                const isCurrent = mobilityStatus === opt.id;
                                                return (
                                                    <div
                                                        key={opt.id}
                                                        onClick={() => {
                                                            if (isLocked) return;
                                                            setMobilityStatus(opt.id);
                                                            if (opt.id === 'NEEDS_AID' || opt.id === 'CANNOT_WALK' || opt.id === 'DIFFICULTY') {
                                                                setHasMobilityLimitation(true);
                                                            } else {
                                                                setHasMobilityLimitation(false);
                                                            }
                                                        }}
                                                        className={`p-3 rounded-xl border text-right transition-all ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.98]'} ${isCurrent ? 'bg-emerald-50 border-emerald-400 text-emerald-950 shadow-sm font-bold ring-2 ring-emerald-500/20' : 'bg-white border-stone-200 text-stone-700 hover:border-stone-300'}`}
                                                    >
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className="text-base">{opt.icon}</span>
                                                            <div className={`w-4 h-4 rounded-full flex items-center justify-center border ${isCurrent ? 'border-emerald-600 bg-emerald-600 text-white' : 'border-stone-300 bg-white'}`}>
                                                                {isCurrent && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                                                            </div>
                                                        </div>
                                                        <div className="text-xs font-black">{opt.label}</div>
                                                        <div className="text-[10px] text-stone-500 font-normal mt-0.5">{opt.desc}</div>
                                                    </div>
                                                );
                                            })}
                                        </div>

                                        {/* Wheelchair explicit check */}
                                        <div 
                                            onClick={() => {
                                                if (!isLocked) setHasMobilityLimitation(!hasMobilityLimitation);
                                            }}
                                            className={`p-3 rounded-xl border flex items-center justify-between gap-3 transition-colors ${isLocked ? 'cursor-default' : 'cursor-pointer'} ${hasMobilityLimitation ? 'bg-amber-50 border-amber-300 text-amber-950 font-bold' : 'bg-white border-stone-200 text-stone-700'}`}
                                        >
                                            <div className="text-xs">
                                                <span className="font-bold block">هل تحتاج كرسي متحرك أثناء الطواف والسعي والتنقل في المشاعر؟</span>
                                                <span className="text-[11px] text-stone-500 font-normal">تشترط الهيئة وجود مرافق ملازم للحاج مستخدم الكرسي المتحرك</span>
                                            </div>
                                            <div className={`w-5 h-5 rounded-md flex items-center justify-center border shrink-0 transition-colors ${hasMobilityLimitation ? 'bg-amber-600 border-amber-600 text-white' : 'border-stone-300 bg-white'}`}>
                                                {hasMobilityLimitation && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Question 3: Recent Surgery or Hospitalization */}
                                    <div className="bg-stone-50/70 rounded-2xl p-4 border border-stone-200/80 space-y-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <div className="space-y-0.5">
                                                <div className="text-xs sm:text-sm font-black text-stone-900 flex items-center gap-1.5">
                                                    <FileText className="w-4 h-4 text-indigo-600 shrink-0" />
                                                    <span>3. هل خضعت لأي عمليات جراحية أو تنويم بالمستشفى خلال آخر 6 أشهر؟</span>
                                                </div>
                                                <p className="text-[11px] text-stone-500">
                                                    تتطلب العمليات الجراحية تقريراً طبياً يثبت التئام الجروح واستقرار الحالة للسفر
                                                </p>
                                            </div>

                                            <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-stone-200 shrink-0">
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasRecentSurgery(false)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${!hasRecentSurgery ? 'bg-emerald-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    لا
                                                </button>
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasRecentSurgery(true)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${hasRecentSurgery ? 'bg-indigo-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    نعم
                                                </button>
                                            </div>
                                        </div>

                                        {hasRecentSurgery && (
                                            <div className="pt-2 animate-in fade-in duration-200">
                                                <label className="text-xs font-bold text-stone-700 block mb-1">
                                                    حدد نوع العملية الجراحية أو سبب التنويم وتاريخها التقريبي:
                                                </label>
                                                <input
                                                    type="text"
                                                    disabled={isLocked}
                                                    value={surgeryDetails}
                                                    onChange={e => setSurgeryDetails(e.target.value)}
                                                    placeholder="مثال: جراحة قسطرة قلبية في شهر يناير 2026، استئصال مرارة..."
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs text-stone-800 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 font-medium"
                                                />
                                            </div>
                                        )}
                                    </div>

                                    {/* Question 4: Allergies */}
                                    <div className="bg-stone-50/70 rounded-2xl p-4 border border-stone-200/80 space-y-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <div className="space-y-0.5">
                                                <div className="text-xs sm:text-sm font-black text-stone-900 flex items-center gap-1.5">
                                                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                                                    <span>4. هل تعاني من حساسية مفرطة معروفة (أدوية معينة أو أطعمة)؟</span>
                                                </div>
                                                <p className="text-[11px] text-stone-500">
                                                    مثل: حساسية البنسلين، أدوية السلفا، حساسية الفول، الأسبرين
                                                </p>
                                            </div>

                                            <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-stone-200 shrink-0">
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasAllergies(false)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${!hasAllergies ? 'bg-emerald-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    لا
                                                </button>
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasAllergies(true)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${hasAllergies ? 'bg-amber-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    نعم
                                                </button>
                                            </div>
                                        </div>

                                        {hasAllergies && (
                                            <div className="pt-2 animate-in fade-in duration-200">
                                                <label className="text-xs font-bold text-stone-700 block mb-1">
                                                    حدد المواد أو الأدوية المسببة للحساسية:
                                                </label>
                                                <input
                                                    type="text"
                                                    disabled={isLocked}
                                                    value={allergyDetails}
                                                    onChange={e => setAllergyDetails(e.target.value)}
                                                    placeholder="مثال: حساسية شديدة من البنسلين ومشتقاته..."
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs text-stone-800 focus:ring-2 focus:ring-amber-500/20 focus:border-amber-600 font-medium"
                                                />
                                            </div>
                                        )}
                                    </div>

                                    {/* Question 5: Medical Devices Needed */}
                                    <div className="bg-stone-50/70 rounded-2xl p-4 border border-stone-200/80 space-y-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <div className="space-y-0.5">
                                                <div className="text-xs sm:text-sm font-black text-stone-900 flex items-center gap-1.5">
                                                    <Pill className="w-4 h-4 text-teal-600 shrink-0" />
                                                    <span>5. هل تستخدم أجهزة أو معدات طبية خاصة أثناء النوم أو التنقل؟</span>
                                                </div>
                                                <p className="text-[11px] text-stone-500">
                                                    مثل: أسطوانة أكسجين، جهاز ضخ الأنسولين، جهاز التنفس أثناء النوم CPAP
                                                </p>
                                            </div>

                                            <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-stone-200 shrink-0">
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasMedicalDevices(false)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${!hasMedicalDevices ? 'bg-emerald-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    لا
                                                </button>
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setHasMedicalDevices(true)}
                                                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${hasMedicalDevices ? 'bg-teal-600 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                >
                                                    نعم
                                                </button>
                                            </div>
                                        </div>

                                        {hasMedicalDevices && (
                                            <div className="pt-2 animate-in fade-in duration-200">
                                                <label className="text-xs font-bold text-stone-700 block mb-1">
                                                    حدد نوع الأجهزة الطبية المستخدمة:
                                                </label>
                                                <input
                                                    type="text"
                                                    disabled={isLocked}
                                                    value={deviceDetails}
                                                    onChange={e => setDeviceDetails(e.target.value)}
                                                    placeholder="مثال: جهاز CPAP للتنفس أثناء النوم، جهاز مضخة أنسولين..."
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs text-stone-800 focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 font-medium"
                                                />
                                            </div>
                                        )}
                                    </div>

                                    {/* Question 6: Pregnancy (Female pilgrims only) */}
                                    {pilgrim.gender === 'FEMALE' && (
                                        <div className="bg-purple-50/50 rounded-2xl p-4 border border-purple-200 space-y-3">
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="space-y-0.5">
                                                    <div className="text-xs sm:text-sm font-black text-purple-950 flex items-center gap-1.5">
                                                        <Baby className="w-4 h-4 text-purple-600 shrink-0" />
                                                        <span>6. هل توجد حالة حمل حالياً؟ (خاص بالحاجات)</span>
                                                    </div>
                                                    <p className="text-[11px] text-purple-700">
                                                        وفق اشتراطات الطيران واللجنة الطبية، يخضع سفر الحامل لضوابط أسبوع الحمل
                                                    </p>
                                                </div>

                                                <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-purple-200 shrink-0">
                                                    <button
                                                        type="button"
                                                        disabled={isLocked}
                                                        onClick={() => setIsPregnant(false)}
                                                        className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${!isPregnant ? 'bg-purple-700 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                    >
                                                        لا
                                                    </button>
                                                    <button
                                                        type="button"
                                                        disabled={isLocked}
                                                        onClick={() => setIsPregnant(true)}
                                                        className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${isPregnant ? 'bg-purple-700 text-white shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}
                                                    >
                                                        نعم
                                                    </button>
                                                </div>
                                            </div>

                                            {isPregnant && (
                                                <div className="pt-2 flex flex-col sm:flex-row sm:items-center gap-3 animate-in fade-in duration-200">
                                                    <div className="space-y-1">
                                                        <label className="text-xs font-bold text-stone-700 block">
                                                            أسبوع الحمل الحالي:
                                                        </label>
                                                        <input
                                                            type="number"
                                                            min="1"
                                                            max="42"
                                                            disabled={isLocked}
                                                            value={gestationalWeeks}
                                                            onChange={e => setGestationalWeeks(e.target.value ? Number(e.target.value) : '')}
                                                            placeholder="مثال: 18"
                                                            className="w-32 px-3.5 py-2 rounded-xl border border-purple-300 bg-white text-xs font-bold text-center focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                                                        />
                                                    </div>
                                                    <p className="text-[11px] text-purple-800 bg-white/80 p-2.5 rounded-xl border border-purple-200 leading-relaxed flex-1">
                                                        ⚠️ تنبيه طبي: الحمل في الأشهر الأخيرة (ما بعد الأسبوع 28) قد يتطلب تقريراً اختصاصياً يثبت سلامة السفر وأداء المناسك.
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Question 7: Regular Medications & Blood Type */}
                                    <div className="bg-stone-50/70 rounded-2xl p-4 border border-stone-200/80 space-y-4">
                                        <div className="space-y-0.5">
                                            <div className="text-xs sm:text-sm font-black text-stone-900 flex items-center gap-1.5">
                                                <Heart className="w-4 h-4 text-rose-500 shrink-0" />
                                                <span>7. قائمة الأدوية المستمرة وفصيلة الدم والتقييم الصحي</span>
                                            </div>
                                            <p className="text-[11px] text-stone-500">
                                                تسجيل الأدوية المستمرة لضمان توفيرها أو استمراريتها في الأراضي المقدسة
                                            </p>
                                        </div>

                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                                            <div className="space-y-1 sm:col-span-2">
                                                <label className="text-xs font-bold text-stone-700 block">
                                                    الأدوية المستعملة بانتظام والجرعات:
                                                </label>
                                                <textarea
                                                    rows={2}
                                                    disabled={isLocked}
                                                    value={regularMedications}
                                                    onChange={e => setRegularMedications(e.target.value)}
                                                    placeholder="أدخل أسماء الأدوية بوضوح (مثال: إنسولين لانتوس 20 وحدة، كونكور 5 ملغ، جلوكوفاج 500)..."
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs text-stone-800 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-medium resize-none"
                                                />
                                            </div>

                                            <div className="space-y-1">
                                                <label className="text-xs font-bold text-stone-700">فصيلة الدم</label>
                                                <select
                                                    disabled={isLocked}
                                                    value={formData.bloodType || ''}
                                                    onChange={e => setFormData({ ...formData, bloodType: e.target.value })}
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs font-bold text-stone-900 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 disabled:opacity-60"
                                                >
                                                    <option value="">غير محدد</option>
                                                    {BLOOD_TYPES.map(bt => <option key={bt} value={bt}>{bt}</option>)}
                                                </select>
                                            </div>

                                            <div className="space-y-1">
                                                <label className="text-xs font-bold text-stone-700">التقييم الذاتي للحالة الصحية (من 10)</label>
                                                <input
                                                    type="number"
                                                    min="1"
                                                    max="10"
                                                    disabled={isLocked}
                                                    value={formData.healthRating || ''}
                                                    onChange={e => setFormData({ ...formData, healthRating: Number(e.target.value) })}
                                                    placeholder="10"
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs font-bold text-stone-900 text-center focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 disabled:opacity-60"
                                                />
                                            </div>

                                            <div className="space-y-1 sm:col-span-2">
                                                <label className="text-xs font-bold text-stone-700 block">
                                                    ملاحظات أو تنبيهات صحية إضافية ترغب بإبلاغ الفريق الطبي بها:
                                                </label>
                                                <textarea
                                                    rows={2}
                                                    disabled={isLocked}
                                                    value={healthNotes}
                                                    onChange={e => setHealthNotes(e.target.value)}
                                                    placeholder="اكتب هنا أي تفاصيل صحية أخرى تود توضيحها للفريق الطبي المشرف..."
                                                    className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-white text-xs text-stone-800 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-medium resize-none"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Question 8: Mandatory Legal Declaration */}
                                    <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-amber-50 to-rose-50/50 border-2 border-amber-300/80 shadow-sm space-y-3">
                                        <div className="flex items-center gap-2 text-amber-900 font-black text-xs sm:text-sm">
                                            <ShieldCheck className="w-5 h-5 text-amber-700 shrink-0" />
                                            <span>الصيغة القانونية المعتمدة للإقرار الصحي (موسم 1448هـ)</span>
                                        </div>

                                        <p className="text-xs text-stone-800 leading-relaxed font-medium bg-white/70 p-3 rounded-xl border border-amber-200">
                                            «أقر أنا الحاج المذكور أعلاه بصحة ودقة جميع البيانات الصحية المصرح بها في هذه الاستمارة، وخلوها من أي إخفاء عمدي لأي مرض حرج أو عارض صحي يستوجب رعاية خاصة أو يشكل مانعاً من السفر، وأتحمل كامل المسؤولية النظامية والطبية المترتبة على ذلك أمام اللجنة الطبية وإدارة البعثة.»
                                        </p>

                                        <label className="flex items-start gap-3 cursor-pointer pt-1">
                                            <input
                                                type="checkbox"
                                                required
                                                disabled={isLocked}
                                                checked={legalDeclarationAcknowledged}
                                                onChange={e => setLegalDeclarationAcknowledged(e.target.checked)}
                                                className="w-5 h-5 rounded text-rose-600 focus:ring-rose-500 mt-0.5 shrink-0 cursor-pointer"
                                            />
                                            <span className="text-xs font-bold text-stone-900 leading-normal">
                                                أوافق وأقر بصحة البيانات الصحية المدخلة وأتعهد بالمسؤولية الكاملة عنها. <span className="text-rose-600">*</span>
                                            </span>
                                        </label>
                                    </div>

                                </div>
                            </div>

                            {/* SECTION 4: Contact & Emergency */}
                            <div className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-stone-200 shadow-sm space-y-4">
                                <div className="flex items-center gap-2.5 pb-2 border-b border-stone-100">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-black text-sm shadow-sm shrink-0">
                                        4
                                    </div>
                                    <div>
                                        <h3 className="text-sm sm:text-base font-black text-stone-900">بيانات التواصل والطوارئ</h3>
                                        <p className="text-[11px] text-stone-500">أرقام هواتف للتواصل السريع والمباشر</p>
                                    </div>
                                </div>

                                <div id="section-contact" className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                            <Phone className="w-3.5 h-3.5 text-emerald-600" />
                                            رقم هاتفك الشخصي (الأساسي) <span className="text-rose-500">*</span>
                                        </label>
                                        <input
                                            type="tel"
                                            inputMode="tel"
                                            style={{ direction: 'ltr', textAlign: 'right' }}
                                            disabled={isLocked}
                                            value={formData.phoneNumber || ''}
                                            onChange={e => setFormData({ ...formData, phoneNumber: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold font-mono text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="09X XXXXXXX"
                                        />

                                        {/* Primary Phone WhatsApp Option (المتطلب الرابع: رقم الهاتف الشخصي الأساسي وحساب واتساب) */}
                                        <div className="p-3 rounded-xl border bg-stone-50/90 border-stone-200 space-y-2">
                                            <div className="flex items-center justify-between gap-2">
                                                <span className="text-xs font-black text-stone-800 flex items-center gap-1.5">
                                                    <MessageCircle className="w-3.5 h-3.5 text-emerald-600" />
                                                    هل هذا الرقم الأساسي مرتبط بحساب واتساب؟ <span className="text-rose-600">*</span>
                                                </span>
                                                {formData.primaryPhoneHasWhatsapp === 'YES' ? (
                                                    <span className="text-[10px] font-black text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-md border border-emerald-200">
                                                        واتساب: نعم
                                                    </span>
                                                ) : formData.primaryPhoneHasWhatsapp === 'NO' ? (
                                                    <span className="text-[10px] font-black text-stone-700 bg-stone-200 px-2.5 py-0.5 rounded-md">
                                                        واتساب: لا
                                                    </span>
                                                ) : (
                                                    <span className="text-[10px] font-black text-rose-700 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200 animate-pulse">
                                                        مطلوب التحديد
                                                    </span>
                                                )}
                                            </div>

                                            <div className="grid grid-cols-2 gap-2">
                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setFormData(prev => ({ ...prev, primaryPhoneHasWhatsapp: 'YES' }))}
                                                    className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-1.5 ${
                                                        formData.primaryPhoneHasWhatsapp === 'YES'
                                                            ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                                                            : 'bg-white text-stone-700 border-stone-300 hover:border-emerald-400'
                                                    }`}
                                                >
                                                    <Check className={`w-3.5 h-3.5 ${formData.primaryPhoneHasWhatsapp === 'YES' ? 'opacity-100' : 'opacity-0'}`} />
                                                    <span>نعم، الرقم يستخدم واتساب</span>
                                                </button>

                                                <button
                                                    type="button"
                                                    disabled={isLocked}
                                                    onClick={() => setFormData(prev => ({ ...prev, primaryPhoneHasWhatsapp: 'NO' }))}
                                                    className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-1.5 ${
                                                        formData.primaryPhoneHasWhatsapp === 'NO'
                                                            ? 'bg-stone-800 text-white border-stone-800 shadow-sm'
                                                            : 'bg-white text-stone-700 border-stone-300 hover:border-stone-400'
                                                    }`}
                                                >
                                                    <X className={`w-3.5 h-3.5 ${formData.primaryPhoneHasWhatsapp === 'NO' ? 'opacity-100' : 'opacity-0'}`} />
                                                    <span>لا، الرقم لا يستخدم واتساب</span>
                                                </button>
                                            </div>

                                            {hasPhoneChanged && (
                                                <p className="text-[11px] text-amber-800 bg-amber-50 p-2 rounded-lg border border-amber-200 font-medium leading-relaxed">
                                                    ⚠️ قمت بتعديل رقم الهاتف الأساسي؛ يرجى مراجعة إجابة واتساب المرتبطة به وإعادة تأكيدها.
                                                </p>
                                            )}
                                        </div>
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                            <MessageCircle className="w-3.5 h-3.5 text-green-600" />
                                            رقم شخصي إضافي (عليه واتساب) <span className="text-rose-500">*</span>
                                        </label>
                                        <input
                                            type="tel"
                                            inputMode="tel"
                                            required
                                            style={{ direction: 'ltr', textAlign: 'right' }}
                                            disabled={isLocked}
                                            value={formData.whatsappNumber || ''}
                                            onChange={e => setFormData({ ...formData, whatsappNumber: e.target.value.replace(/[^\d+\s]/g, '') })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold font-mono text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="09X XXXXXXX"
                                        />
                                        <p className="text-[10px] text-stone-500">رقم مفعّل عليه تطبيق واتساب لاستلام التعليمات والإشعارات (يُفضّل رقم إضافي بديل إن وُجد)</p>
                                        {formData.phoneNumber && digitsOnly(formData.whatsappNumber).length >= 9 && digitsOnly(formData.phoneNumber).length >= 9 && digitsOnly(formData.whatsappNumber).slice(-9) === digitsOnly(formData.phoneNumber).slice(-9) && (
                                            <div className="flex items-center gap-1.5 text-amber-800 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-xl text-xs mt-1.5 font-medium animate-in fade-in">
                                                <AlertCircle className="w-4 h-4 shrink-0 text-amber-600" />
                                                <span>تنبيه: هذا الرقم مطابق لرقمك الأساسي. يُفضّل إدخال رقم إضافي مختلف إن وُجد لضمان بدائل التواصل.</span>
                                            </div>
                                        )}
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                            <Building2 className="w-3.5 h-3.5 text-emerald-600" />
                                            المكتب الذي تتبع له <span className="text-rose-500">*</span>
                                        </label>
                                        <select
                                            required
                                            disabled={isLocked}
                                            value={formData.office || ''}
                                            onChange={e => setFormData({ ...formData, office: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                        >
                                            <option value="">-- اختر المكتب --</option>
                                            {officeOptions.map(office => (
                                                <option key={office} value={office}>{office}</option>
                                            ))}
                                        </select>
                                        <p className="text-[10px] text-stone-500">من المكاتب التابعة للتنسيقية</p>
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                            <Phone className="w-3.5 h-3.5 text-rose-500" />
                                            رقم هاتف الطوارئ (قريب)
                                        </label>
                                        <input
                                            type="tel"
                                            inputMode="tel"
                                            style={{ direction: 'ltr', textAlign: 'right' }}
                                            disabled={isLocked}
                                            value={formData.emergencyContactPhone || ''}
                                            onChange={e => setFormData({ ...formData, emergencyContactPhone: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold font-mono text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="09X XXXXXXX"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                            <User className="w-3.5 h-3.5 text-emerald-600" />
                                            اسم قريب الطوارئ
                                        </label>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.emergencyContactName || ''}
                                            onChange={e => setFormData({ ...formData, emergencyContactName: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-medium text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="مثال: محمد أحمد (الابن)"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700">صلة القرابة</label>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.emergencyContactRelation || ''}
                                            onChange={e => setFormData({ ...formData, emergencyContactRelation: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-medium text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="مثال: ابن، زوج، أخ، أخت..."
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 5: Address Information */}
                            <div id="section-address" className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-stone-200 shadow-sm space-y-4 scroll-mt-20">
                                <div className="flex items-center gap-2.5 pb-2 border-b border-stone-100">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-black text-sm shadow-sm shrink-0">
                                        5
                                    </div>
                                    <div>
                                        <h3 className="text-sm sm:text-base font-black text-stone-900">بيانات السكن والإقامة بليبيا</h3>
                                        <p className="text-[11px] text-stone-500">عنوان السكن لتسهيل ترتيبات التجمع والانطلاق</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700">المدينة</label>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.city || ''}
                                            onChange={e => setFormData({ ...formData, city: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="مثال: طرابلس"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700">المنطقة / المحلة</label>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.region || ''}
                                            onChange={e => setFormData({ ...formData, region: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="مثال: حي الأندلس / فشلوم / السراج"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700">اسم الشارع</label>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.streetName || ''}
                                            onChange={e => setFormData({ ...formData, streetName: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-medium text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="مثال: شارع الجمهورية"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700 flex items-center gap-1.5">
                                            <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                                            أقرب نقطة دالة
                                        </label>
                                        <input
                                            type="text"
                                            disabled={isLocked}
                                            value={formData.nearestLandmark || ''}
                                            onChange={e => setFormData({ ...formData, nearestLandmark: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-medium text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                            placeholder="مثال: قرب مسجد القدس / مدرسة الفداء"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 6: Personal Preferences & Volunteer Cards */}
                            <div className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-stone-200 shadow-sm space-y-4">
                                <div className="flex items-center gap-2.5 pb-2 border-b border-stone-100">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-black text-sm shadow-sm shrink-0">
                                        6
                                    </div>
                                    <div>
                                        <h3 className="text-sm sm:text-base font-black text-stone-900">التفضيلات والتطوع والخبرة</h3>
                                        <p className="text-[11px] text-stone-500">لتوزيع الغرف بشكل متجانس والاستعانة بالخبرات في خدمة الفوج</p>
                                    </div>
                                </div>

                                {/* Interactive Touch Toggle Cards */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3">
                                    
                                    {/* 1. Smoker */}
                                    <div 
                                        onClick={() => {
                                            if (!isLocked) setFormData(prev => ({ ...prev, isSmoker: !prev.isSmoker }));
                                        }}
                                        className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'} ${formData.isSmoker ? 'bg-amber-50/70 border-amber-300 text-amber-950 font-bold' : 'bg-stone-50/50 border-stone-200 text-stone-700'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-lg ${formData.isSmoker ? 'bg-amber-200 text-amber-900' : 'bg-stone-200/70 text-stone-500'}`}>
                                                <Cigarette className="w-4 h-4" />
                                            </div>
                                            <div>
                                                <div className="text-xs sm:text-sm font-bold">هل أنت مدخن؟</div>
                                                <div className="text-[11px] opacity-75 font-normal">لتنسيق الغرف الخالية من التدخين</div>
                                            </div>
                                        </div>
                                        <div className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${formData.isSmoker ? 'bg-amber-600 border-amber-600 text-white' : 'border-stone-300 bg-white'}`}>
                                            {formData.isSmoker && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                        </div>
                                    </div>

                                    {/* 2. Cold AC */}
                                    <div 
                                        onClick={() => {
                                            if (!isLocked) setFormData(prev => ({ ...prev, toleratesColdAC: !prev.toleratesColdAC }));
                                        }}
                                        className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'} ${formData.toleratesColdAC ? 'bg-teal-50/70 border-teal-300 text-teal-950 font-bold' : 'bg-stone-50/50 border-stone-200 text-stone-700'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-lg ${formData.toleratesColdAC ? 'bg-teal-200 text-teal-900' : 'bg-stone-200/70 text-stone-500'}`}>
                                                <Wind className="w-4 h-4" />
                                            </div>
                                            <div>
                                                <div className="text-xs sm:text-sm font-bold">تتحمل التكييف البارد؟</div>
                                                <div className="text-[11px] opacity-75 font-normal">لتسكين الغرف الملائمة لحرارة التكييف</div>
                                            </div>
                                        </div>
                                        <div className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${formData.toleratesColdAC ? 'bg-teal-600 border-teal-600 text-white' : 'border-stone-300 bg-white'}`}>
                                            {formData.toleratesColdAC && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                        </div>
                                    </div>

                                    {/* 3. Can Help Pilgrims */}
                                    <div 
                                        onClick={() => {
                                            if (!isLocked) setFormData(prev => ({ ...prev, canHelpPilgrims: !prev.canHelpPilgrims }));
                                        }}
                                        className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'} ${formData.canHelpPilgrims ? 'bg-emerald-50/70 border-emerald-300 text-emerald-950 font-bold' : 'bg-stone-50/50 border-stone-200 text-stone-700'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-lg ${formData.canHelpPilgrims ? 'bg-emerald-200 text-emerald-900' : 'bg-stone-200/70 text-stone-500'}`}>
                                                <HandHeart className="w-4 h-4" />
                                            </div>
                                            <div>
                                                <div className="text-xs sm:text-sm font-bold">مستعد للمساعدة والتطوع؟</div>
                                                <div className="text-[11px] opacity-75 font-normal">مساعدة كبار السن وخدمة الحجاج</div>
                                            </div>
                                        </div>
                                        <div className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${formData.canHelpPilgrims ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-stone-300 bg-white'}`}>
                                            {formData.canHelpPilgrims && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                        </div>
                                    </div>

                                    {/* 4. Good with Maps */}
                                    <div 
                                        onClick={() => {
                                            if (!isLocked) setFormData(prev => ({ ...prev, goodWithMaps: !prev.goodWithMaps }));
                                        }}
                                        className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'} ${formData.goodWithMaps ? 'bg-blue-50/70 border-blue-300 text-blue-950 font-bold' : 'bg-stone-50/50 border-stone-200 text-stone-700'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-lg ${formData.goodWithMaps ? 'bg-blue-200 text-blue-900' : 'bg-stone-200/70 text-stone-500'}`}>
                                                <Compass className="w-4 h-4" />
                                            </div>
                                            <div>
                                                <div className="text-xs sm:text-sm font-bold">تجيد استخدام الخرائط والـ GPS؟</div>
                                                <div className="text-[11px] opacity-75 font-normal">معرفة المواقع وتوجيه الحجاج</div>
                                            </div>
                                        </div>
                                        <div className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${formData.goodWithMaps ? 'bg-blue-600 border-blue-600 text-white' : 'border-stone-300 bg-white'}`}>
                                            {formData.goodWithMaps && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                        </div>
                                    </div>

                                    {/* 5. Good with Social Media */}
                                    <div 
                                        onClick={() => {
                                            if (!isLocked) setFormData(prev => ({ ...prev, goodWithSocialMedia: !prev.goodWithSocialMedia }));
                                        }}
                                        className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 sm:col-span-2 ${isLocked ? 'cursor-default' : 'cursor-pointer active:scale-[0.99]'} ${formData.goodWithSocialMedia ? 'bg-purple-50/70 border-purple-300 text-purple-950 font-bold' : 'bg-stone-50/50 border-stone-200 text-stone-700'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-lg ${formData.goodWithSocialMedia ? 'bg-purple-200 text-purple-900' : 'bg-stone-200/70 text-stone-500'}`}>
                                                <Share2 className="w-4 h-4" />
                                            </div>
                                            <div>
                                                <div className="text-xs sm:text-sm font-bold">تجيد استخدام الواتساب والتواصل؟</div>
                                                <div className="text-[11px] opacity-75 font-normal">متابعة إعلانات المجموعة ونشر التوجيهات</div>
                                            </div>
                                        </div>
                                        <div className={`w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${formData.goodWithSocialMedia ? 'bg-purple-600 border-purple-600 text-white' : 'border-stone-300 bg-white'}`}>
                                            {formData.goodWithSocialMedia && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                                        </div>
                                    </div>
                                </div>

                                {/* Previous Umrah Experience */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 pt-3 border-t border-stone-100">
                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700">عدد مرات العمرة السابقة</label>
                                        <input
                                            type="number"
                                            min="0"
                                            disabled={isLocked}
                                            value={formData.umrahCount || 0}
                                            onChange={e => setFormData({ ...formData, umrahCount: Number(e.target.value) })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                        />
                                    </div>

                                    <div className="space-y-1">
                                        <label className="text-xs font-bold text-stone-700">تاريخ آخر عمرة</label>
                                        <input
                                            type="date"
                                            disabled={isLocked}
                                            value={formatDateForInput(formData.lastUmrahDate)}
                                            onChange={e => setFormData({ ...formData, lastUmrahDate: e.target.value })}
                                            className="w-full px-3.5 py-3 sm:py-3.5 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-bold font-mono text-stone-900 text-base sm:text-sm disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 7: Companion Linking */}
                            <div className="bg-white rounded-2xl sm:rounded-3xl p-4 sm:p-6 border border-stone-200 shadow-sm space-y-4">
                                <div className="flex items-center gap-2.5 pb-2 border-b border-stone-100">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-black text-sm shadow-sm shrink-0">
                                        7
                                    </div>
                                    <div>
                                        <h3 className="text-sm sm:text-base font-black text-stone-900">ربط المرافق (المحرم / الزوجة)</h3>
                                        <p className="text-[11px] text-stone-500">لضم ملفات العائلة معاً في السكن والحافلات والمخيمات</p>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <p className="text-xs text-stone-600 leading-relaxed">
                                        أدخل الرقم الوطني للمرافق (زوج / زوجة / والد / والدة) لربط ملفكما رسمياً ضمن نفس الفوج.
                                    </p>

                                    {!isLocked && (
                                        <div className="flex gap-2">
                                            <input
                                                type="text"
                                                inputMode="numeric"
                                                pattern="[0-9]*"
                                                value={companionQuery}
                                                onChange={e => setCompanionQuery(e.target.value.replace(/\D/g, ''))}
                                                className="flex-1 px-3.5 py-3 rounded-xl border border-stone-200 bg-stone-50/60 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-mono font-bold text-stone-900 text-base sm:text-sm placeholder:font-normal placeholder:font-sans transition-all"
                                                placeholder="أدخل الرقم الوطني للمرافق..."
                                            />
                                            <button
                                                type="button"
                                                onClick={handleCompanionSearch}
                                                disabled={companionLoading || !companionQuery.trim()}
                                                className="px-4 sm:px-6 bg-stone-900 text-white rounded-xl font-bold hover:bg-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-xs sm:text-sm shrink-0"
                                            >
                                                {companionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                                                <span className="hidden sm:inline">بحث وربط</span>
                                            </button>
                                        </div>
                                    )}

                                    {companionSearchError && (
                                        <div className="bg-rose-50 text-rose-700 p-3 rounded-xl text-xs font-bold border border-rose-200 animate-in fade-in">
                                            {companionSearchError}
                                        </div>
                                    )}

                                    {formData.linkedPilgrimId && (
                                        <div className="bg-emerald-50/80 border border-emerald-200 p-3.5 rounded-2xl flex items-center justify-between gap-3 animate-in fade-in">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700 shrink-0">
                                                    <Users className="w-5 h-5" />
                                                </div>
                                                <div>
                                                    <p className="text-[11px] font-bold text-emerald-700 mb-0.5">تم ربط المرافق بنجاح:</p>
                                                    <p className="font-black text-stone-900 text-xs sm:text-sm">
                                                        {linkedPilgrimName || formData.linkedPilgrimId}
                                                    </p>
                                                </div>
                                            </div>

                                            {!isLocked && (
                                                <button
                                                    type="button"
                                                    onClick={() => setFormData(prev => ({ ...prev, linkedPilgrimId: undefined }))}
                                                    className="px-3 py-1.5 bg-white border border-rose-200 text-rose-600 hover:bg-rose-50 rounded-xl text-xs font-bold transition-colors shadow-sm shrink-0"
                                                >
                                                    إلغاء الربط
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Passport Expiry Warning Banner */}
                            {isPassportExpired && (
                                <div className="bg-rose-50 border-2 border-rose-300 text-rose-900 p-4 sm:p-5 rounded-2xl sm:rounded-3xl flex items-start gap-3 sm:gap-4 shadow-sm animate-in fade-in">
                                    <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center shrink-0">
                                        <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6" />
                                    </div>
                                    <div className="space-y-1">
                                        <p className="font-black text-sm sm:text-base text-rose-800">
                                            عذراً، جواز السفر الحالي غير صالٍ للاعتماد
                                        </p>
                                        <p className="text-xs sm:text-sm font-semibold text-rose-700 leading-relaxed">
                                            {passportExpiryWarning}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* STICKY BOTTOM FLOATING ACTION BAR FOR MOBILE */}
                            {!isLocked && (
                                <div className="fixed bottom-0 left-0 right-0 sm:sticky sm:bottom-4 z-40 bg-white/95 backdrop-blur-md border-t sm:border border-stone-200 p-3 sm:p-4 sm:rounded-2xl shadow-[0_-8px_30px_rgba(0,0,0,0.12)] max-w-4xl mx-auto flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-4">
                                    {isPassportExpired && (
                                        <div className="text-[11px] sm:text-xs font-bold text-rose-600 flex items-center gap-1.5 sm:hidden">
                                            <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                                            <span>الجواز غير صالح - تم إيقاف الإرسال</span>
                                        </div>
                                    )}
                                    <button
                                        type="button"
                                        onClick={handleInitiateSubmit}
                                        disabled={loading || isPassportExpired}
                                        className={`flex-1 text-white py-3.5 sm:py-4 px-4 sm:px-6 rounded-xl font-black text-sm sm:text-base shadow-lg active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                                            isPassportExpired 
                                                ? 'bg-rose-600 hover:bg-rose-700 shadow-rose-700/20' 
                                                : 'bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-700 hover:to-teal-800 shadow-emerald-700/25'
                                        }`}
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                <span>جارٍ المعالجة...</span>
                                            </>
                                        ) : isPassportExpired ? (
                                            <>
                                                <AlertTriangle className="w-5 h-5" />
                                                <span>إيقاف الإرسال: صلاحية الجواز غير مقبولة</span>
                                            </>
                                        ) : (
                                            <>
                                                <Save className="w-5 h-5" />
                                                <span>حفظ وإرسال البيانات للاعتماد</span>
                                            </>
                                        )}
                                    </button>

                                    <button
                                        type="button"
                                        onClick={() => {
                                            setPilgrim(null);
                                            window.scrollTo({ top: 0, behavior: 'smooth' });
                                        }}
                                        className="px-4 sm:px-6 py-3.5 sm:py-4 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-xl font-bold text-xs sm:text-sm transition-colors border border-stone-200 shrink-0"
                                    >
                                        إلغاء
                                    </button>
                                </div>
                            )}

                            {/* SUBMISSION CONFIRMATION MODAL (المتطلب السادس) */}
                            {showSubmitConfirmModal && (
                                <div className="fixed inset-0 z-50 bg-stone-900/70 backdrop-blur-sm flex items-center justify-center p-3.5 animate-in fade-in duration-200" dir="rtl">
                                    <div className="bg-white rounded-3xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-stone-200 space-y-4 animate-in zoom-in-95 duration-200">
                                        <div className="flex items-start gap-3.5 pb-3 border-b border-stone-100">
                                            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 shadow-sm">
                                                <ShieldCheck className="w-6 h-6" />
                                            </div>
                                            <div>
                                                <h3 className="text-base sm:text-lg font-black text-stone-900">
                                                    تأكيد إرسال البيانات للاعتماد
                                                </h3>
                                                <p className="text-xs text-stone-500 mt-0.5">
                                                    إدارة شؤون الحجاج - موسم 1448هـ
                                                </p>
                                            </div>
                                        </div>

                                        {/* Required prompt exact confirmation text */}
                                        <div className="bg-stone-50 p-4 rounded-2xl border border-stone-200 text-xs sm:text-sm font-medium text-stone-800 leading-relaxed space-y-2">
                                            <p className="font-bold text-stone-900">
                                                «هل أنت متأكد من صحة البيانات المدخلة ورغبتك في إرسالها للاعتماد؟ يمكنك تعديل بياناتك ما دامت المطابقة لم تُؤكَّد بعد، أما بعد تأكيد المطابقة فستصبح البيانات غير قابلة للتعديل من خلال حسابك.»
                                            </p>
                                        </div>

                                        {/* Current completion indicator snapshot */}
                                        {completionResult && (
                                            <div className="p-3 rounded-2xl bg-stone-50/80 border border-stone-200/80 flex items-center justify-between text-xs font-bold">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-stone-500">نسبة اكتمال النموذج:</span>
                                                    <span className="font-black font-mono text-emerald-700 text-sm">{completionResult.percentage}%</span>
                                                </div>
                                                <span className={`px-2 py-0.5 rounded-full text-[11px] font-black ${completionResult.isComplete ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                                                    {completionResult.isComplete ? 'مكتمل بالكامل' : `يتبقى ${completionResult.totalRequirements - completionResult.fulfilledCount} متطلبات`}
                                                </span>
                                            </div>
                                        )}

                                        {/* Modal Action Buttons */}
                                        <div className="flex items-center gap-2.5 pt-2">
                                            <button
                                                type="button"
                                                onClick={executeFinalSubmit}
                                                disabled={loading}
                                                className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white py-3.5 px-4 rounded-xl font-black text-sm shadow-lg shadow-emerald-700/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                {loading ? (
                                                    <>
                                                        <Loader2 className="w-4 h-4 animate-spin" />
                                                        <span>جارٍ الإرسال...</span>
                                                    </>
                                                ) : (
                                                    <>
                                                        <Check className="w-4 h-4 stroke-[3]" />
                                                        <span>تأكيد الإرسال</span>
                                                    </>
                                                )}
                                            </button>

                                            <button
                                                type="button"
                                                disabled={loading}
                                                onClick={() => setShowSubmitConfirmModal(false)}
                                                className="px-5 py-3.5 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-xl font-bold text-xs sm:text-sm transition-colors border border-stone-200 disabled:opacity-50"
                                            >
                                                مراجعة البيانات
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Locked State: Return Home Button */}
                            {isLocked && (
                                <div className="pt-2 flex justify-center">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setPilgrim(null);
                                            setSearchQuery('');
                                            window.scrollTo({ top: 0, behavior: 'smooth' });
                                        }}
                                        className="w-full sm:w-auto px-10 py-3.5 bg-stone-900 hover:bg-black text-white rounded-xl font-black text-sm shadow-lg transition-all flex items-center justify-center gap-2"
                                    >
                                        <span>البحث عن حاج آخر</span>
                                        <ArrowRight className="w-4 h-4" />
                                    </button>
                                </div>
                            )}

                        </form>
                    )}

                </div>

                {/* Footer Attribution */}
                <div className="bg-stone-50/90 p-4 sm:p-6 text-center border-t border-stone-100 flex flex-col items-center gap-2">
                    <div className="flex items-center gap-2.5 opacity-70 hover:opacity-100 transition-opacity">
                        <img 
                            src="/assets/athar-logo.svg" 
                            alt="Athar Creative Team" 
                            className="h-5 w-auto" 
                            onError={(e) => {
                                (e.target as HTMLElement).style.display = 'none';
                            }}
                        />
                        <div className="text-right">
                            <span className="text-[10px] text-stone-400 block leading-none">تصميم وتطوير</span>
                            <span className="text-xs font-black text-stone-700">فريق أثر الإبداعي</span>
                        </div>
                    </div>
                    <p className="text-[10px] font-semibold text-stone-400 mt-0.5">
                        جميع الحقوق محفوظة &copy; منظومة ميقات لإدارة وفود الحجاج 2026
                    </p>
                </div>
            </div>

            {/* Lightbox Image Preview Modal */}
            {previewImage && (
                <div 
                    onClick={() => setPreviewImage(null)}
                    className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm p-4 flex flex-col items-center justify-center animate-in fade-in duration-200"
                >
                    <div className="relative max-w-3xl w-full max-h-[90vh] flex flex-col items-center">
                        <button
                            type="button"
                            onClick={() => setPreviewImage(null)}
                            className="absolute -top-12 left-0 p-2 text-white/80 hover:text-white bg-white/10 hover:bg-white/20 rounded-full transition-colors flex items-center gap-1.5 text-xs font-bold"
                        >
                            <X className="w-5 h-5" />
                            <span>إغلاق</span>
                        </button>
                        <img 
                            src={previewImage} 
                            alt="Passport full view" 
                            className="max-h-[85vh] w-auto max-w-full rounded-2xl object-contain shadow-2xl border border-white/20"
                            onClick={e => e.stopPropagation()}
                        />
                    </div>
                </div>
            )}

            {/* OCR Confirmation Modal */}
            {showOcrConfirmModal && ocrResult && ocrResult.success && (
                <div 
                    className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm p-4 flex items-center justify-center animate-in fade-in duration-200"
                    onClick={() => setShowOcrConfirmModal(false)}
                >
                    <div 
                        className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-stone-200 space-y-5"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-start justify-between gap-4 border-b border-stone-100 pb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white flex items-center justify-center shadow-md">
                                    <ScanLine className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-black text-stone-900">
                                        {ocrResult.verified ? 'تمت قراءة بيانات الجواز والتحقق منها' : 'تمت قراءة جزء من بيانات الجواز'}
                                    </h3>
                                    <p className="text-xs text-stone-500">قراءة شريط الـ MRZ مع مطابقة خانات التدقيق المعتمدة دولياً (ICAO)</p>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setShowOcrConfirmModal(false)}
                                className="p-2 text-stone-400 hover:text-stone-700 hover:bg-stone-100 rounded-xl transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-3 bg-stone-50/70 p-4 rounded-2xl border border-stone-200">
                            <div className="flex justify-between items-center py-1.5 border-b border-stone-200/60">
                                <span className="text-xs font-bold text-stone-500">رقم الجواز:</span>
                                <span className="text-sm font-black font-mono text-stone-900 bg-white px-2.5 py-1 rounded-lg border border-stone-200">
                                    {ocrResult.passportNumber || 'لم يُقرأ بدقة - أدخله يدوياً'}
                                </span>
                            </div>

                            <div className="flex justify-between items-center py-1.5 border-b border-stone-200/60">
                                <span className="text-xs font-bold text-stone-500">تاريخ انتهاء الجواز:</span>
                                <span className="text-sm font-black font-mono text-stone-900 bg-white px-2.5 py-1 rounded-lg border border-stone-200">
                                    {ocrResult.passportExpiryDate || 'لم يُقرأ بدقة - أدخله يدوياً'}
                                </span>
                            </div>

                            {ocrResult.birthDate && (
                                <div className="flex justify-between items-center py-1.5 border-b border-stone-200/60">
                                    <span className="text-xs font-bold text-stone-500">تاريخ الميلاد:</span>
                                    <span className="text-sm font-mono font-bold text-stone-800 bg-white px-2.5 py-1 rounded-lg border border-stone-200">
                                        {ocrResult.birthDate}
                                    </span>
                                </div>
                            )}

                            {ocrResult.nationality && (
                                <div className="flex justify-between items-center py-1.5 border-b border-stone-200/60">
                                    <span className="text-xs font-bold text-stone-500">الجنسية:</span>
                                    <span className="text-sm font-bold text-stone-800 bg-white px-2.5 py-1 rounded-lg border border-stone-200">
                                        {ocrResult.nationality}
                                    </span>
                                </div>
                            )}

                            {ocrResult.fullNameEnglish && (
                                <div className="flex justify-between items-center gap-3 py-1.5">
                                    <span className="text-xs font-bold text-stone-500 shrink-0">الاسم باللاتينية:</span>
                                    <span className="text-xs font-mono font-bold text-stone-800 bg-white px-2.5 py-1 rounded-lg border border-stone-200 text-left" dir="ltr">
                                        {ocrResult.fullNameEnglish}
                                    </span>
                                </div>
                            )}
                        </div>

                        {ocrBirthDateMismatch && (
                            <div className="bg-amber-50 border border-amber-300 text-amber-900 p-3.5 rounded-xl text-xs flex items-start gap-2.5">
                                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-bold mb-0.5">تاريخ الميلاد في الجواز لا يطابق المسجل في المنظومة</p>
                                    <p className="leading-relaxed">
                                        المسجل: <span className="font-mono font-bold">{String(pilgrim?.birthDate).slice(0, 10)}</span> — في الجواز: <span className="font-mono font-bold">{ocrResult.birthDate}</span>.
                                        يرجى التأكد من أنك رفعت جواز الحاج الصحيح.
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Minimum Expiry Warning in Modal if applicable */}
                        {isPassportExpired && (
                            <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3.5 rounded-xl text-xs flex items-start gap-2.5">
                                <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-bold mb-0.5">تنبيه صلاحية الجواز:</p>
                                    <p className="leading-relaxed">{passportExpiryWarning}</p>
                                </div>
                            </div>
                        )}

                        <p className="text-xs text-stone-500 leading-relaxed">
                            تم تعبئة الحقول التي تطابقت مع خانات التدقيق فقط. يرجى مقارنتها مع صفحة الجواز، ويمكنك تعديل أي حقل يدوياً قبل الإرسال.
                        </p>

                        <div className="flex gap-3 pt-2">
                            <button
                                type="button"
                                onClick={() => setShowOcrConfirmModal(false)}
                                className="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-black text-sm shadow-md transition-all flex items-center justify-center gap-2"
                            >
                                <Check className="w-4 h-4" />
                                <span>تأكيد البيانات والمتابعة</span>
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowOcrConfirmModal(false)}
                                className="py-3 px-4 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-xl font-bold text-sm transition-colors border border-stone-200"
                            >
                                تعديل يدوي
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
