"use client";

import { Place, SortField, SortDirection } from "@/types/place";
import {
  getTypeIcon,
  getRatingColor,
  cn,
} from "@/lib/utils";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Star,
  ExternalLink,
} from "lucide-react";

interface DataTableProps {
  places: Place[];
  selectedPlace: Place | null;
  onSelectPlace: (place: Place) => void;
  sortField: SortField;
  sortDirection: SortDirection;
  onToggleSort: (field: SortField) => void;
}

function SortIcon({
  field,
  currentField,
  direction,
}: {
  field: SortField;
  currentField: SortField;
  direction: SortDirection;
}) {
  if (field !== currentField)
    return <ArrowUpDown className="w-3.5 h-3.5 text-gray-300" />;
  return direction === "asc" ? (
    <ArrowUp className="w-3.5 h-3.5 text-blue-500" />
  ) : (
    <ArrowDown className="w-3.5 h-3.5 text-blue-500" />
  );
}

export default function DataTable({
  places,
  selectedPlace,
  onSelectPlace,
  sortField,
  sortDirection,
  onToggleSort,
}: DataTableProps) {
  const columns: { key: SortField; label: string; className?: string }[] = [
    { key: "name", label: "Name", className: "min-w-[200px]" },
    { key: "type", label: "Type", className: "w-[120px]" },
    { key: "city", label: "Location", className: "w-[160px]" },
    { key: "rating", label: "Rating", className: "w-[90px]" },
    { key: "price_range", label: "Price", className: "w-[80px]" },
  ];

  return (
    <div className="overflow-auto rounded-xl border border-gray-200 bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50/80">
            {columns.map((col) => (
              <th
                key={col.key}
                className={cn(
                  "text-left px-4 py-3 font-medium text-gray-500 text-xs uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors select-none",
                  col.className
                )}
                onClick={() => onToggleSort(col.key)}
              >
                <div className="flex items-center gap-1.5">
                  {col.label}
                  <SortIcon
                    field={col.key}
                    currentField={sortField}
                    direction={sortDirection}
                  />
                </div>
              </th>
            ))}
            <th className="text-left px-4 py-3 font-medium text-gray-500 text-xs uppercase tracking-wider w-[200px]">
              Summary
            </th>
            <th className="text-left px-4 py-3 font-medium text-gray-500 text-xs uppercase tracking-wider w-[100px]">
              Tags
            </th>
            <th className="text-left px-4 py-3 font-medium text-gray-500 text-xs uppercase tracking-wider w-[60px]">
              Video
            </th>
          </tr>
        </thead>
        <tbody>
          {places.map((place) => {
            const isSelected = selectedPlace?.name === place.name;
            return (
              <tr
                key={`${place.name}-${place.latitude}`}
                onClick={() => onSelectPlace(place)}
                className={cn(
                  "border-b border-gray-50 cursor-pointer transition-colors",
                  isSelected
                    ? "bg-blue-50 hover:bg-blue-50"
                    : "hover:bg-gray-50"
                )}
              >
                {/* Name */}
                <td className="px-4 py-3">
                  <div>
                    <span className="font-medium text-gray-900">
                      {getTypeIcon(place.type)}{" "}
                      {place.name}
                    </span>
                    {place.name_fr && place.name_fr !== place.name && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        {place.name_fr}
                      </p>
                    )}
                  </div>
                </td>

                {/* Type */}
                <td className="px-4 py-3">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 capitalize">
                    {place.type}
                  </span>
                </td>

                {/* Location */}
                <td className="px-4 py-3 text-gray-600">
                  <div className="text-xs">
                    {place.area && (
                      <span className="text-gray-900 font-medium">
                        {place.area}
                      </span>
                    )}
                    {place.area && place.city && (
                      <span className="text-gray-400">, </span>
                    )}
                    {place.city && (
                      <span className="text-gray-500">{place.city}</span>
                    )}
                  </div>
                </td>

                {/* Rating */}
                <td className="px-4 py-3">
                  {place.rating != null && (
                    <div className="flex items-center gap-1.5">
                      <div
                        className={cn(
                          "flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-bold text-white",
                          getRatingColor(place.rating)
                        )}
                      >
                        <Star className="w-3 h-3" />
                        {place.rating}
                      </div>
                    </div>
                  )}
                </td>

                {/* Price */}
                <td className="px-4 py-3 text-gray-600 font-medium text-xs">
                  {place.price_range ?? "—"}
                </td>

                {/* Summary */}
                <td className="px-4 py-3">
                  <p className="text-xs text-gray-500 line-clamp-2 max-w-[200px]">
                    {place.summary}
                  </p>
                </td>

                {/* Tags */}
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1 max-w-[160px]">
                    {(place.tags ?? []).slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-1.5 py-0.5 rounded text-[10px] bg-gray-100 text-gray-500"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>

                {/* Video link */}
                <td className="px-4 py-3">
                  <a
                    href={place.source_video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    onClick={(e) => e.stopPropagation()}
                    title={place.source_video.title}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </td>
              </tr>
            );
          })}
          {places.length === 0 && (
            <tr>
              <td
                colSpan={8}
                className="px-4 py-12 text-center text-gray-400 text-sm"
              >
                No places match your filters. Try adjusting your criteria.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
