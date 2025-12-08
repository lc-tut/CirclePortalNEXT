# CirclePortal Frontend

Next.js frontend for CirclePortal.

## Setup

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Run development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Top page
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── features/        # Feature-specific components
│   │   └── layouts/         # Layout components
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── utils.ts         # Utilities
│   └── types/               # TypeScript types
└── package.json
```

## Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint
npm run lint
```

## Technology Stack

- **Framework**: Next.js 15 (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS
- **Language**: TypeScript
- **Testing**: Vitest
- **Icons**: Lucide React
