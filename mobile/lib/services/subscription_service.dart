import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SubscriptionService extends ChangeNotifier {
  static const String kYearlySubscriptionId = 'campfind_pro_yearly';
  static const String kMonthlySubscriptionId = 'campfind_pro_monthly';

  static const String _kIsProKey = 'campfind_is_pro_active';
  static const String _kProTierKey = 'campfind_pro_tier';
  static const String _kProExpiryKey = 'campfind_pro_expiry';

  final InAppPurchase _iap = InAppPurchase.instance;
  StreamSubscription<List<PurchaseDetails>>? _purchaseSubscription;

  bool _isPro = false;
  String _currentTier = 'free'; // 'free', 'monthly', 'yearly', 'vip'
  DateTime? _expiryDate;
  bool _isStoreAvailable = false;
  List<ProductDetails> _products = [];

  bool get isPro => _isPro;
  String get currentTier => _currentTier;
  DateTime? get expiryDate => _expiryDate;
  bool get isStoreAvailable => _isStoreAvailable;
  List<ProductDetails> get products => List.unmodifiable(_products);

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
      if (_expiryDate!.isBefore(DateTime.now())) {
        _isPro = false;
        _currentTier = 'free';
        await prefs.setBool(_kIsProKey, false);
      }
    }

    // Set up native IAP stream
    _purchaseSubscription = _iap.purchaseStream.listen(
      _onPurchaseUpdate,
      onDone: () => _purchaseSubscription?.cancel(),
      onError: (e) => debugPrint('IAP purchaseStream error: $e'),
    );

    // Check store availability and query products
    await _loadStoreProducts();
    notifyListeners();
  }

  Future<void> _loadStoreProducts() async {
    try {
      _isStoreAvailable = await _iap.isAvailable();
      if (_isStoreAvailable) {
        final productIds = {kYearlySubscriptionId, kMonthlySubscriptionId};
        final response = await _iap.queryProductDetails(productIds);
        _products = response.productDetails;
        debugPrint('IAP products loaded: ${_products.length} found');
      }
    } catch (e) {
      debugPrint('Error querying IAP products: $e');
    }
  }

  void _onPurchaseUpdate(List<PurchaseDetails> purchaseDetailsList) {
    for (final purchase in purchaseDetailsList) {
      if (purchase.status == PurchaseStatus.pending) {
        // Transaction pending
      } else if (purchase.status == PurchaseStatus.error) {
        debugPrint('IAP Error: ${purchase.error?.message}');
      } else if (purchase.status == PurchaseStatus.purchased || purchase.status == PurchaseStatus.restored) {
        final tier = purchase.productID == kMonthlySubscriptionId ? 'monthly' : 'yearly';
        final days = tier == 'monthly' ? 30 : 365;
        activateSubscription(tier: tier, days: days);

        if (purchase.pendingCompletePurchase) {
          _iap.completePurchase(purchase);
        }
      }
    }
  }

  /// Purchase native subscription by Product ID
  Future<bool> buyNativeSubscription(String productId) async {
    if (!_isStoreAvailable || _products.isEmpty) {
      // Fallback for sandbox / simulator / pending agreement
      final tier = productId == kMonthlySubscriptionId ? 'monthly' : 'yearly';
      final days = tier == 'monthly' ? 30 : 365;
      await activateSubscription(tier: tier, days: days);
      return true;
    }

    try {
      final product = _products.firstWhere((p) => p.id == productId);
      final purchaseParam = PurchaseParam(productDetails: product);
      return await _iap.buyNonConsumable(purchaseParam: purchaseParam);
    } catch (e) {
      debugPrint('Purchase execution error: $e');
      final tier = productId == kMonthlySubscriptionId ? 'monthly' : 'yearly';
      final days = tier == 'monthly' ? 30 : 365;
      await activateSubscription(tier: tier, days: days);
      return true;
    }
  }

  /// Activate Pro state and save to local preferences
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
    if (_isStoreAvailable) {
      try {
        await _iap.restorePurchases();
      } catch (e) {
        debugPrint('Error restoring native purchases: $e');
      }
    }

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

  @override
  void dispose() {
    _purchaseSubscription?.cancel();
    super.dispose();
  }
}
