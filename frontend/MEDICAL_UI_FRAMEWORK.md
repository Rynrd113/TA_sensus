# 🏥 SENSUS-RS Medical UI Framework

**Framework UI Terpilih:** Tailwind CSS + Custom Medical Components

## 🎯 Filosofi Design

Sebagai expert UI/UX dengan pengalaman luas, saya memilih **Tailwind CSS** sebagai foundation tunggal untuk proyek medical ini karena:

### ✅ Keunggulan Tailwind untuk Medical Applications

1. **🎨 Design Consistency**: Utility-first approach memastikan konsistensi visual
2. **⚡ Performance**: Tree-shaking otomatis, hanya CSS yang digunakan yang di-bundle
3. **🛠️ Medical Customization**: Mudah disesuaikan untuk kebutuhan healthcare
4. **📱 Responsive**: Mobile-first design untuk accessibility medical staff
5. **♿ Accessibility**: Built-in support untuk WCAG compliance
6. **🔧 Developer Experience**: IntelliSense, purging, dan tooling yang excellent

### ❌ Mengapa Tidak Framework Lain?

- **Material UI**: Terlalu opinionated, tidak cocok untuk medical aesthetics
- **Chakra UI**: Bundle size besar, overhead untuk kebutuhan custom medical
- **Ant Design**: Chinese design language, tidak sesuai medical Indonesia
- **Bootstrap**: Outdated approach, tidak flexible untuk custom theming

## 🎨 Medical Design System

### Color Palette
```css
:root {
  /* Medical Primary - Professional Blue */
  --medical-50: #eff6ff;
  --medical-100: #dbeafe;
  --medical-200: #bfdbfe;
  --medical-300: #93c5fd;
  --medical-400: #60a5fa;
  --medical-500: #3b82f6;  /* Primary */
  --medical-600: #2563eb;
  --medical-700: #1d4ed8;
  --medical-800: #1e40af;
  --medical-900: #1e3a8a;

  /* Status Colors */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #06b6d4;
}
```

### Typography Scale
```css
/* Medical typography - Clean & Readable */
--font-heading: 'Inter', -apple-system, sans-serif;
--font-body: 'Inter', -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Scale */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
```

### Spacing & Layout
```css
/* Medical spacing - Comfortable for touch & mouse */
--spacing-xs: 0.5rem;
--spacing-sm: 0.75rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-2xl: 3rem;

/* Medical radius - Soft & Professional */
--radius-sm: 0.375rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1rem;
```

## 🧩 Core Components

### 1. Button Component
```tsx
// Versatile button dengan medical styling
<Button 
  variant="primary" | "secondary" | "success" | "warning" | "danger" | "ghost"
  size="xs" | "sm" | "md" | "lg" | "xl"
  loading={boolean}
  icon={ReactNode}
  iconPosition="left" | "right"
  fullWidth={boolean}
  disabled={boolean}
>
  Button Text
</Button>

// Usage Examples:
<Button variant="primary" size="md" loading={isSubmitting}>
  Simpan Data Sensus
</Button>

<Button variant="success" icon={<CheckIcon />} size="sm">
  Approve
</Button>
```

### 2. Card Component  
```tsx
// Professional card untuk medical content
<Card
  variant="default" | "primary" | "success" | "warning" | "danger" | "minimal"
  size="sm" | "md" | "lg"
  title="Card Title"
  subtitle="Optional Subtitle"
  description="Description text"
  loading={boolean}
  hoverable={boolean}
  header={ReactNode}
  footer={ReactNode}
>
  Card Content
</Card>

// Usage Examples:
<Card 
  title="Data Sensus Harian"
  variant="primary"
  size="lg"
  hoverable
>
  <SensusData />
</Card>
```

### 3. Input Components
```tsx
// Medical-styled form inputs
<Input
  label="Label Text"
  placeholder="Placeholder"
  variant="default" | "medical"
  error="Error message"
  helperText="Helper text"
  leftIcon={<UserIcon />}
  rightIcon={<SearchIcon />}
  required
/>

<Select
  label="Pilih Bangsal"
  options={bangsalOptions}
  variant="medical"
  error={error}
/>

// Usage Examples:
<Input 
  label="Nama Pasien"
  placeholder="Masukkan nama lengkap"
  variant="medical"
  leftIcon={<UserIcon />}
  required
/>
```

### 4. StatCard Component
```tsx
// KPI metrics dengan medical theming
<StatCard
  title="BOR Hari Ini"
  value="75.5"
  unit="%"
  description="Bed Occupancy Rate"
  status="excellent" | "good" | "warning" | "critical" | "neutral"
  trend={{
    value: 5.2,
    direction: "up" | "down" | "stable",
    label: "vs bulan lalu"
  }}
  icon={<BedIcon />}
  loading={boolean}
  onClick={() => {}}
/>

// Usage Examples:
<StatCard
  title="Total Pasien"
  value="234"
  status="good"
  trend={{ value: 12, direction: "up", label: "dari kemarin" }}
  icon={<UsersIcon />}
/>
```

## 🎨 Medical CSS Utilities

### Tailwind Medical Extensions
```css
/* Medical components */
.medical-card {
  @apply bg-white rounded-lg border border-gray-200 p-6 shadow-sm transition-all duration-200;
}

.medical-btn {
  @apply inline-flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.medical-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

/* Medical status colors */
.status-excellent { @apply bg-green-50 border-green-200 text-green-700; }
.status-good { @apply bg-blue-50 border-blue-200 text-blue-700; }
.status-warning { @apply bg-orange-50 border-orange-200 text-orange-700; }
.status-critical { @apply bg-red-50 border-red-200 text-red-700; }
.status-neutral { @apply bg-gray-50 border-gray-200 text-gray-700; }

/* Medical icons */
.medical-icon-sm { @apply w-4 h-4; }
.medical-icon-md { @apply w-5 h-5; }
.medical-icon-lg { @apply w-6 h-6; }
```

## 📋 Implementation Guidelines

### 1. Import Pattern
```tsx
// Gunakan named imports dari central index
import { Button, Card, Input, StatCard } from '../components/ui';

// Atau gunakan medical aliases untuk clarity
import { MedicalButton, MedicalCard } from '../components/ui';
```

### 2. Theming Consistency
```tsx
// Gunakan variant yang konsisten
const theme = {
  primary: 'primary',
  success: 'success', 
  warning: 'warning',
  danger: 'danger'
};

// Medical status mapping
const statusMap = {
  excellent: 'success',
  good: 'primary', 
  warning: 'warning',
  critical: 'danger'
};
```

### 3. Responsive Design
```tsx
// Mobile-first approach
<div className="
  p-4 sm:p-6 lg:p-8
  text-sm sm:text-base
  grid-cols-1 md:grid-cols-2 lg:grid-cols-4
">
  <StatCard />
</div>
```

## 🔧 Development Workflow

### 1. Component Development
1. Buat component di `/components/ui/`
2. Export dari `/components/ui/index.ts`
3. Test responsiveness di mobile/tablet/desktop
4. Validate accessibility (WCAG)

### 2. Styling Guidelines
- Gunakan Tailwind utilities first
- Custom CSS hanya jika absolutely necessary
- Maintain medical color palette
- Ensure touch-friendly sizing (44px minimum)

### 3. Performance
- Bundle size: < 50KB for UI components
- Tree-shaking: Only import used components
- Lazy loading: Non-critical components

## 📊 Benefits Recap

1. **🎯 Single Source of Truth**: Satu framework, konsistensi tinggi
2. **⚡ Performance**: Optimal bundle size dengan tree-shaking
3. **🏥 Medical Optimized**: Disesuaikan untuk healthcare workflow
4. **📱 Mobile Ready**: Responsive untuk berbagai device
5. **♿ Accessible**: WCAG compliant untuk inclusivity
6. **🛠️ Developer Experience**: IntelliSense, hot reload, tooling

## 🚀 Next Steps

1. ✅ Konsolidasi export dalam `/components/ui/index.ts`
2. ⏳ Remove duplicate components (`MedicalButton.tsx`, `MedicalCard.tsx`, etc)
3. ⏳ Update all imports to use central index
4. ⏳ Implement design tokens in Tailwind config
5. ⏳ Create component documentation/Storybook
6. ⏳ Setup automated accessibility testing

---

**Kesimpulan**: Tailwind CSS + Custom Medical Components adalah pilihan optimal untuk proyek healthcare ini, memberikan balance perfect antara flexibility, performance, dan medical-specific requirements.
