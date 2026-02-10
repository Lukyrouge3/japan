import Dashboard from "@/components/Dashboard";
import StatsBar from "@/components/StatsBar";
import { loadPlaces } from "@/lib/load-places";
import { MapPin } from "lucide-react";

export default function Home() {
  const places = loadPlaces();

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-red-50 text-red-500 p-2 rounded-xl">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 leading-tight">
                Japan Explorer
              </h1>
              <p className="text-xs text-gray-400">
                Places from Tev &amp; Louis videos
              </p>
            </div>
          </div>
          <div className="hidden md:block">
            <StatsBar places={places} />
          </div>
        </div>
      </header>

      {/* Mobile Stats */}
      <div className="md:hidden px-4 py-3 bg-white border-b border-gray-100">
        <StatsBar places={places} />
      </div>

      {/* Dashboard */}
      <Dashboard places={places} />
    </main>
  );
}
