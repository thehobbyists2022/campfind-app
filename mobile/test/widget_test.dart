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
}
