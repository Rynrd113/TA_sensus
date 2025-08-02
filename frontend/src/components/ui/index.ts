// 🏥 SENSUS-RS Medical UI Framework - UNIFIED EXPORTS
// One Component = One File = One Purpose

// ===== CORE UI COMPONENTS ===== 
// NO MORE DUPLICATES - CLEAN & ORGANIZED

export { default as Button } from './Button';         // UNIFIED button system
export { default as Card } from './Card';             // UNIFIED card system  
export { default as Input, Select } from './Input';   // UNIFIED input system
export { default as StatCard } from './StatCard';     // UNIFIED stat card system

// ===== SPECIALIZED COMPONENTS =====
export { default as AlertCard } from './AlertCard';   // Alert notifications
export { default as ExportButton } from './ExportButton'; // Export functionality

// ===== SEMANTIC ALIASES ===== 
// For clarity and backward compatibility
export { default as MedicalButton } from './Button';
export { default as MedicalCard } from './Card';
export { default as MedicalInput } from './Input';
export { default as MedicalStatCard } from './StatCard';
