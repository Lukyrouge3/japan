"""
Consolidate the 338+ free-form place types into 28 canonical categories.

Usage:
    python consolidate_types.py [input.json] [output.json]

If no arguments are given, reads from ./output/tev_louis_japan.json
and writes to ./output/tev_louis_japan.json (in-place).
"""

import json
import sys
import re
from pathlib import Path

# ── Canonical types ──────────────────────────────────────────────────────────
CANONICAL_TYPES = [
    "Restaurant",
    "Café/Salon de thé",
    "Bar",
    "Boulangerie/Pâtisserie",
    "Street food",
    "Magasin",
    "Centre commercial",
    "Supermarché/Konbini",
    "Marché",
    "Hébergement",
    "Temple",
    "Sanctuaire",
    "Musée",
    "Monument",
    "Site historique",
    "Site naturel",
    "Parc/Jardin",
    "Onsen/Spa",
    "Parc d'attractions",
    "Divertissement",
    "Attraction",
    "Quartier/Rue",
    "Ville/Village",
    "Région",
    "Transport",
    "Bâtiment",
    "Lieu abandonné",
    "Service",
]

# ── Explicit mapping: old type → canonical type ──────────────────────────────
# Keys are lowercased for matching; values are the canonical type.
EXPLICIT_MAP: dict[str, str] = {
    # --- Restaurant ---
    "restaurant": "Restaurant",
    "restaurant (buffet)": "Restaurant",
    "restaurant (burger)": "Restaurant",
    "restaurant (ramen)": "Restaurant",
    "restaurant (buffet de petit-déjeuner)": "Restaurant",
    "restaurant / bar": "Restaurant",
    "restaurant / fast food": "Restaurant",
    "restaurant / food court": "Restaurant",
    "restaurant de sushi": "Restaurant",
    "restaurant fast-food": "Restaurant",
    "restaurant à thème": "Restaurant",
    "local restaurant": "Restaurant",
    "fast food restaurant": "Restaurant",
    "fast food": "Restaurant",
    "fast-food": "Restaurant",
    "aire de repos / restaurant": "Restaurant",
    "aire de service / restauration rapide": "Restaurant",
    "boutique / restaurant": "Restaurant",
    "café à thème / restaurant": "Restaurant",

    # --- Café/Salon de thé ---
    "café": "Café/Salon de thé",
    "café / boutique de desserts": "Café/Salon de thé",
    "café / salon de thé": "Café/Salon de thé",
    "café à chats": "Café/Salon de thé",
    "café à thème": "Café/Salon de thé",
    "café, boulangerie": "Café/Salon de thé",
    "coffee plantation / café": "Café/Salon de thé",

    # --- Bar ---
    "bar / café": "Bar",
    "bar / restaurant": "Bar",
    "bar à hôtesses / cosplay bar": "Bar",
    "bar, lounge": "Bar",
    "bar, restaurant": "Bar",
    "bars / restaurants": "Bar",
    "cave à vin": "Bar",
    "lounge vip": "Bar",

    # --- Boulangerie/Pâtisserie ---
    "boulangerie": "Boulangerie/Pâtisserie",
    "boutique / pâtisserie": "Boulangerie/Pâtisserie",
    "magasin de pâtisserie / comptoir": "Boulangerie/Pâtisserie",
    "pâtisserie / café": "Boulangerie/Pâtisserie",
    "pâtisserie / salon de thé": "Boulangerie/Pâtisserie",
    "pâtisserie, glacier": "Boulangerie/Pâtisserie",
    "pâtisserie": "Boulangerie/Pâtisserie",

    # --- Street food ---
    "centre de street food": "Street food",
    "restaurant / food truck": "Street food",
    "restaurant / street-food": "Street food",
    "street food / stand": "Street food",
    "street food / stand de nourriture": "Street food",
    "street food stand": "Street food",

    # --- Magasin ---
    "magasin": "Magasin",
    "magasin (horlogerie)": "Magasin",
    "magasin (électronique / électroménager)": "Magasin",
    "magasin / armurerie": "Magasin",
    "magasin / attraction": "Magasin",
    "magasin / boutique": "Magasin",
    "magasin / glacier": "Magasin",
    "magasin / musée / boutique de souvenirs": "Magasin",
    "magasin / supérette": "Magasin",
    "magasin d'alimentation / fromagerie": "Magasin",
    "magasin d'alimentation / marché": "Magasin",
    "magasin d'occasion": "Magasin",
    "magasin d'électronique": "Magasin",
    "magasin de cartes": "Magasin",
    "magasin de chocolat / chocolaterie": "Magasin",
    "magasin de chocolat, snack bar": "Magasin",
    "magasin de disques": "Magasin",
    "magasin de gachapon": "Magasin",
    "magasin de jeux vidéo": "Magasin",
    "magasin de jeux vidéo / goodies": "Magasin",
    "magasin de jouets": "Magasin",
    "magasin de jouets / boutique de souvenirs": "Magasin",
    "magasin de jouets/collection": "Magasin",
    "magasin de mangas/jouets d'occasion": "Magasin",
    "magasin de souvenirs": "Magasin",
    "magasin de vêtements": "Magasin",
    "magasin de vêtements / équipement": "Magasin",
    "magasin discount": "Magasin",
    "magasin pour adultes": "Magasin",
    "magasin pour adultes / erotique": "Magasin",
    "magasin spécialisé": "Magasin",
    "magasin, attraction, déco d'intérieur": "Magasin",
    "magasin de collection": "Magasin",
    "magasin de figurines": "Magasin",
    "boutique": "Magasin",
    "boutique / événementiel": "Magasin",
    "papeterie": "Magasin",
    "store": "Magasin",
    "showroom": "Magasin",
    "concessionnaire automobile": "Magasin",
    "chaîne de magasins d'occasion": "Magasin",

    # --- Centre commercial ---
    "centre commercial": "Centre commercial",
    "centre commercial / parc": "Centre commercial",
    "centre commercial, rooftop": "Centre commercial",
    "centre commercial/outlet": "Centre commercial",
    "centre commercial (collection rétro)": "Centre commercial",
    "complexe": "Centre commercial",
    "complexe commercial": "Centre commercial",
    "complexe commercial/gratte-ciel": "Centre commercial",
    "complexe commercial/tour": "Centre commercial",
    "complexe de loisirs et commercial": "Centre commercial",
    "department store": "Centre commercial",
    "grand magasin": "Centre commercial",
    "grand magasin (rayon papeterie)": "Centre commercial",
    "grand magasin / centre commercial": "Centre commercial",
    "grand magasin d'occasion": "Centre commercial",
    "zone commerciale / aire de divertissement": "Centre commercial",
    "aire de repos, complexe commercial, attraction routière": "Centre commercial",
    "immeuble, pont d'observation, centre commercial": "Centre commercial",

    # --- Supermarché/Konbini ---
    "konbini": "Supermarché/Konbini",
    "supermarché": "Supermarché/Konbini",
    "supermarché / épicerie": "Supermarché/Konbini",
    "supermarket": "Supermarché/Konbini",
    "supérette": "Supermarché/Konbini",
    "épicerie / supérette": "Supermarché/Konbini",

    # --- Marché ---
    "marché": "Marché",
    "marché / attraction / aire de repos": "Marché",
    "marché alimentaire": "Marché",
    "marché de plein air": "Marché",
    "market": "Marché",

    # --- Hébergement ---
    "hotel": "Hébergement",
    "hébergement": "Hébergement",
    "hébergement / appartement": "Hébergement",
    "hôtel": "Hébergement",
    "hôtel (capsule hotel)": "Hébergement",
    "hôtel (luxe)": "Hébergement",
    "hôtel / villa": "Hébergement",
    "hôtel/onsen": "Hébergement",
    "maison d'hôtes / hébergement": "Hébergement",
    "espace commun, lounge (faisant partie d'un hôtel)": "Hébergement",

    # --- Temple ---
    "temple": "Temple",
    "temple (complexe)": "Temple",
    "temple / unesco world heritage site": "Temple",
    "temple/statue": "Temple",
    "pagode / monument historique": "Temple",
    "pagode/spot photo": "Temple",

    # --- Sanctuaire ---
    "sanctuaire": "Sanctuaire",
    "sanctuaire, parc": "Sanctuaire",

    # --- Musée ---
    "musée": "Musée",
    "musée / attraction": "Musée",
    "musée, parc à thème": "Musée",
    "musée/expérience sensorielle": "Musée",
    "musée/restaurants": "Musée",
    "exposition / galerie d'art": "Musée",
    "maison historique / musée": "Musée",
    "historical site / museum": "Musée",

    # --- Monument ---
    "monument": "Monument",
    "monument / attraction": "Monument",
    "monument historique": "Monument",
    "monument, temple": "Monument",
    "monument/attraction": "Monument",
    "monument/site religieux": "Monument",
    "mémorial": "Monument",
    "sculpture / point de repère": "Monument",
    "statue, point d'intérêt": "Monument",
    "attraction/statue": "Monument",
    "cathédrale": "Monument",
    "église": "Monument",
    "phare / point d'intérêt": "Monument",
    "pont": "Monument",
    "attraction, tour, monument": "Monument",

    # --- Site historique ---
    "site historique": "Site historique",
    "site historique / villa": "Site historique",
    "site historique/tombeaux": "Site historique",
    "attraction/site historique": "Site historique",
    "bâtiment historique": "Site historique",
    "castle": "Site historique",
    "cemetery": "Site historique",
    "cimetière": "Site historique",
    "ancien hôpital": "Site historique",
    "ancien site minier / point d'intérêt": "Site historique",
    "centre de détention": "Site historique",

    # --- Site naturel ---
    "site naturel": "Site naturel",
    "attraction naturelle": "Site naturel",
    "attraction/site naturel": "Site naturel",
    "nature / attraction": "Site naturel",
    "montagne": "Site naturel",
    "montagne / site sacré": "Site naturel",
    "montagne/site naturel": "Site naturel",
    "forêt": "Site naturel",
    "island": "Site naturel",
    "île": "Site naturel",
    "île / ancien site minier": "Site naturel",
    "île / archipel": "Site naturel",
    "île / attraction naturelle et historique": "Site naturel",
    "île volcanique / site historique": "Site naturel",
    "île, destination touristique": "Site naturel",
    "îles": "Site naturel",
    "lake": "Site naturel",
    "river": "Site naturel",
    "riverside area": "Site naturel",
    "plage": "Site naturel",
    "point d'eau": "Site naturel",
    "point géographique": "Site naturel",
    "colline": "Site naturel",
    "ferme": "Site naturel",
    "volcano / natural attraction": "Site naturel",
    "zone volcanique / parc national / destination onsen": "Site naturel",
    "route de montagne / attraction naturelle": "Site naturel",
    "route panoramique / road trip": "Site naturel",

    # --- Parc/Jardin ---
    "parc": "Parc/Jardin",
    "parc / jardin": "Parc/Jardin",
    "jardin / parc sur le toit": "Parc/Jardin",
    "parc intérieur / jardin": "Parc/Jardin",
    "national park": "Parc/Jardin",
    "jardin (faisant partie d'un hôtel)": "Parc/Jardin",

    # --- Onsen/Spa ---
    "onsen / spa / bain public": "Onsen/Spa",
    "onsen/bain public": "Onsen/Spa",

    # --- Parc d'attractions ---
    "amusement park": "Parc d'attractions",
    "parc d'attraction": "Parc d'attractions",
    "parc d'attraction intérieur": "Parc d'attractions",
    "parc d'attractions": "Parc d'attractions",
    "parc de loisirs": "Parc d'attractions",
    "parc à thème": "Parc d'attractions",
    "aquarium": "Parc d'attractions",
    "zoo": "Parc d'attractions",

    # --- Divertissement ---
    "arcade": "Divertissement",
    "centre d'arcade / game center": "Divertissement",
    "centre de divertissement / karaoké / restaurants à thème (franchise)": "Divertissement",
    "salle d'arcade / centre de jeux": "Divertissement",
    "salle de jeux d'arcade": "Divertissement",
    "cinéma": "Divertissement",
    "arène sportive": "Divertissement",
    "stade, complexe de divertissement": "Divertissement",
    "théâtre traditionnel": "Divertissement",
    "convention / salon": "Divertissement",

    # --- Attraction ---
    "attraction": "Attraction",
    "attraction / activité": "Attraction",
    "attraction / cascade intérieure": "Attraction",
    "attraction / curiosité": "Attraction",
    "attraction / observatoire": "Attraction",
    "attraction / transport touristique": "Attraction",
    "attraction / événement": "Attraction",
    "activité / croisière": "Attraction",
    "activité/attraction": "Attraction",
    "observatoire": "Attraction",
    "observatoire / attraction touristique": "Attraction",
    "point d'observation, point d'intérêt": "Attraction",
    "point de vue / gratte-ciel": "Attraction",
    "tour d'observation/attraction": "Attraction",
    "train à thème / attraction": "Attraction",
    "train à thème / expérience": "Attraction",
    "station de ski / montagne": "Attraction",
    "maison / attraction touristique": "Attraction",

    # --- Quartier/Rue ---
    "quartier": "Quartier/Rue",
    "quartier / complexe commercial et architectural": "Quartier/Rue",
    "quartier / rue commerçante": "Quartier/Rue",
    "quartier / zone d'intérêt": "Quartier/Rue",
    "quartier de prostitution": "Quartier/Rue",
    "quartier en développement": "Quartier/Rue",
    "quartier/rue": "Quartier/Rue",
    "quartier/tour": "Quartier/Rue",
    "quartier/île": "Quartier/Rue",
    "neighborhood": "Quartier/Rue",
    "rue animée / quartier": "Quartier/Rue",
    "rue commerçante": "Quartier/Rue",
    "rue de restaurants / zone de restauration": "Quartier/Rue",
    "rue piétonne commerçante": "Quartier/Rue",
    "rue / quartier": "Quartier/Rue",
    "shopping street": "Quartier/Rue",
    "place publique": "Quartier/Rue",
    "carrefour, point d'intérêt": "Quartier/Rue",
    "zone de restaurants": "Quartier/Rue",

    # --- Ville/Village ---
    "ville": "Ville/Village",
    "ville (city)": "Ville/Village",
    "ville / attraction touristique": "Ville/Village",
    "ville / capitale": "Ville/Village",
    "ville / destination alternative": "Ville/Village",
    "ville / destination culinaire": "Ville/Village",
    "ville / quartier historique": "Ville/Village",
    "ville portuaire": "Ville/Village",
    "ville thermale / ville": "Ville/Village",
    "ville/quartier historique": "Ville/Village",
    "ville/région": "Ville/Village",
    "city": "Ville/Village",
    "village": "Ville/Village",
    "village / port": "Ville/Village",
    "village / rue commerçante": "Ville/Village",
    "village traditionnel": "Ville/Village",

    # --- Région ---
    "préfecture / région": "Région",
    "préfecture/région": "Région",
    "région / province": "Région",
    "district / zone naturelle": "Région",
    "archipel / îles": "Région",

    # --- Transport ---
    "transport": "Transport",
    "gare": "Transport",
    "gare (train station)": "Transport",
    "gare / point de repère": "Transport",
    "gare / station de métro / quartier": "Transport",
    "gare ferroviaire": "Transport",
    "aéroport": "Transport",
    "aéroport / centre commercial": "Transport",
    "arrêt de bus": "Transport",
    "port": "Transport",

    # --- Bâtiment ---
    "building": "Bâtiment",
    "bâtiment commercial": "Bâtiment",
    "bâtiment officiel": "Bâtiment",
    "bâtiment public / point de vue": "Bâtiment",
    "gratte-ciel / bâtiment": "Bâtiment",
    "immeuble commercial": "Bâtiment",
    "immeuble de bureaux": "Bâtiment",
    "centre de recherche": "Bâtiment",
    "institut de recherche / laboratoire": "Bâtiment",
    "mairie, observatoire": "Bâtiment",
    "siège social / showroom privé": "Bâtiment",
    "université": "Bâtiment",

    # --- Lieu abandonné ---
    "bâtiment abandonné / point d'intérêt": "Lieu abandonné",
    "complexe abandonné": "Lieu abandonné",
    "lieu abandonné / musée": "Lieu abandonné",
    "lieu abandonné / station service": "Lieu abandonné",
    "lieu abandonné / urbex": "Lieu abandonné",
    "parc d'attraction abandonné / urbex": "Lieu abandonné",
    "zone sinistrée / lieux abandonnés": "Lieu abandonné",
    "île abandonnée / site historique": "Lieu abandonné",
    "île abandonnée, site minier, site du patrimoine mondial": "Lieu abandonné",
    "île quasi-abandonnée / site minier": "Lieu abandonné",

    # --- Service ---
    "aire de repos/autoroute": "Service",
    "centre d'accueil touristique": "Service",
    "commodité publique": "Service",
    "distributeur automatique": "Service",
    "espace de coworking / bureaux individuels": "Service",
    "garage, centre de réparation automobile": "Service",
    "location de voiture": "Service",
    "office du tourisme": "Service",
    "salon de coiffure": "Service",
    "station-service, magasin de proximité, restauration rapide": "Service",
}


def normalize_type(raw_type: str) -> str:
    """Map a raw type string to its canonical form."""
    key = raw_type.strip().lower()

    # 1. Try explicit map
    if key in EXPLICIT_MAP:
        return EXPLICIT_MAP[key]

    # 2. Keyword-based fallback (order matters: more specific first)
    keyword_rules: list[tuple[list[str], str]] = [
        # Abandoned
        (["abandonné", "urbex", "abandonn"], "Lieu abandonné"),
        # Food & Drink
        (["restaurant", "fast food", "fast-food", "ramen", "sushi", "buffet"], "Restaurant"),
        (["boulangerie", "pâtisserie", "glacier"], "Boulangerie/Pâtisserie"),
        (["street food", "food truck", "stand de nourriture"], "Street food"),
        (["café", "salon de thé", "coffee"], "Café/Salon de thé"),
        (["bar", "lounge", "cave à vin"], "Bar"),
        # Shopping
        (["centre commercial", "complexe commercial", "grand magasin", "department store", "outlet"], "Centre commercial"),
        (["supermarché", "supermarket", "konbini", "supérette", "épicerie"], "Supermarché/Konbini"),
        (["marché", "market"], "Marché"),
        (["magasin", "boutique", "papeterie", "store", "showroom"], "Magasin"),
        # Accommodation
        (["hôtel", "hotel", "hébergement", "maison d'hôtes", "capsule"], "Hébergement"),
        # Religious & Cultural
        (["temple", "pagode"], "Temple"),
        (["sanctuaire", "shrine"], "Sanctuaire"),
        (["musée", "museum", "galerie", "exposition"], "Musée"),
        (["monument", "mémorial", "statue", "sculpture"], "Monument"),
        (["site historique", "castle", "château", "historical"], "Site historique"),
        # Nature
        (["onsen", "spa", "bain public"], "Onsen/Spa"),
        (["parc d'attraction", "parc à thème", "amusement", "zoo", "aquarium"], "Parc d'attractions"),
        (["parc", "jardin", "garden", "national park"], "Parc/Jardin"),
        (["montagne", "volcan", "lac", "rivière", "forêt", "île", "plage", "island", "lake", "river", "volcano", "beach", "naturel"], "Site naturel"),
        # Entertainment
        (["arcade", "jeux", "karaoké", "cinéma", "théâtre", "stade", "divertissement"], "Divertissement"),
        (["attraction", "observatoire", "tour d'observation", "point de vue"], "Attraction"),
        # Urban
        (["quartier", "rue", "neighborhood", "shopping street"], "Quartier/Rue"),
        (["ville", "village", "city"], "Ville/Village"),
        (["préfecture", "région", "province", "archipel", "district"], "Région"),
        # Infrastructure
        (["gare", "aéroport", "transport", "arrêt", "port", "station"], "Transport"),
        (["bâtiment", "immeuble", "building", "gratte-ciel", "tour", "université"], "Bâtiment"),
        # Service
        (["location", "coworking", "office", "service", "garage", "salon de coiffure", "distributeur"], "Service"),
    ]

    for keywords, canonical in keyword_rules:
        for kw in keywords:
            if kw in key:
                return canonical

    # 3. If nothing matched, return as-is (will be flagged in report)
    return raw_type


def consolidate(places: list[dict], verbose: bool = True) -> list[dict]:
    """Remap all place types to canonical categories."""
    unmapped = {}
    type_counts: dict[str, int] = {}

    for place in places:
        old_type = place.get("type", "")
        new_type = normalize_type(old_type)
        place["type"] = new_type

        type_counts[new_type] = type_counts.get(new_type, 0) + 1

        if new_type not in CANONICAL_TYPES:
            unmapped[old_type] = new_type

    if verbose:
        print(f"\n{'='*60}")
        print(f"Type consolidation complete")
        print(f"{'='*60}")
        print(f"Places processed: {len(places)}")
        print(f"Unique types after consolidation: {len(type_counts)}")
        print(f"\nType distribution:")
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t:<30s} {count:>4d}")

        if unmapped:
            print(f"\n⚠ WARNING: {len(unmapped)} types could not be mapped:")
            for old, new in sorted(unmapped.items()):
                print(f"  '{old}' → '{new}'")
        else:
            print(f"\n✓ All types successfully mapped to canonical categories.")

    return places


def main():
    default_path = Path(__file__).parent / "output" / "tev_louis_japan.json"

    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    print(f"Reading from: {input_path}")
    with open(input_path) as f:
        places = json.load(f)

    # Show before stats
    old_types = set(p.get("type", "") for p in places)
    print(f"Types before consolidation: {len(old_types)}")

    places = consolidate(places)

    print(f"\nWriting to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()
