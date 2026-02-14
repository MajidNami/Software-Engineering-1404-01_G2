import {
  MapPin,
  Utensils,
  Building,
  Coffee,
  Trees,
  Landmark,
  Theater,
  Dumbbell,
  ShoppingBag,
  Building2,
  Cross,
  Activity,
} from 'lucide-react';
import { categories } from '../data/mockPlaces';

interface CategoryFilterProps {
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
}

const iconMap: { [key: string]: any } = {
  MapPin,
  Utensils,
  Building,
  Coffee,
  Trees,
  Landmark,
  Theater,
  Dumbbell,
  ShoppingBag,
  Hospital: Building2,
  Pill: Cross,
  Stethoscope: Activity,
};

export default function CategoryFilter({
  selectedCategory,
  onCategoryChange,
}: CategoryFilterProps) {
  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-4 max-h-[400px] overflow-auto">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">دسته بندی ها</h3>
      <div className="flex flex-col gap-3 px-2">
        {categories.map((category) => {
          const Icon = iconMap[category.icon];
          const isSelected = selectedCategory === category.id;

          return (
            <button
              key={category.id}
              onClick={() => onCategoryChange(category.id)}
              className={`flex gap-2 items-center p-3 rounded-full border-2 transition-all ${
                isSelected
                  ? 'border-orange-600 bg-orange-50 text-orange-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-orange-300 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium truncate">{category.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
