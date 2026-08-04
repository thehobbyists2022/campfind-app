import 'dart:math';

class Camp {
  final String id;
  final String name;
  final String city;
  final String state;
  final String zip;
  final double lat;
  final double lng;
  final String type;
  final double? price;
  final double? rating;
  final int? ageMin;
  final int? ageMax;
  final String season;
  final String theme;
  final bool? beforeCare;
  final bool? afterCare;
  final bool? shuttle;
  final List<int> weeks;
  final String phone;
  final String email;
  final String website;
  final String description;
  final bool acaVerified;
  final bool unverified;
  final String? sourceUrl;
  final String? verificationMethod;

  Camp({
    required this.id,
    required this.name,
    required this.city,
    required this.state,
    required this.zip,
    required this.lat,
    required this.lng,
    required this.type,
    this.price,
    this.rating,
    this.ageMin,
    this.ageMax,
    required this.season,
    required this.theme,
    this.beforeCare,
    this.afterCare,
    this.shuttle,
    required this.weeks,
    required this.phone,
    required this.email,
    required this.website,
    this.description = '',
    this.acaVerified = false,
    this.unverified = true,
    this.sourceUrl,
    this.verificationMethod,
  });

  factory Camp.fromJson(Map<String, dynamic> json) {
    List<int> parsedWeeks = [];
    if (json['weeks'] != null && json['weeks'] is List) {
      parsedWeeks = (json['weeks'] as List).map((e) => (e as num).toInt()).toList();
    }

    return Camp(
      id: json['id']?.toString() ?? json['name']?.toString().toLowerCase().replaceAll(RegExp(r'\s+'), '_') ?? Random().nextInt(100000).toString(),
      name: json['name']?.toString() ?? 'Unnamed Camp',
      city: json['city']?.toString() ?? 'Unknown City',
      state: json['state']?.toString() ?? 'CA',
      zip: json['zip']?.toString() ?? '',
      lat: (json['lat'] as num?)?.toDouble() ?? 33.1959,
      lng: (json['lng'] as num?)?.toDouble() ?? -117.3795,
      type: json['type']?.toString() ?? 'Day Camp',
      price: (json['price'] as num?)?.toDouble(),
      rating: (json['rating'] as num?)?.toDouble(),
      ageMin: (json['ageMin'] as num?)?.toInt() ?? (json['age_min'] as num?)?.toInt(),
      ageMax: (json['ageMax'] as num?)?.toInt() ?? (json['age_max'] as num?)?.toInt(),
      season: json['season']?.toString() ?? 'summer',
      theme: json['theme']?.toString() ?? 'General',
      beforeCare: json['beforeCare'] == true || json['before_care'] == true,
      afterCare: json['afterCare'] == true || json['after_care'] == true,
      shuttle: json['shuttle'] == true,
      weeks: parsedWeeks,
      phone: json['phone']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      website: json['website']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      acaVerified: json['acaVerified'] == true,
      unverified: json['unverified'] != false,
      sourceUrl: json['sourceUrl']?.toString(),
      verificationMethod: json['verificationMethod']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'city': city,
      'state': state,
      'zip': zip,
      'lat': lat,
      'lng': lng,
      'type': type,
      'price': price,
      'rating': rating,
      'ageMin': ageMin,
      'ageMax': ageMax,
      'season': season,
      'theme': theme,
      'beforeCare': beforeCare,
      'afterCare': afterCare,
      'shuttle': shuttle,
      'weeks': weeks,
      'phone': phone,
      'email': email,
      'website': website,
      'description': description,
      'acaVerified': acaVerified,
      'unverified': unverified,
      'sourceUrl': sourceUrl,
      'verificationMethod': verificationMethod,
    };
  }

  /// Distance calculation in Miles from a user's target lat/lng
  double distanceTo(double userLat, double userLng) {
    const p = 0.017453292519943295; // Math.PI / 180
    final a = 0.5 - cos((lat - userLat) * p) / 2 +
        cos(userLat * p) * cos(lat * p) * (1 - cos((lng - userLng) * p)) / 2;
    return 12742 * asin(sqrt(a)) * 0.621371; // 12742 km to miles
  }
}
