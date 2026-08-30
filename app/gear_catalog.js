/**
 * CampFind — Amazon Associates Gear Catalog
 * Curated kid-friendly camp essentials by theme & season
 */

const AMAZON_AFFILIATE_TAG = 'campfindgear-20'; // Official Amazon Associates Tracking ID

const GEAR_CATALOG = {
    outdoor: [
        {
            id: 'gear-sunscreen',
            name: 'Kids Mineral Sunscreen SPF 50+ (Water Resistant)',
            category: 'Sun & Skin Protection',
            price: '$12 – $18',
            rating: '4.8 ⭐',
            badge: 'Essential',
            icon: '🧴',
            reason: 'Tear-free mineral zinc protection for long hours of outdoor camp activities.',
            asin: 'B07B9Q67R7',
            searchQuery: 'kids mineral sunscreen spf 50 water resistant'
        },
        {
            id: 'gear-bugspray',
            name: 'DEET-Free Natural Insect & Mosquito Repellent',
            category: 'Safety & Protection',
            price: '$9 – $15',
            rating: '4.7 ⭐',
            badge: 'Parent Pick',
            icon: '🌿',
            reason: 'Plant-based repellent safe for daily camp use against ticks and mosquitoes.',
            asin: 'B004N59OFU',
            searchQuery: 'deet free plant based insect repellent kids'
        },
        {
            id: 'gear-bottle',
            name: 'Insulated Stainless Steel Kids Water Bottle (24 oz)',
            category: 'Hydration',
            price: '$16 – $24',
            rating: '4.9 ⭐',
            badge: 'Top Rated',
            icon: '💧',
            reason: 'Keeps water ice-cold all day with leak-proof straw lid and carrying handle.',
            asin: 'B083XXK2F9',
            searchQuery: 'kids insulated water bottle with straw 24 oz'
        },
        {
            id: 'gear-backpack',
            name: 'Lightweight Waterproof Kids Daypack (15L)',
            category: 'Bags & Storage',
            price: '$18 – $28',
            rating: '4.8 ⭐',
            badge: 'Must Have',
            icon: '🎒',
            reason: 'Ergonomic breathable straps, chest buckle, and water-resistant pockets for camp gear.',
            asin: 'B07D3N2X44',
            searchQuery: 'kids lightweight hiking daypack 15l'
        },
        {
            id: 'gear-watershoes',
            name: 'Quick-Dry Non-Slip Kids Water Shoes',
            category: 'Footwear',
            price: '$14 – $22',
            rating: '4.7 ⭐',
            badge: 'Aquatics',
            icon: '👟',
            reason: 'Protects little feet at lake, pool, and creek exploration with rapid drainage.',
            asin: 'B08F9S8F78',
            searchQuery: 'kids quick dry aqua water shoes non slip'
        }
    ],
    sports: [
        {
            id: 'gear-sports-bottle',
            name: 'Half Gallon Insulated Sports Water Jug (64 oz)',
            category: 'Hydration',
            price: '$19 – $29',
            rating: '4.9 ⭐',
            badge: 'High Endurance',
            icon: '🧊',
            reason: 'Maximum hydration capacity with sturdy handle for full-day athletic camps.',
            asin: 'B08QGKBK8Y',
            searchQuery: 'half gallon insulated sports water jug kids'
        },
        {
            id: 'gear-cooling-towel',
            name: 'Instant Cooling Towels for Athletes (4-Pack)',
            category: 'Cooling & Recovery',
            price: '$12 – $16',
            rating: '4.8 ⭐',
            badge: 'Hot Days',
            icon: '❄️',
            reason: 'Provides hours of refreshing cooling relief during intense summer sports drills.',
            asin: 'B07CV9M7J6',
            searchQuery: 'instant cooling towel for kids sports'
        },
        {
            id: 'gear-shinguards',
            name: 'Kids Breathable Sports Shin Guards & Sleeves',
            category: 'Safety Gear',
            price: '$11 – $17',
            rating: '4.7 ⭐',
            badge: 'Protection',
            icon: '🛡️',
            reason: 'Shock-absorbing lightweight EVA foam for soccer and active team sports.',
            asin: 'B07MVM4W8B',
            searchQuery: 'youth soccer shin guards with calf sleeves'
        },
        {
            id: 'gear-sports-bag',
            name: 'Sports Duffle Bag with Shoe & Ball Compartment',
            category: 'Equipment Bag',
            price: '$22 – $34',
            rating: '4.8 ⭐',
            badge: 'Organizer',
            icon: '⚽',
            reason: 'Separate ventilated compartment keeps muddy cleats and gear organized.',
            asin: 'B0892DMB1B',
            searchQuery: 'youth sports duffle bag with shoe compartment'
        }
    ],
    stem: [
        {
            id: 'gear-bluelight',
            name: 'Kids Anti-Blue Light Protective Glasses',
            category: 'Eye Care',
            price: '$12 – $18',
            rating: '4.8 ⭐',
            badge: 'Screen Time',
            icon: '👓',
            reason: 'Reduces digital eye strain and glare during coding, robotics, and game design sessions.',
            asin: 'B07F2R7C9T',
            searchQuery: 'kids blue light blocking glasses flexible'
        },
        {
            id: 'gear-robotics-kit',
            name: 'STEM Robotics & Coding Starter Project Kit',
            category: 'Hands-on STEM',
            price: '$25 – $45',
            rating: '4.9 ⭐',
            badge: 'Enrichment',
            icon: '🤖',
            reason: 'Continue the learning at home with beginner-friendly modular circuits and robotics.',
            asin: 'B0868F7K6L',
            searchQuery: 'stem robotics coding science kit for kids'
        },
        {
            id: 'gear-tablet-sleeve',
            name: 'Heavy Duty Shockproof Kids Tablet/Laptop Sleeve',
            category: 'Device Protection',
            price: '$15 – $24',
            rating: '4.8 ⭐',
            badge: 'Drop Proof',
            icon: '💻',
            reason: 'Waterproof cushioned EVA protection for laptops/iPads transported to camp daily.',
            asin: 'B08K34P9V8',
            searchQuery: 'kids laptop tablet shockproof padded sleeve'
        }
    ],
    arts: [
        {
            id: 'gear-art-apron',
            name: 'Waterproof Long-Sleeve Kids Art Smock / Apron',
            category: 'Clothing Care',
            price: '$10 – $15',
            rating: '4.7 ⭐',
            badge: 'No Mess',
            icon: '🎨',
            reason: 'Keeps clothes clean from acrylic paints, clay, and glue during messy art projects.',
            asin: 'B07G39X4T9',
            searchQuery: 'kids waterproof art smock long sleeve'
        },
        {
            id: 'gear-art-organizer',
            name: 'Portable Multi-Pocket Art Supply Caddy & Tote',
            category: 'Organization',
            price: '$14 – $22',
            rating: '4.8 ⭐',
            badge: 'Convenient',
            icon: '🖌️',
            reason: 'Quick-access compartments for brushes, markers, scissors, and sketchpads.',
            asin: 'B08H9R7K8L',
            searchQuery: 'kids portable craft art supply organizer caddy'
        }
    ],
    winter: [
        {
            id: 'gear-winter-gloves',
            name: 'Kids Waterproof Thermal 3M Thinsulate Ski Gloves',
            category: 'Cold Weather',
            price: '$16 – $26',
            rating: '4.8 ⭐',
            badge: 'Sub-Zero',
            icon: '🧤',
            reason: 'Super warm windproof and waterproof insulation for snow play, ski & winter camps.',
            asin: 'B07J5M4K8L',
            searchQuery: 'kids waterproof thermal ski snow gloves'
        },
        {
            id: 'gear-snow-goggles',
            name: 'Anti-Fog UV400 Kids Ski & Snowboard Goggles',
            category: 'Eye Protection',
            price: '$18 – $28',
            rating: '4.9 ⭐',
            badge: 'Safety',
            icon: '🥽',
            reason: 'Dual-layer anti-fog lens with 100% UV protection for mountain and winter camps.',
            asin: 'B07593M6G4',
            searchQuery: 'kids ski snowboard goggles anti fog uv400'
        },
        {
            id: 'gear-balaclava',
            name: 'Fleece Windproof Winter Balaclava & Neck Warmer',
            category: 'Thermal Layer',
            price: '$10 – $16',
            rating: '4.7 ⭐',
            badge: 'Cozy',
            icon: '🧣',
            reason: 'All-in-one head, ear, and neck thermal coverage for freezing morning drop-offs.',
            asin: 'B07Z4R7V8M',
            searchQuery: 'kids winter fleece balaclava neck warmer'
        }
    ],
    general: [
        {
            id: 'gear-namelabels',
            name: 'Custom Waterproof Name Labels for Camp Clothes & Gear',
            category: 'Organization',
            price: '$10 – $16',
            rating: '4.9 ⭐',
            badge: 'Camp Essential',
            icon: '🏷️',
            reason: 'Dishwasher & laundry-safe stickers prevent lost water bottles, clothes, and backpacks.',
            asin: 'B07X9Q8K7L',
            searchQuery: 'waterproof personalized name labels for kids camp'
        },
        {
            id: 'gear-firstaid',
            name: 'Compact Travel Kids First Aid Kit (100 Pieces)',
            category: 'Health & Safety',
            price: '$12 – $18',
            rating: '4.8 ⭐',
            badge: 'Peace of Mind',
            icon: '🩹',
            reason: 'Mini emergency kit with kid-friendly bandages, wipes, and sting relief.',
            asin: 'B08F9S8P45',
            searchQuery: 'compact kids mini travel first aid kit'
        }
    ]
};

/**
 * Returns Amazon search/product URL with tracking tag
 */
function getAmazonAffiliateUrl(gearItem) {
    const query = encodeURIComponent(gearItem.searchQuery || gearItem.name);
    return `https://www.amazon.com/s?k=${query}&tag=${AMAZON_AFFILIATE_TAG}`;
}

/**
 * Match recommended gear based on camp properties
 */
function getRecommendedGearForCamp(camp) {
    const theme = (camp.theme || '').toLowerCase();
    const type = (camp.type || '').toLowerCase();
    const season = (camp.season || 'summer').toLowerCase();

    let items = [];

    // 1. Season specific
    if (season === 'winter') {
        items.push(...GEAR_CATALOG.winter);
    }

    // 2. Theme specific
    if (theme.includes('stem') || theme.includes('code') || theme.includes('robot') || theme.includes('science')) {
        items.push(...GEAR_CATALOG.stem);
    } else if (theme.includes('sport') || theme.includes('athletic') || theme.includes('swim') || theme.includes('soccer') || theme.includes('basketball')) {
        items.push(...GEAR_CATALOG.sports);
    } else if (theme.includes('art') || theme.includes('drama') || theme.includes('theater') || theme.includes('music') || theme.includes('dance')) {
        items.push(...GEAR_CATALOG.arts);
    } else {
        items.push(...GEAR_CATALOG.outdoor);
    }

    // 3. Always include top general outdoor & organization essentials
    if (season !== 'winter' && !items.some(i => i.id === 'gear-sunscreen')) {
        items.push(GEAR_CATALOG.outdoor[0]); // Sunscreen
        items.push(GEAR_CATALOG.outdoor[2]); // Water bottle
    }

    items.push(GEAR_CATALOG.general[0]); // Name labels

    // Deduplicate by ID
    const uniqueMap = new Map();
    items.forEach(item => {
        if (!uniqueMap.has(item.id)) {
            uniqueMap.set(item.id, item);
        }
    });

    return Array.from(uniqueMap.values()).slice(0, 5); // Return top 4-5 high-impact items
}

// Export for browser
if (typeof window !== 'undefined') {
    window.GEAR_CATALOG = GEAR_CATALOG;
    window.getAmazonAffiliateUrl = getAmazonAffiliateUrl;
    window.getRecommendedGearForCamp = getRecommendedGearForCamp;
}
