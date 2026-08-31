import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'services/camp_repository.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  final repository = CampRepository();
  await repository.initialize();

  runApp(CampFindApp(repository: repository));
}

class CampFindApp extends StatefulWidget {
  final CampRepository repository;

  const CampFindApp({super.key, required this.repository});

  @override
  State<CampFindApp> createState() => _CampFindAppState();
}

class _CampFindAppState extends State<CampFindApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused || state == AppLifecycleState.hidden) {
      // Clear image cache when the app goes into the background
      PaintingBinding.instance.imageCache.clear();
      PaintingBinding.instance.imageCache.clearLiveImages();
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CampFind — Summer & Winter Camp Finder',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFFF6B6B),
          primary: const Color(0xFFFF6B6B),
          secondary: const Color(0xFF4ECDC4),
          surface: Colors.white,
        ),
        textTheme: GoogleFonts.interTextTheme(
          Theme.of(context).textTheme,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          elevation: 0,
          scrolledUnderElevation: 0.5,
        ),
      ),
      home: HomeScreen(repository: widget.repository),
    );
  }
}
