# GitHub Spark Prompts for SoulSpot Bridge

**Version:** 3.0.0  
**Last Updated:** 2025-11-24  
**Purpose:** Step-by-step prompts to create SoulSpot Bridge using GitHub Spark  
**Reference:** https://docs.github.com/en/copilot/tutorials/spark/your-first-spark

---

## What is This Document?

This document provides **ready-to-use prompts** for GitHub Spark to generate the SoulSpot Bridge Web UI **iteratively**. Each prompt builds on the previous one, creating a complete music automation application.

GitHub Spark lets you create apps by describing what you want in natural language. Copy these prompts into GitHub Spark and watch it build your app!

---

## 🚀 Getting Started with GitHub Spark

1. Go to **https://githubnext.com/projects/copilot-workspace** or your GitHub Spark interface
2. Start a new Spark project
3. Copy and paste the prompts below **one at a time**
4. Review the generated code after each prompt
5. Test functionality before moving to the next prompt

---

## 📋 Iteration 1: Project Setup & Basic Structure

### Prompt 1.1: Initialize Project

```
Create a React + TypeScript music automation app called "SoulSpot Bridge" that syncs Spotify playlists and downloads tracks via Soulseek.

Setup requirements:
- Use Vite as the build tool
- Configure TypeScript with strict mode
- Add TailwindCSS for styling
- Set up React Router v6 for navigation
- Configure ESLint and Prettier

Create the following basic structure:
- src/app/App.tsx (main app component)
- src/app/Routes.tsx (route configuration)
- src/app/Layout.tsx (app layout with navigation)
- src/styles/globals.css (global styles)

The app should have a clean, modern dark theme with a sidebar navigation.
```

### Prompt 1.2: Design Tokens & Theme

```
Add a design system with design tokens to the SoulSpot Bridge app.

Create src/styles/tokens.ts with:
- Spacing scale (4px base: xs, sm, md, lg, xl, 2xl)
- Typography scale (xs to 3xl)
- Color palette: primary (blue), success (green), warning (yellow), error (red)
- Neutral colors: backgrounds, text colors, borders
- Border radius values (sm to full)
- Box shadow values

Also create src/styles/globals.css with:
- CSS custom properties for all design tokens
- Dark mode support using prefers-color-scheme
- Base typography styles
- Reset/normalize styles

Use these design tokens throughout the app for consistency.
```

---

## 📋 Iteration 2: Core UI Components

### Prompt 2.1: Button Component

```
Create a reusable Button component in src/components/ui/Button.tsx for SoulSpot Bridge.

Requirements:
- TypeScript with full prop types
- Variants: primary, secondary, ghost, danger
- Sizes: sm, md, lg
- Support for loading state with spinner
- Support for icons (before or after text)
- Full width option
- Disabled state styling
- Use TailwindCSS for styling
- Export ButtonProps type

Example usage:
<Button variant="primary" size="md" loading={isLoading}>
  Save Changes
</Button>
```

### Prompt 2.2: Input Component

```
Create a reusable Input component in src/components/ui/Input.tsx.

Requirements:
- TypeScript with props extending HTMLInputElement
- Support for label, error message, and hint text
- Different states: default, error, disabled
- Full width by default
- Use design tokens for spacing and colors
- Accessible with proper ARIA labels

Example:
<Input
  label="Search tracks"
  placeholder="Enter track name..."
  error={errors.query?.message}
  hint="Search by track, artist, or album"
/>
```

### Prompt 2.3: Badge & Progress Components

```
Create two UI components for SoulSpot Bridge:

1. Badge component (src/components/ui/Badge.tsx):
- Variants: default, success, warning, error, info
- Small, inline display
- TypeScript types

2. ProgressBar component (src/components/ui/ProgressBar.tsx):
- Props: value (0-100), label, variant, size
- Variants: primary, success, warning, error
- Sizes: sm, md, lg
- Animated fill
- Show percentage label

Use TailwindCSS and design tokens.
```

---

## 📋 Iteration 3: Card Components

### Prompt 3.1: Base Card Structure

```
Create a base Card component system in src/components/cards/ for SoulSpot Bridge.

Create Card.tsx with these sub-components:
- Card (container)
- CardHeader (with icon, title, badge)
- CardBody (content area)
- CardFooter (actions)

All should use design tokens and support:
- Hover effects (subtle shadow increase)
- Responsive design
- Dark mode
- Clean borders and spacing

Export all components and their TypeScript types.
```

### Prompt 3.2: StatusCard Component

```
Create a StatusCard component in src/components/cards/StatusCard.tsx for showing module health.

Props:
- moduleId: string
- moduleName: string
- icon: ReactNode
- status: 'active' | 'warning' | 'inactive' | 'loading'
- lastCheck: string
- healthPercentage: number
- onViewDetails?: () => void
- autoRefresh?: boolean

Features:
- Display module icon and name
- Show colored badge based on status (green/yellow/red)
- Show health percentage with ProgressBar
- Display last check time
- Optional "View Details" button
- Auto-refresh support (poll every 30s)

Use the base Card components and make it visually appealing.
```

### Prompt 3.3: ProgressCard Component

```
Create a ProgressCard component in src/components/cards/ProgressCard.tsx for download progress.

Props:
- downloadId: string
- title: string
- progress: number (0-100)
- status: 'downloading' | 'paused' | 'completed' | 'failed'
- bytesDownloaded: number
- bytesTotal: number
- timeRemaining?: string
- onPause?: () => void
- onResume?: () => void
- onCancel?: () => void

Features:
- Large progress bar showing download %
- Format and display file sizes (formatBytes utility)
- Show time remaining if available
- Action buttons: Pause/Resume/Cancel based on status
- Status-based coloring (blue/green/red)
- Accessible with ARIA labels
```

### Prompt 3.4: DataCard & ListCard Components

```
Create two more card components for SoulSpot Bridge:

1. DataCard (src/components/cards/DataCard.tsx):
Props: trackId, title, subtitle, imageUrl, metadata array, actions array
- Display album art image
- Show track title and artist
- Metadata list (album, duration, quality)
- Action buttons (Play, Download, More)

2. ListCard (src/components/cards/ListCard.tsx):
Props: title, items array, emptyMessage, onClearAll, onSort
- List container with header showing item count
- Scrollable list area (max height 400px)
- Each item shows: icon, title, subtitle, delete button
- Empty state message
- Optional "Clear All" button
- Optional sort button

Both should use base Card components and design tokens.
```

---

## 📋 Iteration 4: API Integration

### Prompt 4.1: API Client

```
Create an API client service in src/services/api/client.ts for SoulSpot Bridge.

Requirements:
- Use axios for HTTP requests
- Base URL: /api
- Request interceptor: add Authorization header with token from localStorage
- Response interceptor: handle 401 errors and refresh tokens
- Methods: get, post, put, patch, delete (all typed with generics)
- Automatic JSON parsing
- Error handling

Also create src/types/api.ts with:
- ApiResponse<T> type
- ApiError type
- Common API response types

The client should unwrap response.data.data automatically.
```

### Prompt 4.2: TypeScript API Types

```
Create comprehensive TypeScript type definitions in src/types/api.ts for SoulSpot Bridge.

Define types for:
1. ModuleStatus (id, name, status, health, lastCheck, errors)
2. SoulseekDownload (id, trackId, filename, progress, status, bytes, speed, timeRemaining)
3. SpotifyTrack (id, name, artists, album, duration, uri)
4. SpotifyAlbum (id, name, artists, images, release_date)
5. SpotifyPlaylist (id, name, description, owner, tracks, images)
6. LibraryTrack (id, title, artist, album, metadata, filePath)
7. User (id, username, email, spotifyConnected, soulseekConnected)
8. AuthTokens (accessToken, refreshToken, expiresAt)

All types should be fully typed with proper TypeScript interfaces.
```

### Prompt 4.3: Custom React Hooks

```
Create custom React hooks for SoulSpot Bridge:

1. src/hooks/useApi.ts:
- useApiQuery: wrapper for React Query useQuery
- useApiMutation: wrapper for React Query useMutation

2. src/hooks/useModuleStatus.ts:
- useModuleStatus(moduleId): fetch single module status (refetch every 30s)
- useAllModulesStatus(): fetch all modules status

3. src/hooks/useToast.ts:
- useToast(): returns { success, error, warning, info, dismiss }
- Uses ToastContext

All should use TanStack Query and TypeScript.
Include proper error handling and loading states.
```

---

## 📋 Iteration 5: Pages & Routing

### Prompt 5.1: Dashboard Page

```
Create a Dashboard page in src/modules/dashboard/DashboardPage.tsx for SoulSpot Bridge.

Features:
- Page header with title and description
- Fetch all modules status using useAllModulesStatus hook
- Show warning AlertCard if any modules are inactive
- Display grid of StatusCard components (3 columns on desktop)
- Show loading skeletons while fetching
- Handle errors gracefully

Modules to display:
- Soulseek, Spotify, Library, Metadata, Dashboard, Settings

Each StatusCard should show module health and status.
Make it responsive and visually appealing.
```

### Prompt 5.2: Soulseek Downloads Page

```
Create Soulseek Downloads page in src/modules/soulseek/SoulseekDownloadsPage.tsx.

Features:
- Page header: "Downloads" with subtitle
- Fetch downloads using React Query (refetch every 5s)
- Two sections:
  1. "Active Downloads": Show ProgressCard for each downloading/paused item
  2. "Download Queue": Show ListCard with queued items

Actions:
- Pause/Resume downloads (useMutation)
- Cancel downloads (useMutation with confirmation)
- Clear all from queue

Include:
- formatDuration utility function
- Empty states for no downloads
- Error handling
- Toast notifications on actions
```

### Prompt 5.3: Spotify Search Page

```
Create Spotify Search page in src/modules/spotify/SpotifySearchPage.tsx.

Features:
- Page header: "Search Spotify"
- Search form using React Hook Form + Zod validation
- Search input with submit button
- Results grid (3 columns) showing DataCard for each track
- Each track card shows: album art, track name, artist, album, duration
- Download button on each card
- Empty state before search
- Loading state during search
- Error handling

Use:
- useSpotifySearch hook (create with React Query)
- z.object({ query: z.string().min(1) }) validation
- DataCard component
- Toast for success/error messages
```

### Prompt 5.4: Navigation & Routes

```
Update SoulSpot Bridge routing and navigation:

1. src/app/Routes.tsx:
Add routes for:
- / → redirect to /dashboard
- /dashboard → DashboardPage
- /soulseek/downloads → SoulseekDownloadsPage
- /spotify/search → SpotifySearchPage
- /spotify/playlists → placeholder
- /library → placeholder
- /settings → placeholder

2. src/components/layout/Navigation.tsx:
Create sidebar navigation with:
- App logo/title at top
- Nav links with icons:
  - 🏠 Dashboard
  - 🔍 Search
  - 📝 Playlists
  - ⬇️ Downloads
  - 📚 Library
  - ⚙️ Settings
- Active link styling
- Responsive (collapse on mobile)

Use NavLink from react-router-dom for active states.
```

---

## 📋 Iteration 6: State Management & Real-time

### Prompt 6.1: Context Providers

```
Create context providers for SoulSpot Bridge:

1. src/contexts/AuthContext.tsx:
- AuthProvider component
- State: user, isAuthenticated, isLoading
- Methods: login, logout, refreshAuth
- Fetch user on mount
- Handle token refresh
- Export useAuth hook

2. src/contexts/ToastContext.tsx:
- ToastProvider component
- State: toasts array
- Methods: addToast, removeToast
- Auto-dismiss after duration (default 5s)
- Export useToast hook

3. src/components/ui/ToastContainer.tsx:
- Render toasts in fixed position (top-right)
- Support 4 types: success, error, warning, info
- Animate in/out
- Dismiss button
- Stack multiple toasts

Wrap App.tsx with both providers.
```

### Prompt 6.2: Real-time Updates with SSE

```
Create real-time update support using Server-Sent Events for SoulSpot Bridge.

Create src/hooks/useEventSource.ts:
- Custom hook that connects to SSE endpoint
- Props: url (string | null), options { events: string[] }
- Returns: { data, error, isConnected }
- Automatically parse JSON from event.data
- Clean up on unmount
- Support multiple event types
- Reconnect on error

Update ProgressCard to use useEventSource:
- Connect to `/api/downloads/${downloadId}/events`
- Listen for 'progress' events
- Update progress, bytes, status in real-time
- Only connect if realTimeUpdates prop is true

This enables live download progress without polling.
```

---

## 📋 Iteration 7: Forms & Validation

### Prompt 7.1: Search Form with Validation

```
Enhance search functionality in SoulSpot Bridge with proper form handling.

Update SpotifySearchPage to use:
- React Hook Form for form state
- Zod for validation schema
- Display validation errors inline
- Disable submit while loading
- Clear form option
- Search history (optional)

Create reusable ActionCard component:
Props: title, icon, schema (Zod), fields array, onSubmit, submitLabel
- Render form with react-hook-form
- Auto-generate inputs from fields config
- Show validation errors
- Loading state on submit button
- Support secondary action buttons

Use ActionCard for search form.
```

---

## 📋 Iteration 8: Polish & Accessibility

### Prompt 8.1: Loading States & Skeletons

```
Add loading states to SoulSpot Bridge:

1. Create skeleton components:
- StatusCardSkeleton
- DataCardSkeleton
- ListSkeleton
- Use pulsing animation (animate-pulse)

2. Update all pages to show skeletons while loading:
- Dashboard: 6 StatusCardSkeletons in grid
- Downloads: 2 ProgressCardSkeletons
- Search: Show skeleton after search starts

3. Add LoadingSpinner component:
- Sizes: sm, md, lg
- Use in buttons when loading
- Spinning animation

Make all loading states smooth and professional.
```

### Prompt 8.2: Error Boundaries & 404

```
Add error handling to SoulSpot Bridge:

1. Create ErrorBoundary component:
- Catch React errors
- Show friendly error UI
- Log errors to console
- Reset button to recover
- Wrap entire app

2. Create NotFoundPage (404):
- Friendly message
- Link back to dashboard
- Illustration or icon
- Add to routes as catch-all (path="*")

3. Add error states to data fetching:
- Show AlertCard on API errors
- Retry button
- Helpful error messages

Make errors user-friendly and recoverable.
```

### Prompt 8.3: Accessibility Improvements

```
Improve accessibility in SoulSpot Bridge to meet WCAG 2.1 AA:

1. Add ARIA labels to all interactive elements:
- Buttons: aria-label for icon-only buttons
- Links: aria-current for active nav links
- Forms: aria-describedby for hints/errors
- Progress: aria-live="polite" for progress updates

2. Ensure keyboard navigation:
- All interactive elements focusable
- Focus indicators visible (focus-visible)
- Tab order logical
- Escape closes modals/dialogs

3. Color contrast:
- Check all text meets 4.5:1 ratio
- Don't rely on color alone for meaning
- Add text labels to status indicators

4. Screen reader support:
- Semantic HTML (nav, main, article)
- Heading hierarchy (h1 → h2 → h3)
- Skip to main content link

Test with keyboard only and screen reader.
```

---

## 📋 Iteration 9: Testing

### Prompt 9.1: Unit Tests Setup

```
Set up testing infrastructure for SoulSpot Bridge:

1. Install dependencies:
- @testing-library/react
- @testing-library/jest-dom
- @testing-library/user-event
- vitest

2. Create test utilities in src/test-utils.tsx:
- renderWithProviders: wraps component with Router, QueryClient, Contexts
- Custom render function
- Mock providers

3. Write unit tests for:
- Button component (Button.test.tsx)
- StatusCard component (StatusCard.test.tsx)
- Input component (Input.test.tsx)

Each test should cover:
- Rendering
- Props
- User interactions
- Different states
- Accessibility

Use descriptive test names and arrange-act-assert pattern.
```

---

## 📋 Iteration 10: Build & Deploy

### Prompt 10.1: Production Build Config

```
Configure SoulSpot Bridge for production deployment:

1. Update vite.config.ts:
- Enable source maps
- Configure code splitting (manualChunks)
  - react-vendor: react, react-dom, react-router-dom
  - query-vendor: @tanstack/react-query
  - form-vendor: react-hook-form, zod
- Optimize build for production
- Configure proxy for /api → http://localhost:8765

2. Create .env.example:
- VITE_API_BASE_URL
- VITE_ENABLE_DARK_MODE
- VITE_ENABLE_DEV_TOOLS

3. Add build scripts to package.json:
- build: production build
- preview: preview production build
- type-check: run TypeScript compiler

4. Add deployment instructions to README.md

Test production build with `npm run build && npm run preview`.
```

---

## 🎯 Usage Instructions

### How to Use These Prompts

1. **Start with Iteration 1** - Always begin with project setup
2. **Go in order** - Each iteration builds on previous ones
3. **Test after each prompt** - Verify functionality before moving forward
4. **Customize as needed** - Adapt prompts to your specific needs
5. **Review generated code** - GitHub Spark is smart but may need tweaks

### Example Workflow

```bash
# 1. Copy Prompt 1.1 into GitHub Spark
# 2. Wait for generation
# 3. Review and test the code
# 4. Copy Prompt 1.2
# 5. Continue through iterations
# ... repeat until complete
```

### Tips for Success

- ✅ Read each prompt before pasting
- ✅ Let Spark finish generating before next prompt
- ✅ Test the app frequently in browser
- ✅ Fix any errors before continuing
- ✅ Customize design tokens to match your brand
- ❌ Don't skip iterations
- ❌ Don't rush through prompts
- ❌ Don't ignore TypeScript errors

---

## �� Additional Resources

- **GitHub Spark Tutorial**: https://docs.github.com/en/copilot/tutorials/spark/your-first-spark
- **Complete Specification**: [GITHUB_SPARK_WEB_UI.md](./GITHUB_SPARK_WEB_UI.md)
- **Quick Start Guide**: [GITHUB_SPARK_QUICK_START.md](./GITHUB_SPARK_QUICK_START.md)
- **Design System**: [UI_DESIGN_SYSTEM.md](./UI_DESIGN_SYSTEM.md)

---

## 🆘 Troubleshooting

**Spark doesn't generate what I want:**
- Make prompts more specific
- Add examples to prompts
- Break down complex prompts into smaller ones

**TypeScript errors:**
- Ask Spark to "fix TypeScript errors in [file]"
- Ensure all imports are correct
- Check tsconfig.json is strict mode

**Components don't look right:**
- Verify design tokens are loaded
- Check TailwindCSS is configured
- Ask Spark to "improve styling of [component]"

**API integration fails:**
- Ensure backend is running on localhost:8765
- Check proxy configuration in vite.config.ts
- Verify API endpoints match backend

---

**Ready to build?** Start with Prompt 1.1 and create your SoulSpot Bridge app with GitHub Spark! 🚀

**AI-Model:** GitHub Copilot
