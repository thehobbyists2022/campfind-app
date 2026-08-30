import '../models/camp_model.dart';
import '../models/gear_item.dart';

class GearService {
  static const List<GearItem> outdoorGear = [
    GearItem(
      id: 'gear-sunscreen',
      name: 'Kids Mineral Sunscreen SPF 50+ (Water Resistant)',
      category: 'Sun & Skin Protection',
      price: '\$12 – \$18',
      rating: '4.8 ⭐',
      badge: 'Essential',
      icon: '🧴',
      reason: 'Tear-free mineral zinc protection for long outdoor camp hours.',
      searchQuery: 'kids mineral sunscreen spf 50 water resistant',
    ),
    GearItem(
      id: 'gear-bugspray',
      name: 'DEET-Free Natural Insect & Mosquito Repellent',
      category: 'Safety & Protection',
      price: '\$9 – \$15',
      rating: '4.7 ⭐',
      badge: 'Parent Pick',
      icon: '🌿',
      reason: 'Plant-based repellent safe for daily camp use against ticks and mosquitoes.',
      searchQuery: 'deet free plant based insect repellent kids',
    ),
    GearItem(
      id: 'gear-bottle',
      name: 'Insulated Stainless Steel Kids Water Bottle (24 oz)',
      category: 'Hydration',
      price: '\$16 – \$24',
      rating: '4.9 ⭐',
      badge: 'Top Rated',
      icon: '💧',
      reason: 'Keeps water ice-cold all day with leak-proof straw lid and handle.',
      searchQuery: 'kids insulated water bottle with straw 24 oz',
    ),
    GearItem(
      id: 'gear-backpack',
      name: 'Lightweight Waterproof Kids Daypack (15L)',
      category: 'Bags & Storage',
      price: '\$18 – \$28',
      rating: '4.8 ⭐',
      badge: 'Must Have',
      icon: '🎒',
      reason: 'Ergonomic breathable straps and water-resistant pockets for gear.',
      searchQuery: 'kids lightweight hiking daypack 15l',
    ),
  ];

  static const List<GearItem> sportsGear = [
    GearItem(
      id: 'gear-sports-bottle',
      name: 'Half Gallon Insulated Sports Water Jug (64 oz)',
      category: 'Hydration',
      price: '\$19 – \$29',
      rating: '4.9 ⭐',
      badge: 'High Endurance',
      icon: '🧊',
      reason: 'Maximum hydration capacity with sturdy handle for sports camps.',
      searchQuery: 'half gallon insulated sports water jug kids',
    ),
    GearItem(
      id: 'gear-cooling-towel',
      name: 'Instant Cooling Towels for Athletes (4-Pack)',
      category: 'Cooling & Recovery',
      price: '\$12 – \$16',
      rating: '4.8 ⭐',
      badge: 'Hot Days',
      icon: '❄️',
      reason: 'Refreshing cooling relief during intense summer sports drills.',
      searchQuery: 'instant cooling towel for kids sports',
    ),
    GearItem(
      id: 'gear-shinguards',
      name: 'Kids Breathable Sports Shin Guards & Sleeves',
      category: 'Safety Gear',
      price: '\$11 – \$17',
      rating: '4.7 ⭐',
      badge: 'Protection',
      icon: '🛡️',
      reason: 'Shock-absorbing lightweight EVA foam for active team sports.',
      searchQuery: 'youth soccer shin guards with calf sleeves',
    ),
  ];

  static const List<GearItem> stemGear = [
    GearItem(
      id: 'gear-bluelight',
      name: 'Kids Anti-Blue Light Protective Glasses',
      category: 'Eye Care',
      price: '\$12 – \$18',
      rating: '4.8 ⭐',
      badge: 'Screen Time',
      icon: '👓',
      reason: 'Reduces digital eye strain and glare during coding and robotics.',
      searchQuery: 'kids blue light blocking glasses flexible',
    ),
    GearItem(
      id: 'gear-robotics-kit',
      name: 'STEM Robotics & Coding Starter Project Kit',
      category: 'Hands-on STEM',
      price: '\$25 – \$45',
      rating: '4.9 ⭐',
      badge: 'Enrichment',
      icon: '🤖',
      reason: 'Continue the learning at home with beginner-friendly modular circuits.',
      searchQuery: 'stem robotics coding science kit for kids',
    ),
    GearItem(
      id: 'gear-tablet-sleeve',
      name: 'Heavy Duty Shockproof Kids Tablet/Laptop Sleeve',
      category: 'Device Protection',
      price: '\$15 – \$24',
      rating: '4.8 ⭐',
      badge: 'Drop Proof',
      icon: '💻',
      reason: 'Waterproof cushioned EVA protection for laptops transported daily.',
      searchQuery: 'kids laptop tablet shockproof padded sleeve',
    ),
  ];

  static const List<GearItem> artsGear = [
    GearItem(
      id: 'gear-art-apron',
      name: 'Waterproof Long-Sleeve Kids Art Smock / Apron',
      category: 'Clothing Care',
      price: '\$10 – \$15',
      rating: '4.7 ⭐',
      badge: 'No Mess',
      icon: '🎨',
      reason: 'Keeps clothes clean from acrylic paints and clay in art workshops.',
      searchQuery: 'kids waterproof art smock long sleeve',
    ),
    GearItem(
      id: 'gear-art-organizer',
      name: 'Portable Multi-Pocket Art Supply Caddy & Tote',
      category: 'Organization',
      price: '\$14 – \$22',
      rating: '4.8 ⭐',
      badge: 'Convenient',
      icon: '🖌️',
      reason: 'Quick-access compartments for brushes, markers, and sketchpads.',
      searchQuery: 'kids portable craft art supply organizer caddy',
    ),
  ];

  static const List<GearItem> winterGear = [
    GearItem(
      id: 'gear-winter-gloves',
      name: 'Kids Waterproof Thermal 3M Thinsulate Ski Gloves',
      category: 'Cold Weather',
      price: '\$16 – \$26',
      rating: '4.8 ⭐',
      badge: 'Sub-Zero',
      icon: '🧤',
      reason: 'Windproof and waterproof insulation for snow play & ski camps.',
      searchQuery: 'kids waterproof thermal ski snow gloves',
    ),
    GearItem(
      id: 'gear-snow-goggles',
      name: 'Anti-Fog UV400 Kids Ski & Snowboard Goggles',
      category: 'Eye Protection',
      price: '\$18 – \$28',
      rating: '4.9 ⭐',
      badge: 'Safety',
      icon: '🥽',
      reason: 'Anti-fog lens with 100% UV protection for winter mountain camps.',
      searchQuery: 'kids ski snowboard goggles anti fog uv400',
    ),
  ];

  static const List<GearItem> generalGear = [
    GearItem(
      id: 'gear-namelabels',
      name: 'Custom Waterproof Name Labels for Camp Clothes & Gear',
      category: 'Organization',
      price: '\$10 – \$16',
      rating: '4.9 ⭐',
      badge: 'Camp Essential',
      icon: '🏷️',
      reason: 'Dishwasher & laundry-safe stickers prevent lost items at camp.',
      searchQuery: 'waterproof personalized name labels for kids camp',
    ),
  ];

  static List<GearItem> getRecommendedGear(Camp camp) {
    final theme = camp.theme.toLowerCase();
    final season = camp.season.toLowerCase();

    List<GearItem> items = [];

    if (season == 'winter') {
      items.addAll(winterGear);
    }

    if (theme.contains('stem') || theme.contains('code') || theme.contains('robot') || theme.contains('science')) {
      items.addAll(stemGear);
    } else if (theme.contains('sport') || theme.contains('athletic') || theme.contains('swim') || theme.contains('soccer') || theme.contains('basketball')) {
      items.addAll(sportsGear);
    } else if (theme.contains('art') || theme.contains('drama') || theme.contains('theater') || theme.contains('music')) {
      items.addAll(artsGear);
    } else {
      items.addAll(outdoorGear);
    }

    if (season != 'winter' && !items.any((i) => i.id == 'gear-sunscreen')) {
      items.add(outdoorGear[0]); // Sunscreen
      items.add(outdoorGear[2]); // Bottle
    }

    items.add(generalGear[0]); // Name labels

    // Deduplicate
    final seen = <String>{};
    final unique = <GearItem>[];
    for (final item in items) {
      if (seen.add(item.id)) {
        unique.add(item);
      }
    }

    return unique.take(5).toList();
  }
}
