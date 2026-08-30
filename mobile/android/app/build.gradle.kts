import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// Load release signing config from key.properties (never committed to git).
// Falls back to built-in no-signing behavior when the file is absent so that
// debug/local builds keep working; release builds require a real keystore.
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
val loadKeystore = keystorePropertiesFile.exists()
if (loadKeystore) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    namespace = "com.campfind.campfind"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        // Match the app id used on Google Play (com.campfind.app).
        applicationId = "com.campfind.app"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = 19
        versionName = "1.1.0"
    }

    signingConfigs {
        create("release") {
            if (loadKeystore) {
                storeFile = file(keystoreProperties.getProperty("storeFile"))
                storePassword = keystoreProperties.getProperty("storePassword")
                keyAlias = keystoreProperties.getProperty("keyAlias")
                keyPassword = keystoreProperties.getProperty("keyPassword")
            } else {
                // key.properties missing: leave the signing config unset so
                // release builds fail with a clear message rather than using a
                // hardcoded/weak credential from source.
            }
        }
    }

    buildTypes {
        release {
            signingConfig = if (loadKeystore) {
                signingConfigs.getByName("release")
            } else {
                // Build without signing when no keystore is configured.
                null
            }
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
