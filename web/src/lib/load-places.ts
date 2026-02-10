import { Place } from "@/types/place";
import { samplePlaces } from "@/data/sample-places";
import * as fs from "fs";
import * as path from "path";

/**
 * Attempts to load places from the scraper's JSON output file.
 * Falls back to sample data if the file doesn't exist.
 *
 * The scraper outputs to: ../scrapper/tev_louis_japan.json
 * (relative to the web/ directory)
 */
export function loadPlaces(): Place[] {
  const possiblePaths = [
    path.join(process.cwd(), "..", "scrapper", "tev_louis_japan.json"),
    path.join(process.cwd(), "..", "scrapper", "output", "tev_louis_japan.json"),
    path.join(process.cwd(), "data", "places.json"),
  ];

  for (const filePath of possiblePaths) {
    try {
      if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath, "utf-8");
        const data = JSON.parse(raw);

        // The scraper output may be an array directly or have a `places` key
        const places: Place[] = Array.isArray(data) ? data : data.places ?? [];

        // Filter to only places with valid coordinates
        const validPlaces = places.filter(
          (p) =>
            p.name &&
            p.type &&
            p.summary &&
            p.source_video
        );

        if (validPlaces.length > 0) {
          console.log(
            `Loaded ${validPlaces.length} places from ${filePath}`
          );
          return validPlaces;
        }
      }
    } catch {
      // Continue to next path
    }
  }

  console.log("No scraper data found, using sample data");
  return samplePlaces;
}
