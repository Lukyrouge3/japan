import { Place, Filters } from "@/types/place";

export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function getUniqueValues(
  places: Place[],
  key: keyof Place
): string[] {
  const values = places
    .map((p) => p[key])
    .filter((v): v is string => typeof v === "string" && v.length > 0);
  return [...new Set(values)].sort();
}

export function getUniqueTags(places: Place[]): string[] {
  const tags = places.flatMap((p) => p.tags ?? []);
  return [...new Set(tags)].sort();
}

export function filterPlaces(places: Place[], filters: Filters): Place[] {
  return places.filter((place) => {
    // Search filter
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const searchable = [
        place.name,
        place.name_fr,
        place.summary,
        place.city,
        place.area,
        place.type,
        ...(place.tags ?? []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      if (!searchable.includes(q)) return false;
    }

    // City filter
    if (filters.cities.length > 0) {
      if (!place.city || !filters.cities.includes(place.city)) return false;
    }

    // Type filter
    if (filters.types.length > 0) {
      if (!filters.types.includes(place.type)) return false;
    }

    // Price range filter
    if (filters.priceRanges.length > 0) {
      if (
        !place.price_range ||
        !filters.priceRanges.includes(place.price_range)
      )
        return false;
    }

    // Tags filter
    if (filters.tags.length > 0) {
      if (
        !place.tags ||
        !filters.tags.some((tag) => place.tags!.includes(tag))
      )
        return false;
    }

    // Rating filter
    if (place.rating != null) {
      if (place.rating < filters.ratingMin || place.rating > filters.ratingMax)
        return false;
    }

    return true;
  });
}

export function getRatingColor(rating: number | null | undefined): string {
  if (rating == null) return "bg-gray-400";
  if (rating >= 9) return "bg-emerald-500";
  if (rating >= 7) return "bg-green-400";
  if (rating >= 5) return "bg-yellow-400";
  if (rating >= 3) return "bg-orange-400";
  return "bg-red-400";
}

export function getRatingTextColor(
  rating: number | null | undefined
): string {
  if (rating == null) return "text-gray-400";
  if (rating >= 9) return "text-emerald-500";
  if (rating >= 7) return "text-green-500";
  if (rating >= 5) return "text-yellow-500";
  if (rating >= 3) return "text-orange-500";
  return "text-red-500";
}

export function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    "Restaurant": "🍜",
    "Café/Salon de thé": "☕",
    "Bar": "🍶",
    "Boulangerie/Pâtisserie": "🥐",
    "Street food": "🍡",
    "Magasin": "🛍️",
    "Centre commercial": "🏬",
    "Supermarché/Konbini": "🏪",
    "Marché": "🧺",
    "Hébergement": "🏨",
    "Temple": "🛕",
    "Sanctuaire": "⛩️",
    "Musée": "🏛️",
    "Monument": "🗿",
    "Site historique": "🏯",
    "Site naturel": "🏔️",
    "Parc/Jardin": "🌳",
    "Onsen/Spa": "♨️",
    "Parc d'attractions": "🎢",
    "Divertissement": "🎮",
    "Attraction": "🎌",
    "Quartier/Rue": "🏘️",
    "Ville/Village": "🏙️",
    "Région": "🗾",
    "Transport": "🚉",
    "Bâtiment": "🏢",
    "Lieu abandonné": "🚧",
    "Service": "ℹ️",
  };
  return icons[type] ?? "📍";
}

export function getPriceRangeLabel(pr: string): string {
  const count = (pr.match(/€/g) || []).length;
  if (count <= 1) return "Budget";
  if (count === 2) return "Moderate";
  if (count === 3) return "Expensive";
  return "Very Expensive";
}
