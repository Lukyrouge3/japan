"use client";

import { useMemo } from "react";
import { Place, Filters } from "@/types/place";
import {
  cn,
  getUniqueValues,
  getUniqueTags,
  getTypeIcon,
} from "@/lib/utils";
import { Search, X, RotateCcw, SlidersHorizontal } from "lucide-react";

interface FilterPanelProps {
  places: Place[];
  filters: Filters;
  onUpdateFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  onToggleArrayFilter: (
    key: "cities" | "types" | "priceRanges" | "tags",
    value: string
  ) => void;
  onResetFilters: () => void;
  hasActiveFilters: boolean;
  filteredCount: number;
  totalCount: number;
}

function FilterSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
        {title}
      </h4>
      {children}
    </div>
  );
}

function Chip({
  label,
  active,
  onClick,
  icon,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
  icon?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-150",
        active
          ? "bg-blue-100 text-blue-700 ring-1 ring-blue-200"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
      )}
    >
      {icon && <span className="text-xs">{icon}</span>}
      {label}
    </button>
  );
}

export default function FilterPanel({
  places,
  filters,
  onUpdateFilter,
  onToggleArrayFilter,
  onResetFilters,
  hasActiveFilters,
  filteredCount,
  totalCount,
}: FilterPanelProps) {
  const cities = useMemo(() => getUniqueValues(places, "city"), [places]);
  const types = useMemo(() => getUniqueValues(places, "type"), [places]);
  const priceRanges = useMemo(() => {
    const prs = places
      .map((p) => p.price_range)
      .filter((v): v is string => typeof v === "string");
    return [...new Set(prs)].sort((a, b) => a.length - b.length);
  }, [places]);
  const tags = useMemo(() => getUniqueTags(places), [places]);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-gray-400" />
          <h3 className="font-semibold text-sm text-gray-700">Filters</h3>
        </div>
        {hasActiveFilters && (
          <button
            onClick={onResetFilters}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        )}
      </div>

      {/* Count */}
      <div className="text-xs text-gray-400">
        Showing{" "}
        <span className="font-semibold text-gray-700">{filteredCount}</span> of{" "}
        <span className="font-medium text-gray-500">{totalCount}</span> places
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search places..."
          value={filters.search}
          onChange={(e) => onUpdateFilter("search", e.target.value)}
          className="w-full pl-9 pr-8 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:border-blue-300 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
        />
        {filters.search && (
          <button
            onClick={() => onUpdateFilter("search", "")}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 text-gray-400 hover:text-gray-600"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* City filter */}
      <FilterSection title="City">
        <div className="flex flex-wrap gap-1.5">
          {cities.map((city) => (
            <Chip
              key={city}
              label={city}
              active={filters.cities.includes(city)}
              onClick={() => onToggleArrayFilter("cities", city)}
            />
          ))}
        </div>
      </FilterSection>

      {/* Type filter */}
      <FilterSection title="Type">
        <div className="flex flex-wrap gap-1.5">
          {types.map((type) => (
            <Chip
              key={type}
              label={type}
              active={filters.types.includes(type)}
              onClick={() => onToggleArrayFilter("types", type)}
              icon={getTypeIcon(type)}
            />
          ))}
        </div>
      </FilterSection>

      {/* Price Range filter */}
      <FilterSection title="Price Range">
        <div className="flex flex-wrap gap-1.5">
          {priceRanges.map((pr) => (
            <Chip
              key={pr}
              label={pr}
              active={filters.priceRanges.includes(pr)}
              onClick={() => onToggleArrayFilter("priceRanges", pr)}
            />
          ))}
        </div>
      </FilterSection>

      {/* Rating filter */}
      <FilterSection title={`Rating (${filters.ratingMin}–${filters.ratingMax})`}>
        <div className="space-y-2 px-1">
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-400 w-4">1</span>
            <input
              type="range"
              min={1}
              max={10}
              value={filters.ratingMin}
              onChange={(e) =>
                onUpdateFilter(
                  "ratingMin",
                  Math.min(Number(e.target.value), filters.ratingMax)
                )
              }
              className="flex-1 accent-blue-500 h-1.5"
            />
            <input
              type="range"
              min={1}
              max={10}
              value={filters.ratingMax}
              onChange={(e) =>
                onUpdateFilter(
                  "ratingMax",
                  Math.max(Number(e.target.value), filters.ratingMin)
                )
              }
              className="flex-1 accent-blue-500 h-1.5"
            />
            <span className="text-xs text-gray-400 w-6">10</span>
          </div>
        </div>
      </FilterSection>

      {/* Tags filter */}
      <FilterSection title="Tags">
        <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
          {tags.map((tag) => (
            <Chip
              key={tag}
              label={tag}
              active={filters.tags.includes(tag)}
              onClick={() => onToggleArrayFilter("tags", tag)}
            />
          ))}
        </div>
      </FilterSection>
    </div>
  );
}
