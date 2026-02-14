# API Integration & UI Components Update

## 📋 Overview

This document describes all the changes made to integrate the Trip Plan API and replace `window.confirm`/`alert` calls with reusable UI components.

---

## ✅ Changes Made

### 1. **Complete API Service Implementation**

**File:** [src/services/api.ts](src/services/api.ts)

- ✅ Implemented all 13 API endpoints from the documentation
- ✅ Added TypeScript types for all requests and responses
- ✅ Configured base URL from environment variable
- ✅ Added JWT token interceptor for authentication
- ✅ Added helper method for PDF download

**API Services Created:**
- `tripApi` - Trip management (create, get, update, delete, history, claim, cost breakdown, export PDF)
- `tripItemApi` - Item management (update, delete, replace)
- `tripDayApi` - Day management (create day, bulk create items)

---

### 2. **Updated Type Definitions**

**File:** [src/types/trip.ts](src/types/trip.ts)

- ✅ Aligned types with API documentation
- ✅ Added all API payload and response types
- ✅ Added backward compatibility with existing field names
- ✅ Added new types: `CategoryType`, `ItemType`, `ReplaceItemPayload`, `BulkCreateItemPayload`, `CostBreakdownResponse`, `TripHistoryResponse`

**Key Changes:**
- Extended `ItemType` to include: `FOOD`, `TRANSPORT`, `ACTIVITY`
- Removed `UNLIMITED` from `BudgetLevel` (per API spec)
- Added dual field support (e.g., `id`/`trip_id`, `type`/`item_type`) for flexibility

---

### 3. **Reusable UI Components**

#### **ConfirmDialog Component**
**File:** [src/components/ui/ConfirmDialog.tsx](src/components/ui/ConfirmDialog.tsx)

Replaces all `window.confirm()` calls with a beautiful, accessible modal dialog.

**Features:**
- Three variants: `danger`, `warning`, `info`
- Loading state support
- Keyboard-friendly (ESC to close)
- Persian text support

**Usage Example:**
```tsx
const [confirmDialog, setConfirmDialog] = useState({
  isOpen: false,
  title: '',
  message: '',
  onConfirm: () => {},
});

// Show dialog
setConfirmDialog({
  isOpen: true,
  title: 'حذف آیتم',
  message: 'آیا از حذف این آیتم اطمینان دارید؟',
  variant: 'danger',
  onConfirm: async () => {
    // Your async action
  },
});

// In JSX
<ConfirmDialog
  isOpen={confirmDialog.isOpen}
  onClose={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
  onConfirm={confirmDialog.onConfirm}
  title={confirmDialog.title}
  message={confirmDialog.message}
  variant={confirmDialog.variant}
/>
```

---

#### **Notification System**
**Files:**
- [src/contexts/NotificationContext.tsx](src/contexts/NotificationContext.tsx)
- [src/components/ui/NotificationContainer.tsx](src/components/ui/NotificationContainer.tsx)

Replaces all `alert()` calls with toast notifications.

**Features:**
- Four types: `success`, `error`, `warning`, `info`
- Auto-dismiss with configurable duration
- Multiple notifications stacking
- Smooth animations

**Usage Example:**
```tsx
import { useNotification } from '@/contexts/NotificationContext';

const { success, error, warning, info } = useNotification();

// Show notifications
success('عملیات با موفقیت انجام شد');
error('خطایی رخ داد');
warning('این قابلیت در دسترس نیست');
info('اطلاعات ذخیره شد');
```

---

### 4. **Updated Pages & Components**

#### **FinalizeTrip Page**
**File:** [src/pages/FinalizeTrip.tsx](src/pages/FinalizeTrip.tsx)

**Changes:**
- ✅ Replaced `window.confirm()` with `ConfirmDialog`
- ✅ Replaced `alert()` with notifications
- ✅ Updated API calls to use `tripItemApi` instead of old `tripApi` methods
- ✅ Added proper error handling with API error messages
- ✅ Implemented final save with PDF download
- ✅ Updated budget save to use `tripApi.update()`

**Handlers Updated:**
- `handleItemTimeChange()` - Now uses `tripItemApi.update()`
- `handleDeleteItem()` - Shows confirm dialog, uses `tripItemApi.delete()`
- `handleSuggestAlternative()` - Prepared for `tripItemApi.replace()` (commented until backend ready)
- `handleSaveBudget()` - Uses `tripApi.update()`
- `handleFinalSave()` - New handler with dialog and PDF download

---

#### **CreateTripForm**
**File:** [src/containers/create-trip/CreateTripForm.tsx](src/containers/create-trip/CreateTripForm.tsx)

**Changes:**
- ✅ Integrated `tripApi.create()` API call
- ✅ Added loading state during creation
- ✅ Maps form data to API payload correctly:
  - `startDate` → `start_date`
  - Calculates `duration_days` from date range
  - `style` → `travel_style`
  - `density` → `daily_available_hours` (RELAXED=6h, BALANCED=8h, INTENSIVE=10h)
- ✅ Replaced console.log with notifications
- ✅ Navigates to finalize-trip page on success

**Field Mapping Logic:**
```typescript
// Quick mode: Only basic fields
{
  province, city, start_date, duration_days
}

// Pro mode: Includes advanced fields
{
  province, city, start_date, duration_days,
  travel_style, budget_level, daily_available_hours
}
```

---

### 5. **App-Level Changes**

#### **App.tsx**
**File:** [src/App.tsx](src/App.tsx)

**Changes:**
- ✅ Wrapped app in `NotificationProvider`
- ✅ Added `NotificationContainer` to render toasts globally

---

### 6. **Environment Configuration**

**File:** [.env.example](.env.example)

```env
VITE_API_BASE_URL=http://localhost:9151/api
```

**Setup:**
1. Copy `.env.example` to `.env`
2. Update `VITE_API_BASE_URL` if needed

---

## 🔄 API Endpoint Mapping

| Feature | Old Implementation | New Implementation | Status |
|---------|-------------------|-------------------|--------|
| Create Trip | ❌ Mock/console.log | ✅ `POST /trips/` | ✅ Done |
| Get Trip | ✅ Mock service | ✅ `GET /trips/{id}/` | ✅ Ready |
| Update Budget | ⚠️ Wrong endpoint | ✅ `PATCH /trips/{id}/` | ✅ Fixed |
| Update Item Time | ⚠️ Wrong endpoint | ✅ `PATCH /items/{id}/` | ✅ Fixed |
| Delete Item | ⚠️ Wrong endpoint | ✅ `DELETE /items/{id}/` | ✅ Fixed |
| Suggest Alternative | ❌ Not implemented | ✅ `POST /items/{id}/replace/` | ⏳ Prepared |
| Export PDF | ❌ Not implemented | ✅ `GET /trips/{id}/export_pdf/` | ✅ Done |
| Cost Breakdown | ❌ Local calculation | ✅ `GET /trips/{id}/cost_breakdown/` | ✅ Ready |
| Trip History | ❌ Not implemented | ✅ `GET /trips/history/` | ✅ Ready |

---

## 🎯 Field Name Mapping (FormData → API)

As requested, **formData field names are NOT changed**. Mapping happens only in API call:

| FormData Field | API Field | Mapping Logic |
|---------------|-----------|---------------|
| `startDate` | `start_date` | `.format('YYYY-MM-DD')` |
| `endDate` | `duration_days` | Calculate difference + 1 |
| `style` | `travel_style` | Direct mapping |
| `budget` | `budget_level` | Direct mapping |
| `density` | `daily_available_hours` | Map to hours (6, 8, 10) |

---

## 🚀 How to Use

### 1. **Environment Setup**
```bash
# Copy environment file
cp .env.example .env

# Update API URL if needed
nano .env
```

### 2. **Install Dependencies** (if needed)
```bash
npm install
```

### 3. **Start Development Server**
```bash
npm run dev
```

### 4. **Testing API Integration**

#### Create Trip:
1. Go to "ایجاد برنامه سفر"
2. Fill in province and start date
3. Click "ایجاد برنامه فوری" or add advanced options
4. Should navigate to finalize-trip page

#### Finalize Trip:
1. View trip timeline
2. Edit item times (drag sliders)
3. Delete items (shows confirm dialog)
4. Change budget level (shows success notification)
5. Click "ذخیره نهایی" (downloads PDF)

---

## 🛡️ Error Handling

All API calls now have proper error handling:

```typescript
try {
  await tripApi.create(payload);
  success('Success message');
} catch (err: any) {
  const errorMessage = err.response?.data?.error || 'Fallback error message';
  showError(errorMessage);
}
```

**Error Sources:**
1. **API Error Messages** - Displayed if available (Persian from backend)
2. **Validation Errors** - Shown from API response
3. **Network Errors** - Generic fallback message

---

## 📝 Notes

### Backward Compatibility
- All existing type fields are preserved
- Dual field support (e.g., `id` and `trip_id` both work)
- Mock service still functional for development

### Not Implemented (Waiting for Backend)
- Suggest Alternative (API prepared, needs backend integration)
- Some fields may need adjustment based on actual API responses

### Future Enhancements
Consider adding:
- Authentication flow with JWT storage
- Claim guest trip after login
- Trip history page
- Cost breakdown visualization

---

## 🐛 Troubleshooting

### API calls fail with 404
- Check `VITE_API_BASE_URL` in `.env`
- Ensure backend is running on `http://localhost:9151`

### Notifications not showing
- Check `NotificationProvider` wraps your app
- Check `NotificationContainer` is rendered

### TypeScript errors
- Run `npm run type-check` or restart TS server
- Check import paths use `@/` alias

---

## 📞 Contact

For questions about these changes, please check:
- API Documentation (provided in the task)
- This README
- Component source code (well-commented)
