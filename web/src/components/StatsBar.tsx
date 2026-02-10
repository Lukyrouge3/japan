"use client";

import { useMemo } from "react";
import { Place } from "@/types/place";
import { getTypeIcon } from "@/lib/utils";
import { MapPin, Star, Utensils, Map } from "lucide-react";

interface StatsBarProps {
  places: Place[];
}

export default function StatsBar({ places }: StatsBarProps) {
  const stats = useMemo(() => {
    const cities = new Set(places.map((p) => p.city).filter(Boolean));
    const avgRating =
      places.filter((p) => p.rating != null).reduce((sum, p) => sum + p.rating!, 0) /
        places.filter((p) => p.rating != null).length || 0;
    const topRated = places.filter((p) => p.rating != null && p.rating >= 9).length;
    const types = places.reduce(
      (acc, p) => {
        acc[p.type] = (acc[p.type] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>
    );
    const topType = Object.entries(types).sort((a, b) => b[1] - a[1])[0];

    return { cities: cities.size, avgRating, topRated, topType };
  }, [places]);

  const items = [
    {
      icon: <MapPin className="w-4 h-4" />,
      label: "Places",
      value: places.length,
      color: "text-blue-500",
      bg: "bg-blue-50",
    },
    {
      icon: <Map className="w-4 h-4" />,
      label: "Cities",
      value: stats.cities,
      color: "text-purple-500",
      bg: "bg-purple-50",
    },
    {
      icon: <Star className="w-4 h-4" />,
      label: "Avg Rating",
      value: stats.avgRating.toFixed(1),
      color: "text-amber-500",
      bg: "bg-amber-50",
    },
    {
      icon: <Utensils className="w-4 h-4" />,
      label: stats.topType ? stats.topType[0] : "—",
      value: stats.topType ? `${stats.topType[1]}` : "0",
      color: "text-emerald-500",
      bg: "bg-emerald-50",
      emoji: stats.topType ? getTypeIcon(stats.topType[0]) : undefined,
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {items.map((item) => (
        <div
          key={item.label}
          className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white border border-gray-100"
        >
          <div
            className={`${item.bg} ${item.color} p-2 rounded-lg`}
          >
            {item.emoji ? (
              <span className="text-base">{item.emoji}</span>
            ) : (
              item.icon
            )}
          </div>
          <div>
            <p className="text-lg font-bold text-gray-900">{item.value}</p>
            <p className="text-xs text-gray-400 capitalize">{item.label}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
