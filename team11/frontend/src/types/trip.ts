export type TripStyle = 'SOLO' | 'COUPLE' | 'FAMILY' | 'FRIENDS' | 'BUSINESS';
export type TripDensity = 'RELAXED' | 'BALANCED' | 'INTENSIVE';
export type BudgetLevel = 'ECONOMY' | 'MEDIUM' | 'LUXURY';
export type TripStatus = 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
export type ItemType = 'VISIT' | 'FOOD' | 'STAY' | 'TRANSPORT' | 'ACTIVITY';
export type CategoryType = 'HISTORICAL' | 'SHOPPING' | 'RECREATIONAL' | 'RELIGIOUS' | 'NATURAL' | 'DINING' | 'STUDY' | 'EVENTS';

export interface TripItem {
  id: number; // Changed to number as per API
  type: ItemType;
  title: string;
  category: CategoryType;
  start_time: string; // snake_case for API response
  end_time: string; // snake_case for API response
  duration_minutes?: number; // Optional field
  summery?: string; // Optional field
  cost: number; // Float in API response
  address?: string; // Optional field
  url?: string | null; // Optional field
}

export interface TripDay {
  day_number: number;
  date: string;
  items: TripItem[];
}

export interface Trip {
  id: number; // Changed to number as per API
  title: string;
  province: string;
  city: string;
  start_date: string; // snake_case for API response
  end_date: string; // snake_case for API response
  duration_days: number;
  style: TripStyle;
  budget_level: BudgetLevel;
  density?: TripDensity; // Optional field
  interests?: CategoryType[]; // Optional field
  status: TripStatus; // Default is ACTIVE
  total_cost: number; // Float in API response
  days: TripDay[];
  created_at: string; // snake_case for API response
}

// API Payloads
export interface CreateTripPayload {
  province: string;
  city: string;
  startDate: string; // camelCase for API request
  endDate?: string; // Optional field, camelCase for API request
  style: TripStyle | null;
  density?: TripDensity; // Optional field
  interests?: CategoryType[]; // Optional field
  budget_level: BudgetLevel | null;
}

export interface UpdateTripPayload {
  budget_level?: BudgetLevel;
  density?: TripDensity; // Optional field
}

export interface UpdateTripItemPayload {
  start_time?: string;
  end_time?: string;
  estimated_cost?: string;
}

export interface ReplaceItemPayload {
  new_place_id: string;
  new_place_data?: {
    title: string;
    category: CategoryType;
    estimated_cost: string;
    address?: string;
  };
}

export interface BulkCreateItemPayload {
  item_type: ItemType;
  place_ref_id: string;
  title: string;
  category: CategoryType;
  start_time: string;
  end_time: string;
  estimated_cost: string;
  order_index: number;
}

// API Responses
// Destination Suggest API
export type SuggestSeason = 'spring' | 'summer' | 'fall' | 'winter';

export type SuggestTravelStyle = 'SOLO' | 'COUPLE' | 'FAMILY' | 'FRIENDS' | 'BUSINESS';

export interface DestinationSuggestRequest {
  season: SuggestSeason;
  budget_level: BudgetLevel;
  travel_style: SuggestTravelStyle;
  interests?: string[];
}

export interface DestinationSuggestion {
  city: string;
  province: string;
  score: number;
  reason: string;
  highlights: string[];
  best_season: SuggestSeason;
  estimated_cost: string;
  duration_days: number;
  description: string;
  categories: string[];
}

export interface DestinationSuggestResponse {
  success: boolean;
  count: number;
  suggestions: DestinationSuggestion[];
}
export interface CostBreakdownResponse {
  total_estimated_cost: number;
  breakdown_by_category: {
    [key in CategoryType]?: {
      amount: number;
      percentage: number;
      count: number;
    };
  };
  breakdown_by_day: Array<{
    day_index: number;
    date: string;
    total_cost: number;
    item_count: number;
  }>;
}

export interface TripHistoryItem {
  id: number;
  title: string;
  province: string;
  city: string;
  start_date: string;
  end_date: string;
  style: string;
  density?: string;
  budget_level: string;
  interests?: string[];
  total_cost: number;
  status: string;
  created_at: string;
}

export interface TripHistoryResponse {
  count: number;
  results: TripHistoryItem[];
}

export interface TripItemWithDay extends TripItem {
  day_number: number;
  date: string;
}

// Item Alternatives API
export interface AlternativePlace {
  id: string;
  title: string;
  category: CategoryType;
  address?: string;
  lat?: number;
  lng?: number;
  entry_fee?: number;
  price_tier?: 'FREE' | 'BUDGET' | 'MODERATE' | 'LUXURY';
  rating?: number;
  distance?: number;
  recommendation_reason?: string;
}

export interface ItemAlternativesResponse {
  success: boolean;
  item_id: number;
  current_place: {
    place_id: string;
    title: string;
    category: CategoryType;
    lat?: number;
    lng?: number;
    estimated_cost: number;
  };
  alternatives: AlternativePlace[];
  count: number;
}
