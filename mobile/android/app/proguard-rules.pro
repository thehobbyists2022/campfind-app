# Flutter Wrapper
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# Dart JNI & Engine bindings
-keep class * extends io.flutter.embedding.engine.plugins.FlutterPlugin { *; }
-keep class * extends io.flutter.embedding.engine.plugins.activity.ActivityAware { *; }

# Keep URL Launcher & Shared Preferences
-keep class io.flutter.plugins.urllauncher.** { *; }
-keep class io.flutter.plugins.sharedpreferences.** { *; }

# Keep main activity
-keep class com.campfind.app.MainActivity { *; }

# Ignore missing optional Play Core classes used by Flutter deferred components
-dontwarn com.google.android.play.core.**

# Preserve line numbers for crash reporting
-keepattributes LineNumberTable,SourceFile
