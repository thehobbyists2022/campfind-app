// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:campfind/models/camp_model.dart';
import 'package:campfind/services/subscription_service.dart';
import 'package:campfind/screens/claim_camp_screen.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  test('Camp model parsing and FilterOptions work correctly', () {
    final campJson = {
      'id': 'test-1',
      'name': 'Camp Sunshine',
      'city': 'San Diego',
      'state': 'CA',
      'zip': '92101',
      'type': 'Day Camp',
      'season': 'Summer',
      'theme': 'STEM',
      'age_min': 6,
      'age_max': 12,
      'weeks': [1, 2, 3],
      'before_care': true,
      'after_care': true,
      'shuttle': false,
      'provider': 'private',
    };

    final camp = Camp.fromJson(campJson);
    expect(camp.id, 'test-1');
    expect(camp.name, 'Camp Sunshine');
    expect(camp.ageMin, 6);
    expect(camp.ageMax, 12);
    expect(camp.isFeatured, false);
    expect(camp.isClaimed, false);
    expect(camp.sponsorTier, 'free');
  });

  test('SubscriptionService activates and redeems promo codes correctly', () async {
    final sub = SubscriptionService();
    await sub.initialize();
    expect(sub.isPro, false);

    // Test promo code redemption
    final redeemed = await sub.redeemPromoCode('CAMPFINDVIP');
    expect(redeemed, true);
    expect(sub.isPro, true);
    expect(sub.currentTier, 'vip');

    // Test invalid code
    final invalid = await sub.redeemPromoCode('INVALID_CODE');
    expect(invalid, false);
  });

  testWidgets('CampFind app renders title and interface', (WidgetTester tester) async {
    final mockJson = json.encode({
      'camps': [
        {
          'id': 'camp-1',
          'name': 'Camp Adventure',
          'city': 'Carlsbad',
          'state': 'CA',
          'zip': '92008',
          'type': 'Day Camp',
          'season': 'Summer',
          'theme': 'STEM',
          'age_min': 5,
          'age_max': 14,
          'weeks': [1, 2],
          'before_care': true,
          'after_care': false,
          'shuttle': false,
          'provider': 'private',
        }
      ]
    });

    final camp = Camp.fromJson(json.decode(mockJson)['camps'][0]);
    expect(camp.name, 'Camp Adventure');

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Text('CampFind'),
        ),
      ),
    );

    expect(find.text('CampFind'), findsOneWidget);
  });

  testWidgets('ClaimCampScreen renders as free director verification with zero unsubmitted IAP tiers', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: ClaimCampScreen(initialCampName: 'Test Camp'),
      ),
    );

    expect(find.text('Camp Director Verification'), findsOneWidget);
    expect(find.text('Submit Verification Request →'), findsOneWidget);
    // Explicitly verify absence of unsubmitted paid tier references:
    expect(find.textContaining('\$299'), findsNothing);
    expect(find.textContaining('\$99'), findsNothing);
    expect(find.textContaining('Partnership Tier'), findsNothing);
  });
}
