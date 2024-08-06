import {
  Density,
  Mode,
  applyDensity,
  applyMode,
} from '@cloudscape-design/global-styles'
import '@cloudscape-design/global-styles/index.css'
import React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Session from './Session'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'

applyMode(Mode.Light)
applyDensity(Density.Comfortable)

const router = createBrowserRouter([
  {
    path: '/',
    element: <Session />,
  },
])

const root = createRoot(document.getElementById('root'))
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
