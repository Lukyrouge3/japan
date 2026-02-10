export interface SourceVideo {
  title: string;
  url: string;
  published_at?: string;
}

export interface Place {
  name: string;
  name_fr?: string;
  type: string;
  address?: string | null;
  city?: string | null;
  area?: string | null;
  rating?: number | null;
  summary: string;
  quotes?: string[];
  price_range?: string | null;
  tags?: string[];
  source_video: SourceVideo;
  additional_sources?: SourceVideo[];
  latitude?: number | null;
  longitude?: number | null;
}

export type SortField = "name" | "type" | "city" | "rating" | "price_range";
export type SortDirection = "asc" | "desc";

export interface Filters {
  search: string;
  cities: string[];
  types: string[];
  priceRanges: string[];
  tags: string[];
  ratingMin: number;
  ratingMax: number;
}
