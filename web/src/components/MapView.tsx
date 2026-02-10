"use client";

import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { Place } from "@/types/place";
import { getTypeIcon, getRatingColor } from "@/lib/utils";
import "leaflet/dist/leaflet.css";

function createCustomIcon(place: Place): L.DivIcon {
  const emoji = getTypeIcon(place.type);
  return L.divIcon({
    html: `<div class="flex items-center justify-center w-8 h-8 rounded-full bg-white shadow-lg border-2 border-gray-200 text-base leading-none">${emoji}</div>`,
    className: "custom-marker",
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
}

function FitBounds({ places }: { places: Place[] }) {
  const map = useMap();
  const prevPlacesRef = useRef<string>("");

  useEffect(() => {
    const geoPlaces = places.filter(
      (p) => p.latitude != null && p.longitude != null
    );
    if (geoPlaces.length === 0) return;

    const key = geoPlaces.map((p) => `${p.latitude},${p.longitude}`).join("|");
    if (key === prevPlacesRef.current) return;
    prevPlacesRef.current = key;

    const bounds = L.latLngBounds(
      geoPlaces.map((p) => [p.latitude!, p.longitude!])
    );
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
  }, [places, map]);

  return null;
}

interface MapViewProps {
  places: Place[];
  selectedPlace: Place | null;
  onSelectPlace: (place: Place | null) => void;
}

export default function MapView({
  places,
  selectedPlace,
  onSelectPlace,
}: MapViewProps) {
  const geoPlaces = places.filter(
    (p) => p.latitude != null && p.longitude != null
  );

  return (
    <MapContainer
      center={[36.2, 138.2]}
      zoom={6}
      className="h-full w-full rounded-xl"
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
      />
      <FitBounds places={geoPlaces} />
      {geoPlaces.map((place) => (
        <Marker
          key={`${place.name}-${place.latitude}-${place.longitude}`}
          position={[place.latitude!, place.longitude!]}
          icon={createCustomIcon(place)}
          eventHandlers={{
            click: () => onSelectPlace(place),
          }}
        >
          <Popup maxWidth={280} className="custom-popup">
            <div className="p-1">
              <div className="flex items-start justify-between gap-2 mb-1">
                <h3 className="font-bold text-sm text-gray-900 leading-tight">
                  {getTypeIcon(place.type)} {place.name}
                </h3>
                {place.rating != null && (
                  <span
                    className={`inline-flex items-center justify-center min-w-[28px] h-6 px-1.5 rounded-md text-xs font-bold text-white ${getRatingColor(place.rating)}`}
                  >
                    {place.rating}/10
                  </span>
                )}
              </div>
              {place.name_fr && place.name_fr !== place.name && (
                <p className="text-xs text-gray-500 -mt-0.5 mb-1">
                  {place.name_fr}
                </p>
              )}
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-1.5">
                {place.city && <span>{place.city}</span>}
                {place.area && (
                  <>
                    <span>·</span>
                    <span>{place.area}</span>
                  </>
                )}
                {place.price_range && (
                  <>
                    <span>·</span>
                    <span className="font-medium text-gray-600">
                      {place.price_range}
                    </span>
                  </>
                )}
              </div>
              <p className="text-xs text-gray-600 leading-relaxed mb-1.5">
                {place.summary}
              </p>
              {place.tags && place.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {place.tags.slice(0, 4).map((tag) => (
                    <span
                      key={tag}
                      className="px-1.5 py-0.5 rounded text-[10px] bg-gray-100 text-gray-600"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
