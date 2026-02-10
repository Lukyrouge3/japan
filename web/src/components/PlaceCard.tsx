"use client";

import { Place } from "@/types/place";
import {
  cn,
  getTypeIcon,
  getRatingColor,
  getRatingTextColor,
} from "@/lib/utils";
import {
  MapPin,
  Star,
  ExternalLink,
  Quote,
  Youtube,
} from "lucide-react";

interface PlaceCardProps {
  place: Place;
  isSelected: boolean;
  onSelect: (place: Place) => void;
}

export default function PlaceCard({
  place,
  isSelected,
  onSelect,
}: PlaceCardProps) {
  return (
    <div
      onClick={() => onSelect(place)}
      className={cn(
        "group relative p-4 rounded-xl border cursor-pointer transition-all duration-200",
        "hover:shadow-md hover:border-gray-300",
        isSelected
          ? "border-blue-400 bg-blue-50/50 shadow-md ring-1 ring-blue-200"
          : "border-gray-200 bg-white"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight truncate">
            <span className="mr-1.5">{getTypeIcon(place.type)}</span>
            {place.name}
          </h3>
          {place.name_fr && place.name_fr !== place.name && (
            <p className="text-xs text-gray-400 mt-0.5 truncate">
              {place.name_fr}
            </p>
          )}
        </div>
        {place.rating != null && (
          <div
            className={cn(
              "flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-bold text-white shrink-0",
              getRatingColor(place.rating)
            )}
          >
            <Star className="w-3 h-3" />
            {place.rating}
          </div>
        )}
      </div>

      {/* Location & Price */}
      <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
        <MapPin className="w-3 h-3 shrink-0" />
        <span className="truncate">
          {[place.area, place.city].filter(Boolean).join(", ")}
        </span>
        {place.price_range && (
          <>
            <span className="text-gray-300 mx-0.5">·</span>
            <span className="font-medium text-gray-600 shrink-0">
              {place.price_range}
            </span>
          </>
        )}
      </div>

      {/* Summary */}
      <p className="text-xs text-gray-600 leading-relaxed mb-2 line-clamp-2">
        {place.summary}
      </p>

      {/* Quote */}
      {place.quotes && place.quotes[0] && (
        <div className="flex items-start gap-1.5 mb-2 px-2 py-1.5 bg-gray-50 rounded-lg">
          <Quote className="w-3 h-3 text-gray-300 shrink-0 mt-0.5" />
          <p className="text-[11px] text-gray-500 italic line-clamp-1">
            &ldquo;{place.quotes[0]}&rdquo;
          </p>
        </div>
      )}

      {/* Tags */}
      {place.tags && place.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {place.tags.slice(0, 5).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-500"
            >
              {tag}
            </span>
          ))}
          {place.tags.length > 5 && (
            <span className="px-2 py-0.5 rounded-full text-[10px] text-gray-400">
              +{place.tags.length - 5}
            </span>
          )}
        </div>
      )}

      {/* Source */}
      <div className="flex items-center gap-1.5 pt-2 border-t border-gray-100">
        <Youtube className="w-3 h-3 text-red-500 shrink-0" />
        <a
          href={place.source_video.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[11px] text-gray-400 hover:text-blue-500 truncate transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          {place.source_video.title}
          <ExternalLink className="w-2.5 h-2.5 inline ml-1" />
        </a>
      </div>
    </div>
  );
}
