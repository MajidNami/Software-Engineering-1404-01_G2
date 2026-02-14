import { Trip, TripDay } from '@/types/trip';

export interface CategoryCost {
  category: string;
  totalCost: number;
  percentage: number;
}

/**
 * Calculate the total cost and percentage for each category in a trip
 * @param trip - The trip object containing all days and items
 * @returns Array of category costs with percentages
 */
export const calculateCategoryCosts = (trip: Trip): CategoryCost[] => {
  if (!trip || !trip.days || trip.total_cost === 0) {
    return [];
  }

  // Aggregate costs by category
  const categoryCostMap: Record<string, number> = {};

  trip.days.forEach((day: TripDay) => {
    day.items.forEach((item) => {
      const category = item.category || 'سایر';
      if (!categoryCostMap[category]) {
        categoryCostMap[category] = 0;
      }
      categoryCostMap[category] += item.cost;
    });
  });

  // Convert to array and calculate percentages
  const categoryCosts: CategoryCost[] = Object.entries(categoryCostMap).map(
    ([category, totalCost]) => ({
      category,
      totalCost,
      percentage: (totalCost / trip.total_cost) * 100,
    })
  );

  // Sort by total cost descending
  categoryCosts.sort((a, b) => b.totalCost - a.totalCost);

  return categoryCosts;
};

/**
 * Format a number as Persian currency
 * @param amount - The amount to format
 * @returns Formatted string with Persian digits and thousand separators
 */
export const formatPersianCurrency = (amount: number): string => {
  return amount.toLocaleString('fa-IR');
};
