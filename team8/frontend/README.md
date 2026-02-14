# Frontend

React + Vite frontend for comments, media, and ratings.

## Setup

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## API Integration

Uses React Query for server state management. API requests automatically include authentication cookies.

Example:
```jsx
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const api = axios.create({ 
  baseURL: '/api',
  withCredentials: true
})

function Places() {
  const { data } = useQuery({
    queryKey: ['places'],
    queryFn: () => api.get('/places/').then(r => r.data)
  })
}
```

## Project Structure

```
src/
├── components/   # Reusable UI components
├── pages/        # Route pages
├── api/          # API client
├── hooks/        # Custom hooks
└── utils/        # Helpers
```

## Styling

Follows project standards:
- Font: Vazirmatn
- RTL layout
- Color palette: forest green, leaf green, persian gold
