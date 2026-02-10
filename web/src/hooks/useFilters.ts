"use client";

import { useState, useMemo, useCallback } from "react";
import { Place, Filters, SortField, SortDirection } from "@/types/place";
import { filterPlaces } from "@/lib/utils";

const defaultFilters: Filters = {
  search: "",
  cities: [],
  types: [],
  priceRanges: [],
  tags: [],
  ratingMin: 1,
  ratingMax: 10,
};

export function useFilters(places: Place[]) {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [sortField, setSortField] = useState<SortField>("rating");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const filteredPlaces = useMemo(
    () => filterPlaces(places, filters),
    [places, filters]
  );

  const sortedPlaces = useMemo(() => {
    const sorted = [...filteredPlaces].sort((a, b) => {
      let aVal: string | number | null = null;
      let bVal: string | number | null = null;

      switch (sortField) {
        case "name":
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case "type":
          aVal = a.type;
          bVal = b.type;
          break;
        case "city":
          aVal = a.city ?? "";
          bVal = b.city ?? "";
          break;
        case "rating":
          aVal = a.rating ?? 0;
          bVal = b.rating ?? 0;
          break;
        case "price_range":
          aVal = (a.price_range ?? "").length;
          bVal = (b.price_range ?? "").length;
          break;
      }

      if (aVal == null || bVal == null) return 0;
      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [filteredPlaces, sortField, sortDirection]);

  const toggleSort = useCallback(
    (field: SortField) => {
      if (sortField === field) {
        setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
      } else {
        setSortField(field);
        setSortDirection(field === "rating" ? "desc" : "asc");
      }
    },
    [sortField]
  );

  const updateFilter = useCallback(
    <K extends keyof Filters>(key: K, value: Filters[K]) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const toggleArrayFilter = useCallback(
    (key: "cities" | "types" | "priceRanges" | "tags", value: string) => {
      setFilters((prev) => {
        const arr = prev[key];
        return {
          ...prev,
          [key]: arr.includes(value)
            ? arr.filter((v) => v !== value)
            : [...arr, value],
        };
      });
    },
    []
  );

  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
  }, []);

  const hasActiveFilters = useMemo(() => {
    return (
      filters.search !== "" ||
      filters.cities.length > 0 ||
      filters.types.length > 0 ||
      filters.priceRanges.length > 0 ||
      filters.tags.length > 0 ||
      filters.ratingMin > 1 ||
      filters.ratingMax < 10
    );
  }, [filters]);

  return {
    filters,
    sortField,
    sortDirection,
    filteredPlaces,
    sortedPlaces,
    toggleSort,
    updateFilter,
    toggleArrayFilter,
    resetFilters,
    hasActiveFilters,
  };
}
