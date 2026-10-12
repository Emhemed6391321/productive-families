// Minimal stand-ins for the real project's ../types (only what PublicPilgrimForm uses).
export enum HealthStatus { FIT = 'FIT', CHRONIC = 'CHRONIC', DISABLED = 'DISABLED' }
export enum DocStatus { PENDING = 'PENDING', RECEIVED = 'RECEIVED', VERIFIED = 'VERIFIED' }
export enum PilgrimRole { PILGRIM = 'PILGRIM', SUPERVISOR = 'SUPERVISOR', COORDINATOR = 'COORDINATOR' }
export type Pilgrim = any;
