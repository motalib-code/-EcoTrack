# Project: EcoTrack — Carbon Footprint Awareness Platform

## Architecture

### Tech Stack
- **Frontend**: Next.js 15+ (App Router), TypeScript strict, Tailwind CSS, Shadcn UI, Framer Motion, Recharts
- **Forms**: React Hook Form + Zod validation
- **Auth**: NextAuth.js v5 (email/password + Google/GitHub OAuth), JWT + refresh tokens
- **Database**: PostgreSQL + Prisma ORM
- **Caching**: Redis (ioredis) for dashboard aggregations
- **Testing**: Vitest + React Testing Library
- **Styling**: Dark/Light mode, emerald/green palette, glassmorphism

### Module Boundaries
1. **Foundation** — Next.js project scaffolding, Tailwind/Shadcn setup, theme system, layout components
2. **Database** — Prisma schema, migrations, seed script
3. **Auth** — NextAuth config, login/register pages, OAuth, middleware, session management
4. **Calculator** — Multi-category carbon calculator with EPA/IPCC factors
5. **Dashboard** — Analytics dashboard with KPI cards, charts (pie, line, bar, progress)
6. **Recommendations** — Personalized recommendation engine
7. **Goals & Gamification** — Goal setting, sustainability scoring (A+ to F), badges, streaks
8. **API & Server Actions** — REST endpoints, server actions, rate limiting, security headers
9. **Landing Page** — Hero section, features, CTA — premium design inspired by reference prototype
10. **Testing & Polish** — 30+ tests, ESLint/Prettier, build verification

### Data Flow
```
User → Auth (NextAuth) → Protected Routes
  → Calculator → Emission Records (Prisma/PostgreSQL)
  → Dashboard ← Aggregated Data (Redis cache)
  → Recommendations Engine ← User Emission Data
  → Goals/Gamification ← Achievement Tracking
```

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Foundation & Database | Next.js 15 setup, Tailwind, Shadcn, Prisma schema, seed script, theme system | none | PLANNED |
| M2 | Auth System | NextAuth v5, email/password, Google/GitHub OAuth, JWT, middleware, login/register UI | M1 | PLANNED |
| M3 | Carbon Calculator | Multi-category calculator (5 categories), EPA/IPCC factors, form with React Hook Form + Zod, results display | M1 | PLANNED |
| M4 | Dashboard & Analytics | KPI cards, pie/doughnut chart, line chart, bar chart, goal progress, Framer Motion animations | M1, M2 | PLANNED |
| M5 | Recommendations, Goals & Gamification | Recommendation engine, goal CRUD, sustainability scoring A+-F, badges, streaks | M1, M2, M3 | PLANNED |
| M6 | Landing Page & Polish | Hero section, feature sections, responsive design, animations, dark/light mode polish | M1 | PLANNED |
| M7 | API Security & Testing | Rate limiting, CSRF, security headers, 30+ tests, ESLint, build verification | M1-M6 | PLANNED |

## Interface Contracts

### Auth ↔ All Protected Routes
- `getServerSession()` returns `{ user: { id, email, name, image } }` or `null`
- Middleware protects `/dashboard/*`, `/calculator/*`, `/goals/*`, `/api/protected/*`
- Unauthenticated → redirect to `/auth/login` (pages) or 401 (API)

### Calculator ↔ Database
- `EmissionRecord { id, userId, category, subcategory, value, unit, co2Amount, factors, date }`
- Categories: `TRANSPORT | ENERGY | FOOD | SHOPPING | WASTE`
- Server action: `createEmissionRecord(data: EmissionInput): Promise<EmissionRecord>`

### Dashboard ↔ Database/Redis
- `getDashboardData(userId): { monthly, annual, byCategory, trend, goals }`
- Redis cache key: `dashboard:${userId}` with 5-min TTL
- Invalidate on new emission record creation

### Recommendations ↔ User Data
- `getRecommendations(userId): Recommendation[]`
- Each: `{ title, description, category, co2Savings, difficulty, costImpact, impactScore }`

### Goals & Scoring
- `SustainabilityScore { userId, score: number, grade: 'A+' | 'A' | ... | 'F', breakdown }`
- `Goal { id, userId, targetReduction, currentEmissions, baselineEmissions, deadline, status }`
- Grade thresholds: A+ (90-100), A (85-89), B+ (80-84), B (75-79), C+ (70-74), C (65-69), D (50-64), F (<50)

## Code Layout

```
/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout with providers
│   │   ├── page.tsx                # Landing page
│   │   ├── globals.css             # Global styles + Tailwind
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── error/page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── calculator/
│   │   │   └── page.tsx
│   │   ├── goals/
│   │   │   └── page.tsx
│   │   ├── recommendations/
│   │   │   └── page.tsx
│   │   └── api/
│   │       ├── auth/[...nextauth]/route.ts
│   │       ├── emissions/route.ts
│   │       ├── dashboard/route.ts
│   │       ├── recommendations/route.ts
│   │       └── goals/route.ts
│   ├── components/
│   │   ├── ui/                     # Shadcn UI components
│   │   ├── layout/                 # Navbar, Footer, Sidebar
│   │   ├── dashboard/              # KPI cards, charts
│   │   ├── calculator/             # Calculator form, results
│   │   ├── auth/                   # Login/Register forms
│   │   ├── goals/                  # Goal cards, progress
│   │   ├── recommendations/        # Recommendation cards
│   │   └── landing/                # Hero, features sections
│   ├── lib/
│   │   ├── auth.ts                 # NextAuth config
│   │   ├── prisma.ts               # Prisma client singleton
│   │   ├── redis.ts                # Redis client
│   │   ├── emission-factors.ts     # EPA/IPCC emission factors
│   │   ├── calculator.ts           # Calculation logic
│   │   ├── recommendations.ts      # Recommendation engine
│   │   ├── scoring.ts              # Sustainability scoring
│   │   ├── validators.ts           # Zod schemas
│   │   └── utils.ts                # Utility functions
│   ├── actions/
│   │   ├── emissions.ts            # Server actions for emissions
│   │   ├── goals.ts                # Server actions for goals
│   │   └── dashboard.ts            # Server actions for dashboard
│   ├── hooks/
│   │   ├── use-theme.ts
│   │   └── use-dashboard.ts
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   └── providers/
│       ├── theme-provider.tsx
│       └── session-provider.tsx
├── prisma/
│   ├── schema.prisma
│   ├── seed.ts
│   └── migrations/
├── __tests__/
│   ├── calculator.test.ts
│   ├── scoring.test.ts
│   ├── recommendations.test.ts
│   ├── auth.test.ts
│   ├── api/
│   │   ├── emissions.test.ts
│   │   └── goals.test.ts
│   └── components/
│       ├── dashboard.test.tsx
│       └── calculator.test.tsx
├── public/
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── vitest.config.ts
├── package.json
└── README.md
```

## Design Reference
- App name: **EcoTrack**
- Color palette: Emerald primary (#00d4aa / #10b981), teal accents (#2dd4bf), amber warnings (#f59e0b), slate neutrals
- Glassmorphism: `backdrop-filter: blur(16px)`, semi-transparent backgrounds
- Typography: Inter font family
- Reference prototype: `C:\Users\91720\.gemini\antigravity\brain\847113ce-4fba-4b8c-ba8c-e36486a2613c\scratch\reference\`
