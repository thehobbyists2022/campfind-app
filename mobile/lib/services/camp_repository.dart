import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/camp_model.dart';

const String kCampsDataVersionKey = 'camps_data_version';
const String kDefaultBundledVersion = '2026.10.04-v1';
const String kRemoteVersionUrl = 'https://campfind.netlify.app/app/version.json';
const String kFallbackVersionUrl = 'https://raw.githubusercontent.com/thehobbyists2022/campfind-app/main/app/version.json';

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
  bool cityOnly;

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
    this.cityOnly = false,
  });
}

class CampRepository extends ChangeNotifier {
  List<Camp> _allCamps = [];
  Set<String> _favoriteIds = {};
  bool _isInitialized = false;
  String _currentVersion = kDefaultBundledVersion;

  bool get isInitialized => _isInitialized;
  List<Camp> get allCamps => List.unmodifiable(_allCamps);
  Set<String> get favoriteIds => Set.unmodifiable(_favoriteIds);
  String get currentVersion => _currentVersion;

  Future<void> initialize() async {
    if (_isInitialized) return;

    File? cacheFile;
    try {
      final docDir = await getApplicationDocumentsDirectory();
      cacheFile = File('${docDir.path}/camps_cache.json');

      String jsonString;
      if (await cacheFile.exists()) {
        jsonString = await cacheFile.readAsString();
      } else {
        jsonString = await rootBundle.loadString('assets/aca_camps.json');
      }

      // Run heavy JSON decoding and mapping in a background isolate (Flutter compute)
      _allCamps = await compute(_parseCampsJson, jsonString);

      final prefs = await SharedPreferences.getInstance();
      _currentVersion = prefs.getString(kCampsDataVersionKey) ?? kDefaultBundledVersion;

      await _loadFavorites();
      _isInitialized = true;
      notifyListeners();
    } catch (e) {
      try {
        final fallbackJson = await rootBundle.loadString('assets/aca_camps.json');
        _allCamps = await compute(_parseCampsJson, fallbackJson);
        await _loadFavorites();
        _isInitialized = true;
      } catch (innerError) {
        // ignore: avoid_print
        print('Error loading camp dataset: $innerError');
        _allCamps = [];
      }
    }

    // Trigger non-blocking silent background OTA sync
    if (cacheFile != null) {
      _silentBackgroundSync(cacheFile);
    }
  }

  Future<void> _silentBackgroundSync(File cacheFile) async {
    try {
      final client = HttpClient()..connectionTimeout = const Duration(seconds: 6);

      Map<String, dynamic>? meta = await _fetchJson(client, kRemoteVersionUrl);
      meta ??= await _fetchJson(client, kFallbackVersionUrl);

      if (meta == null) {
        client.close();
        return;
      }

      final remoteVersion = meta['version']?.toString() ?? '';
      final downloadUrl = meta['download_url']?.toString() ?? meta['fallback_url']?.toString() ?? '';

      final prefs = await SharedPreferences.getInstance();
      final localVersion = prefs.getString(kCampsDataVersionKey) ?? kDefaultBundledVersion;

      if (remoteVersion.isNotEmpty && remoteVersion != localVersion && downloadUrl.isNotEmpty) {
        final newJsonString = await _fetchString(client, downloadUrl);
        if (newJsonString != null && newJsonString.length > 50000) {
          final updatedCamps = await compute(_parseCampsJson, newJsonString);
          if (updatedCamps.isNotEmpty) {
            await cacheFile.writeAsString(newJsonString);
            await prefs.setString(kCampsDataVersionKey, remoteVersion);
            _currentVersion = remoteVersion;
            _allCamps = updatedCamps;
            notifyListeners();
          }
        }
      }
      client.close();
    } catch (_) {
      // Silent error: offline or network issue never affects user experience
    }
  }

  static Future<Map<String, dynamic>?> _fetchJson(HttpClient client, String url) async {
    try {
      final req = await client.getUrl(Uri.parse(url));
      final res = await req.close();
      if (res.statusCode == 200) {
        final body = await res.transform(utf8.decoder).join();
        return json.decode(body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  static Future<String?> _fetchString(HttpClient client, String url) async {
    try {
      final req = await client.getUrl(Uri.parse(url));
      final res = await req.close();
      if (res.statusCode == 200) {
        return await res.transform(utf8.decoder).join();
      }
    } catch (_) {}
    return null;
  }


  // Top-level or static function required for isolate execution
  static List<Camp> _parseCampsJson(String jsonString) {
    final Map<String, dynamic> data = json.decode(jsonString);
    final List<dynamic> rawList = data['camps'] ?? [];
    return rawList.map((c) => Camp.fromJson(c)).toList();
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
      if (options.theme != 'all' && options.theme != 'city' &&
          camp.theme.toLowerCase() != options.theme.toLowerCase()) {
        return false;
      }

      // 6b. City-Run provider filter
      if (options.cityOnly && camp.provider.toLowerCase() != 'city') {
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
