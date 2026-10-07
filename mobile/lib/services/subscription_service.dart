import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SubscriptionService extends ChangeNotifier {
  static const String _kIsProKey = 'campfind_is_pro_active';
  static const String _kProTierKey = 'campfind_pro_tier';
  static const String _kProExpiryKey = 'campfind_pro_expiry';

  bool _isPro = false;
  String _currentTier = 'free'; // 'free', 'monthly', 'yearly', 'vip'
  DateTime? _expiryDate;

  bool get isPro => _isPro;
  String get currentTier => _currentTier;
  DateTime? get expiryDate => _expiryDate;

  static final SubscriptionService _instance = SubscriptionService._internal();
  factory SubscriptionService() => _instance;
  SubscriptionService._internal();

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _isPro = prefs.getBool(_kIsProKey) ?? false;
    _currentTier = prefs.getString(_kProTierKey) ?? 'free';
    final expiryMillis = prefs.getInt(_kProExpiryKey);
    if (expiryMillis != null) {
      _expiryDate = DateTime.fromMillisecondsSinceEpoch(expiryMillis);
      // Check if expired
      if (_expiryDate!.isBefore(DateTime.now())) {
        _isPro = false;
        _currentTier = 'free';
        await prefs.setBool(_kIsProKey, false);
      }
    }
    notifyListeners();
  }

  /// Activate Pro via mock subscription / testing / web Stripe
  Future<void> activateSubscription({required String tier, int days = 365}) async {
    final prefs = await SharedPreferences.getInstance();
    _isPro = true;
    _currentTier = tier;
    _expiryDate = DateTime.now().add(Duration(days: days));

    await prefs.setBool(_kIsProKey, true);
    await prefs.setString(_kProTierKey, tier);
    await prefs.setInt(_kProExpiryKey, _expiryDate!.millisecondsSinceEpoch);

    notifyListeners();
  }

  /// Redeem promotional or VIP code
  Future<bool> redeemPromoCode(String code) async {
    final cleanCode = code.trim().toUpperCase();
    final validCodes = {
      'CAMPFINDVIP': 365,
      'SUMMER2026': 180,
      'EARLYBIRD': 90,
      'JEVPRO': 365,
    };

    if (validCodes.containsKey(cleanCode)) {
      final days = validCodes[cleanCode]!;
      await activateSubscription(tier: 'vip', days: days);
      return true;
    }
    return false;
  }

  /// Restore purchases
  Future<bool> restorePurchases() async {
    final prefs = await SharedPreferences.getInstance();
    final storedPro = prefs.getBool(_kIsProKey) ?? false;
    if (storedPro) {
      _isPro = true;
      _currentTier = prefs.getString(_kProTierKey) ?? 'yearly';
      notifyListeners();
      return true;
    }
    return false;
  }
}
