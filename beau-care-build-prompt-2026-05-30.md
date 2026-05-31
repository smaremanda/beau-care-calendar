# Comprehensive Build Prompt: Beau - Dog Care Calendar

Build a dog care tracking calendar application that helps pet owners quickly log daily medication (Apoquel) and bath activities with seamless switching between weekly and monthly calendar views.

## Core Purpose

A single-purpose pet care calendar for tracking two specific daily activities (Apoquel medication and baths) with an optional notes field. The app should feel like a caring daily ritual - reliable, gentle, and efficient.

## Technical Stack

- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS v4 with custom theme
- **UI Components**: shadcn/ui v4 components
- **Icons**: Phosphor Icons React (`@phosphor-icons/react`)
- **Animations**: Framer Motion for smooth transitions
- **Data Persistence**: Use the Spark KV storage API (`useKV` hook or `spark.kv` API)
- **Font**: Outfit (Google Fonts) - rounded, friendly geometric sans-serif

## Design System

### Color Palette (All colors in OKLCH format)

```css
/* Base colors */
--background: oklch(0.95 0.02 85);           /* Soft cream background */
--foreground: oklch(0.30 0.02 35);           /* Dark brown text */

/* Card colors */
--card: oklch(0.98 0.01 85);                 /* Slightly lighter cream */
--card-foreground: oklch(0.30 0.02 35);      /* Dark brown text */

/* Action colors */
--primary: oklch(0.62 0.14 35);              /* Warm terracotta */
--primary-foreground: oklch(0.98 0.01 85);   /* Light text on primary */
--secondary: oklch(0.88 0.04 85);            /* Light neutral */
--secondary-foreground: oklch(0.30 0.02 35); /* Dark text */
--accent: oklch(0.70 0.17 25);               /* Bright coral for "today" */
--accent-foreground: oklch(0.98 0.01 85);    /* Light text on accent */

/* Activity-specific colors */
--apoquel: oklch(0.72 0.08 145);             /* Sage green (medication) */
--bath: oklch(0.65 0.20 250);                /* Sky blue (water/cleanliness) */
--comment: oklch(0.75 0.18 50);              /* Warm yellow (notes) */

/* Supporting colors */
--muted: oklch(0.92 0.02 85);
--muted-foreground: oklch(0.55 0.02 35);
--border: oklch(0.85 0.03 85);
--destructive: oklch(0.577 0.245 27.325);

/* Border radius */
--radius: 0.75rem;
```

**Important Color Update**: The bath color has been changed from purple to a more distinct blue to improve color-blind accessibility, making it more visually distinct from the warm yellow notes indicator.

### Typography Hierarchy

- **App Title (H1)**: Outfit SemiBold, 36px (text-4xl), tight tracking
- **Month/Week Header (H2)**: Outfit SemiBold, 24px (text-2xl), normal tracking
- **Day Numbers**: Outfit Medium, 16px (text-base) in month view, 24px (text-2xl) in week view
- **Body Text**: Outfit Regular, 14px (text-sm)
- **Day Names Header**: Outfit Medium, 14px (text-sm), uppercase, wide tracking

### Border Radius System

- Small: `calc(var(--radius) * 0.5)` = 0.375rem
- Medium: `var(--radius)` = 0.75rem
- Large: `calc(var(--radius) * 1.5)` = 1.125rem
- Extra Large: `calc(var(--radius) * 2)` = 1.5rem
- Full: 9999px (for circular indicators)

## Data Structure

### TypeScript Interfaces

```typescript
export interface DayActivities {
  apoquel: boolean
  bath: boolean
  comment?: string
}

export interface CalendarData {
  [dateKey: string]: DayActivities
  // dateKey format: "YYYY-MM-DD" (e.g., "2024-01-15")
}

export type ViewMode = 'month' | 'week'
```

### Data Persistence

All calendar data should persist between sessions using the Spark KV storage API. Use the `useKV` hook in React components:

```typescript
import { useKV } from '@github/spark/hooks'

const [activities, setActivities] = useKV<CalendarData>('dog-care-activities', {})
```

**CRITICAL**: Always use functional updates with `setActivities` to avoid data loss:

```typescript
// ❌ WRONG - Don't reference activities from closure
setActivities({ ...activities, [dateKey]: dayActivities })

// ✅ CORRECT - Use functional updates
setActivities((current) => ({
  ...current,
  [dateKey]: dayActivities
}))
```

## Core Features & Implementation Details

### 1. Calendar Grid Display

**Month View (Default)**:
- 7-column grid (Monday - Sunday)
- 6 rows (42 day cells total to show previous/next month overflow)
- Each day cell shows:
  - Day number
  - Small circular indicators (8px diameter w-2 h-2) for active activities
  - Indicators stack vertically with gap-1.5
- Responsive gap: `gap-2` for month view
- Day cell padding: `p-3` with minimum height of `80px`
- Days from previous/next month: 40% opacity
- Today: accent-colored ring (2px) with subtle shadow
- Future dates: 60% opacity (viewable but indicates can't log)

**Week View**:
- Same 7-column grid but showing only current week
- Larger day cells: `p-4 md:p-6` with minimum height of `100px md:min-h-[120px]`
- Day numbers: larger font (text-lg md:text-2xl)
- Activity indicators: larger (12px diameter w-4 h-4 md:w-3 md:h-3)
- Responsive gap: `gap-2 md:gap-4` for more breathing room

**Week Day Header**:
- Always visible above calendar grid
- Shows: Mon, Tue, Wed, Thu, Fri, Sat, Sun
- Uppercase, medium weight, muted color, centered

### 2. View Mode Toggle

Two buttons in the header:
- **Month button**: Shows `Calendar` icon (filled when active) + "Month" label
- **Week button**: Shows `CalendarBlank` icon (filled when active) + "Week" label
- Active button: default variant
- Inactive button: outline variant
- Both buttons in a horizontal group with gap-2

### 3. Navigation Controls

**Header Layout**:
- Left: Previous button (`CaretLeft` icon, icon-only button, outline variant)
- Center: Current month/week display (e.g., "January 2024" or "Jan 15 - Jan 21, 2024")
- Right: Next button (`CaretRight` icon, icon-only button, outline variant)
- Below navigation: "Today" button (secondary variant, centered)

**Navigation Behavior**:
- Month view: Previous/next buttons move by 1 month
- Week view: Previous/next buttons move by 1 week
- Today button: jumps to current date, updates view to include today

### 4. Day Selection & Quick Log Dialog

**Trigger**: Click any day cell in calendar

**Dialog Contents**:
- **Header**: Shows formatted date
  - "Today" if today
  - "Yesterday" if yesterday
  - Otherwise: "Wednesday, January 15" (or with year if different year)
- **Future Date Handling**: If date is in future, show message "Can't log activities for future dates" and disable all inputs
- **Activity Toggles** (if not future date):
  - Large button for Apoquel: `PawPrint` icon + "Apoquel" label
    - When active: sage green background, filled icon, subtle scale bounce animation
    - Height: 80px (h-20), full width
  - Large button for Bath: `Bathtub` icon + "Bath" label
    - When active: sky blue background, filled icon, subtle scale bounce animation
    - Height: 80px (h-20), full width
- **Notes Field**:
  - Label: "Notes for the day"
  - Textarea with placeholder "Add any notes or comments..."
  - Minimum height: 100px
  - Auto-saves on change
- **Animations**: When activity is toggled on, button scales from 1 → 1.05 → 1 over 0.3s

### 5. Activity Indicators on Calendar

Each day cell shows small circular dots for logged activities:

**Month View**:
- Size: 8px width × 8px height (w-2 h-2)
- Layout: Stack vertically or as flex-col with small gap (gap-1.5)
- Position: Below day number

**Week View**:
- Size: 12px on mobile, 8px on desktop (w-4 h-4 md:w-3 md:h-3)
- Layout: Horizontal row with small gap (gap-1.5)
- Position: Below day number, mt-auto to stick to bottom

**Indicator Colors**:
- Apoquel: `bg-apoquel` (sage green)
- Bath: `bg-bath` (sky blue)
- Notes (when comment exists and not empty): `bg-comment` (warm yellow)

### 6. Legend

At the bottom of the calendar, show a centered legend with three items:
- Small colored circle + "Apoquel" label
- Small colored circle + "Bath" label
- Small colored circle + "Notes" label

Each with appropriate background color matching the activity indicators.

### 7. Analytics Tab

A second tab showing statistics about logged activities:

**Total Statistics Cards**:
- Two cards side by side showing total Apoquel pills and total baths
- Each card has appropriate icon and color theming
- Shows "All time" subtitle

**Monthly Breakdown**:
- List of months with activity counts
- Shows Apoquel and Bath counts for each month
- Sorted by most recent first
- Empty state message when no data

**Export Functionality**:
- Button to download all data as CSV with columns: Date, Apoquel, Bath, Notes
- Button to download comprehensive build prompt as markdown file

## Animation & Interaction Details

### Hover States

- **Day cells**: 
  - Scale: 1.02
  - Add subtle shadow
  - Border color: slightly stronger primary tint
  - Transition: 0.15s ease

### Tap/Click States

- **Day cells**: Scale to 0.98 briefly
- **Activity toggle buttons**: Scale to 0.98 on press, then bounce to 1.05 when activated

### View Transitions

When switching between month/week view or navigating months/weeks:
- Fade out old view (opacity 0, translate Y -20px)
- Fade in new view (opacity 1, translate Y 0)
- Duration: 0.2s
- Use AnimatePresence from Framer Motion with mode="wait"

### Today Indicator

- Accent-colored ring around day cell (2px, `ring-2 ring-accent`)
- Subtle shadow with accent color tint (`shadow-lg shadow-accent/20`)
- Day number text in accent color

## Utility Functions Needed

### Date Utilities (date-utils.ts)

```typescript
// Format date as "YYYY-MM-DD" for storage keys
export function formatDateKey(date: Date): string

// Check if two dates are the same day
export function isSameDay(date1: Date, date2: Date): boolean

// Get start of week (Monday)
export function startOfWeek(date: Date): Date

// Get start of month
export function startOfMonth(date: Date): Date

// Get end of month
export function endOfMonth(date: Date): Date

// Get array of 42 dates for month view (includes prev/next month overflow)
// Starts from Monday of first week
export function getDaysInMonth(date: Date): Date[]

// Add months to a date
export function addMonths(date: Date, months: number): Date

// Add weeks to a date
export function addWeeks(date: Date, weeks: number): Date

// Get array of 7 dates for week view (Monday - Sunday)
export function getWeekDays(date: Date): Date[]

// Format as "January 2024"
export function formatMonthYear(date: Date): string

// Format as "Jan 15 - Jan 21, 2024"
export function formatWeekRange(date: Date): string
```

## Component Structure

### Main App Component (App.tsx)

State management:
- `activities`: CalendarData stored in persistent KV storage using `useKV`
- `currentDate`: Date - the currently viewed month/week
- `selectedDate`: Date | null - the day clicked to show quick log dialog
- `viewMode`: 'month' | 'week'
- `activeTab`: 'calendar' | 'analytics'

### DayCard Component

Props:
- `date: Date` - the date this card represents
- `isCurrentMonth: boolean` - whether this date is in the currently viewed month
- `isToday: boolean` - whether this is today
- `activities: CalendarData` - all activities data
- `onDayClick: (date: Date) => void` - callback when clicked
- `viewMode: 'month' | 'week'` - current view mode for sizing

Renders:
- Card component (from shadcn)
- Day number
- Activity indicators (conditional rendering based on activities for this date)
- Hover/press animations
- Conditional styling based on isToday, isCurrentMonth, isFuture

### QuickLogDialog Component

Props:
- `selectedDate: Date | null` - the selected date (null when closed)
- `activities: CalendarData` - all activities data
- `onUpdateActivities: (dateKey: string, activities: DayActivities) => void` - callback to update
- `onClose: () => void` - callback to close dialog

Renders:
- Dialog component (from shadcn)
- Formatted date header
- Apoquel toggle button
- Bath toggle button
- Notes textarea
- Handles future date logic
- Manages local comment state with auto-save

### Analytics Component

Props:
- `activities: CalendarData` - all activities data

Renders:
- Total statistics cards
- Monthly breakdown list
- CSV export button
- Build prompt download button

## Responsive Behavior

### Desktop (≥768px)
- Full 7-column grid
- Header with inline controls
- Comfortable spacing

### Mobile (<768px)
- Maintain 7-column grid but with smaller cells
- Month view: compact day cells with small indicators
- Week view: larger indicators (w-4 h-4) that are visible on mobile
- Stack header elements vertically (title, view toggles, navigation)
- Dialog takes full screen width with padding

## Accessibility Considerations

- All interactive elements have appropriate ARIA labels
- Focus states are visible and clear
- Color contrast ratios meet WCAG AA standards (4.5:1 minimum)
- Keyboard navigation supported (Tab, Enter, Escape)
- Activity colors (apoquel sage green, bath sky blue, notes warm yellow) are distinguishable for color-blind users

## shadcn Components to Use

Install/use these shadcn components:
- `button` - for all buttons
- `card` - for day cells
- `dialog` - for quick log panel
- `textarea` - for notes field
- `label` - for form labels
- `tabs` - for calendar/analytics switching
- `sonner` - for toast notifications

## Implementation Notes

1. **Week starts on Monday**: All calendar calculations should treat Monday as day 0 of the week
2. **Date key format**: Always use "YYYY-MM-DD" format for storage keys (e.g., "2024-01-15")
3. **Persist all changes immediately**: No save button needed, update storage on every activity toggle or comment change using functional updates
4. **Future date prevention**: Check if date > new Date() and disable logging if true
5. **Empty state**: When no activities logged yet, calendar still shows normally (no special empty state needed)
6. **Animation performance**: Use `framer-motion` with `whileHover`, `whileTap`, and `AnimatePresence`
7. **Today always visible**: When app loads, default view should show today's date

## Final Visual Polish

- Subtle shadows on cards that intensify on hover
- Smooth transitions between all states (0.2s duration)
- Generous white space and breathing room
- Rounded corners throughout (using radius system)
- Activity indicators perfectly circular
- Icons properly sized and weighted (Phosphor default sizes)
- Consistent padding and spacing using Tailwind's scale

## Example User Flow

1. User opens app → sees current month with today highlighted
2. User clicks today's date → quick log dialog appears
3. User taps "Apoquel" button → button turns sage green with bounce animation, indicator appears on calendar
4. User taps "Bath" button → button turns sky blue with bounce animation, indicator appears on calendar
5. User adds note "First bath after grooming" → auto-saves
6. User clicks outside dialog → dialog closes, calendar shows both indicators on today
7. User switches to week view → sees current week with larger cells and indicators
8. User clicks previous week → calendar slides to show previous week
9. User clicks "Today" button → returns to current week
10. User switches to Analytics tab → sees total stats and monthly breakdown
11. User downloads CSV export → gets file with all logged data
12. User closes app and reopens → all logged activities still visible

---

This prompt contains all the information needed to rebuild the Beau - Dog Care Calendar application from scratch, including all recent updates and improvements.