import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h1>تیم 8 - سیستم نظرات، رسانه و امتیازدهی</h1>
          <p style={{ marginTop: '1rem', color: '#666' }}>
            در حال توسعه...
          </p>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
