// lib/routes.ts
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  DASHBOARD: '/dashboard'
} as const

export type RouteType = typeof ROUTES[keyof typeof ROUTES]
