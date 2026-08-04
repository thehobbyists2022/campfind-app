import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/camp_model.dart';

class FilterOptions {
  String searchQuery;
  int childAge;
  bool isSiblingMode;
  int child2Age;
  String season;
  String campType;
  String theme;
  int sessionWeek;
  bool requireBeforeCare;
  bool requireAfterCare;
  bool requireShuttle;

  FilterOptions({
    this.searchQuery = '',
    this.childAge = 10,
    this.isSiblingMode = false,
    this.child2Age = 6,
    this.season = 'all',
    this.campType = 'all',
    this.theme = 'all',
    this.sessionWeek = 0,
    this.requireBeforeCare = false,
    this.requireAfterCare = false,
    this.requireShuttle = false,
  });
}

class CampRepository {
  List<Camp> _allCamps = [];
  Set<String> _favoriteIds = {};
  bool _isInitialized = false;

  bool get isInitialized => _isInitialized;
  List<Camp> get allCamps => List.unmodifiable(_allCamps);
  Set<String> get favoriteIds => Set.unmodifiable(_favoriteIds);

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      final jsonString = await rootBundle.loadString('assets/aca_camps.json');
      final Map<String, dynamic> data = json.decode(jsonString);
      final List<dynamic> rawList = data['camps'] ?? [];
      
      _allCamps = rawList.map((c) => Camp.fromJson(c)).toList();
      await _loadFavorites();
      _isInitialized = true;
    } catch (e) {
      print('Error loading camp dataset: $e');
      _allCamps = [];
    }
  }

  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    final list = prefs.getStringList('saved_camp_ids') ?? [];
    _favoriteIds = list.toSet();
  }

  Future<void> toggleFavorite(String campId) async {
    if (_favoriteIds.contains(campId)) {
      _favoriteIds.remove(campId);
    } else {
      _favoriteIds.add(campId);
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('saved_camp_ids', _favoriteIds.toList());
  }

  bool isFavorite(String campId) => _favoriteIds.contains(campId);

  List<Camp> filterCamps(FilterOptions options) {
    return _allCamps.where((camp) {
      // 1. Search Query (ZIP / City / State / Name)
      if (options.searchQuery.isNotEmpty) {
        final query = options.searchQuery.trim().toLowerCase();
        final matchesZip = camp.zip.toLowerCase().contains(query);
        final matchesCity = camp.city.toLowerCase().contains(query);
        final matchesState = camp.state.toLowerCase().contains(query);
        final matchesName = camp.name.toLowerCase().contains(query);

        if (!matchesZip && !matchesCity && !matchesState && !matchesName) {
          return false;
        }
      }

      // 2. Child Age Match (null ageMin/ageMax = unknown age, not a filter-out)
      if (camp.ageMin != null && options.childAge < camp.ageMin!) {
        return false;
      }
      if (camp.ageMax != null && options.childAge > camp.ageMax!) {
        return false;
      }

      // 3. Multi-Child / Sibling Mode Match
      if (options.isSiblingMode) {
        if (camp.ageMin != null && options.child2Age < camp.ageMin!) {
          return false;
        }
        if (camp.ageMax != null && options.child2Age > camp.ageMax!) {
          return false;
        }
      }

      // 4. Season Filter
      if (options.season != 'all' && camp.season.toLowerCase() != options.season.toLowerCase()) {
        return false;
      }

      // 5. Camp Type Filter
      if (options.campType != 'all') {
        final typeLower = camp.type.toLowerCase();
        final target = options.campType.toLowerCase();
        if (target == 'day' && !typeLower.contains('day')) return false;
        if (target == 'overnight' && !typeLower.contains('overnight')) return false;
        if (target == 'both' && !typeLower.contains('both')) return false;
      }

      // 6. Theme & Focus Filter
      if (options.theme != 'all' && camp.theme.toLowerCase() != options.theme.toLowerCase()) {
        return false;
      }

      // 7. Session Week Picker
      if (options.sessionWeek > 0 && !camp.weeks.contains(options.sessionWeek)) {
        return false;
      }

      // 8. Logistics & Extended Care (null = unknown, not a filter-out)
      if (options.requireBeforeCare && camp.beforeCare != true) return false;
      if (options.requireAfterCare && camp.afterCare != true) return false;
      if (options.requireShuttle && camp.shuttle != true) return false;

      return true;
    }).toList();
  }
}
