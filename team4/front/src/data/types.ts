export interface RouteResponse {
  routes: Route[]
}

export interface Route {
  overview_polyline: OverviewPolyline
  legs: Leg[]
}

export interface OverviewPolyline {
  points: string
}

export interface Leg {
  summary: string
  distance: Distance
  duration: Duration
  steps: Step[]
}

export interface Distance {
  value: number
  text: string
}

export interface Duration {
  value: number
  text: string
}

export interface Step {
  name: string
  instruction: string
  bearing_after: number
  type: string
  modifier?: string
  distance: Distance2
  duration: Duration2
  polyline: string
  start_location: number[]
  exit?: number
}

export interface Distance2 {
  value: number
  text: string
}

export interface Duration2 {
  value: number
  text: string
}
