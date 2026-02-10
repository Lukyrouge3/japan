"use client";

import { useState, useCallback, useMemo } from "react";
import dynamic from "next/dynamic";
import { Place } from "@/types/place";
import { useFilters } from "@/hooks/useFilters";
import FilterPanel from "./FilterPanel";
import DataTable from "./DataTable";
import PlaceCard from "./PlaceCard";
import StatsBar from "./StatsBar";
import { cn } from "@/lib/utils";
import {
  Map,
  Table2,
  LayoutGrid,
  PanelLeftClose,
  PanelLeft,
  ChevronDown,
} from "lucide-react";

const MapView = dynamic(() => import("./MapView"), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full rounded-xl bg-gray-100 animate-pulse flex items-center justify-center">
      <span className="text-gray-400 text-sm">Loading map...</span>
    </div>
  ),
});

type ViewMode = "map" | "table" | "cards";

interface DashboardProps {
  places: Place[];
}

export default function Dashboard({ places }: DashboardProps) {
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("map");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const {
    filters,
    sortField,
    sortDirection,
    sortedPlaces,
    toggleSort,
    updateFilter,
    toggleArrayFilter,
    resetFilters,
    hasActiveFilters,
    filteredPlaces,
  } = useFilters(places);

  const handleSelectPlace = useCallback((place: Place | null) => {
    setSelectedPlace((prev) =>
      prev?.name === place?.name ? null : place
    );
  }, []);

  const viewModes: { key: ViewMode; label: string; icon: React.ReactNode }[] = [
    { key: "map", label: "Map", icon: <Map className="w-4 h-4" /> },
    { key: "table", label: "Table", icon: <Table2 className="w-4 h-4" /> },
    { key: "cards", label: "Cards", icon: <LayoutGrid className="w-4 h-4" /> },
  ];

  return (
    <div className="flex h-[calc(100vh-73px)] overflow-hidden">
      {/* Sidebar - Desktop */}
      <div
        className={cn(
          "hidden lg:flex flex-col border-r border-gray-200 bg-white transition-all duration-300 overflow-hidden",
          sidebarOpen ? "w-[300px] min-w-[300px]" : "w-0 min-w-0"
        )}
      >
        <div className="p-5 overflow-y-auto flex-1">
          <FilterPanel
            places={places}
            filters={filters}
            onUpdateFilter={updateFilter}
            onToggleArrayFilter={toggleArrayFilter}
            onResetFilters={resetFilters}
            hasActiveFilters={hasActiveFilters}
            filteredCount={filteredPlaces.length}
            totalCount={places.length}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Toolbar */}
        <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-2">
            {/* Sidebar toggle - desktop */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg hover:bg-gray-100 transition-colors text-gray-400"
              title={sidebarOpen ? "Hide filters" : "Show filters"}
            >
              {sidebarOpen ? (
                <PanelLeftClose className="w-4 h-4" />
              ) : (
                <PanelLeft className="w-4 h-4" />
              )}
            </button>

            {/* Mobile filter toggle */}
            <button
              onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
              className={cn(
                "lg:hidden flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                mobileFiltersOpen || hasActiveFilters
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              Filters
              {hasActiveFilters && (
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              )}
              <ChevronDown
                className={cn(
                  "w-3.5 h-3.5 transition-transform",
                  mobileFiltersOpen && "rotate-180"
                )}
              />
            </button>

            <span className="text-xs text-gray-400 hidden sm:inline">
              {filteredPlaces.length} places
            </span>
          </div>

          {/* View mode toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
            {viewModes.map((mode) => (
              <button
                key={mode.key}
                onClick={() => setViewMode(mode.key)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-150",
                  viewMode === mode.key
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                )}
              >
                {mode.icon}
                <span className="hidden sm:inline">{mode.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Mobile Filters */}
        {mobileFiltersOpen && (
          <div className="lg:hidden border-b border-gray-200 bg-white p-4 overflow-y-auto max-h-[60vh]">
            <FilterPanel
              places={places}
              filters={filters}
              onUpdateFilter={updateFilter}
              onToggleArrayFilter={toggleArrayFilter}
              onResetFilters={resetFilters}
              hasActiveFilters={hasActiveFilters}
              filteredCount={filteredPlaces.length}
              totalCount={places.length}
            />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-auto p-4 bg-gray-50/50">
          {viewMode === "map" && (
            <div className="h-full min-h-[400px]">
              <MapView
                places={sortedPlaces}
                selectedPlace={selectedPlace}
                onSelectPlace={handleSelectPlace}
              />
            </div>
          )}

          {viewMode === "table" && (
            <DataTable
              places={sortedPlaces}
              selectedPlace={selectedPlace}
              onSelectPlace={handleSelectPlace}
              sortField={sortField}
              sortDirection={sortDirection}
              onToggleSort={toggleSort}
            />
          )}

          {viewMode === "cards" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
              {sortedPlaces.map((place) => (
                <PlaceCard
                  key={`${place.name}-${place.latitude}`}
                  place={place}
                  isSelected={selectedPlace?.name === place.name}
                  onSelect={handleSelectPlace}
                />
              ))}
              {sortedPlaces.length === 0 && (
                <div className="col-span-full text-center py-16 text-gray-400">
                  No places match your filters.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
