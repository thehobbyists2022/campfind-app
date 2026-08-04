// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:campfind/main.dart';
import 'package:campfind/services/camp_repository.dart';

void main() {
  testWidgets('CampFind app starts with the camp finder', (WidgetTester tester) async {
    final repository = CampRepository();
    await repository.initialize();
    await tester.pumpWidget(CampFindApp(repository: repository));

    expect(find.text('CampFind'), findsOneWidget);
  });
}
