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
  Completer<bool>? _pendingPurchaseCompleter;

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

  Future<void> _onPurchaseUpdate(List<PurchaseDetails> purchaseDetailsList) async {
    for (final purchase in purchaseDetailsList) {
      if (purchase.status == PurchaseStatus.pending) {
        // Transaction pending in store sheet
      } else if (purchase.status == PurchaseStatus.error) {
        if (kDebugMode) {
          debugPrint('IAP Error: ${purchase.error?.message}');
        }
        if (purchase.pendingCompletePurchase) {
          await _iap.completePurchase(purchase);
        }
        if (_pendingPurchaseCompleter != null && !_pendingPurchaseCompleter!.isCompleted) {
          _pendingPurchaseCompleter!.complete(false);
        }
      } else if (purchase.status == PurchaseStatus.canceled) {
        if (purchase.pendingCompletePurchase) {
          await _iap.completePurchase(purchase);
        }
        if (_pendingPurchaseCompleter != null && !_pendingPurchaseCompleter!.isCompleted) {
          _pendingPurchaseCompleter!.complete(false);
        }
      } else if (purchase.status == PurchaseStatus.purchased || purchase.status == PurchaseStatus.restored) {
        final tier = purchase.productID == kMonthlySubscriptionId ? 'monthly' : 'yearly';
        final days = tier == 'monthly' ? 30 : 365;
        await activateSubscription(tier: tier, days: days);

        if (purchase.pendingCompletePurchase) {
          await _iap.completePurchase(purchase);
        }
        if (_pendingPurchaseCompleter != null && !_pendingPurchaseCompleter!.isCompleted) {
          _pendingPurchaseCompleter!.complete(true);
        }
      }
    }
  }

  /// Purchase native subscription by Product ID.
  /// Strictly requires a valid StoreKit / Google Play Billing session and waits
  /// for the asynchronous purchaseStream result (with a 30s bounded timeout).
  /// Never grants free Pro access when offline or on error.
  Future<bool> buyNativeSubscription(String productId) async {
    if (!_isStoreAvailable || _products.isEmpty) {
      await _loadStoreProducts();
      if (!_isStoreAvailable || _products.isEmpty) {
        return false;
      }
    }

    try {
      final product = _products.firstWhere((p) => p.id == productId);
      final purchaseParam = PurchaseParam(productDetails: product);
      _pendingPurchaseCompleter = Completer<bool>();

      final launched = await _iap.buyNonConsumable(purchaseParam: purchaseParam);
      if (!launched) {
        _pendingPurchaseCompleter = null;
        return false;
      }

      final completed = await _pendingPurchaseCompleter!.future.timeout(
        const Duration(seconds: 30),
        onTimeout: () => _isPro,
      );
      _pendingPurchaseCompleter = null;
      return completed && _isPro;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Purchase execution error: $e');
      }
      _pendingPurchaseCompleter = null;
      return false;
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
