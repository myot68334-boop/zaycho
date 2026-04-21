import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val keystorePropertiesFile = rootProject.file("keystore.properties")
val keystoreProperties = Properties()
if (keystorePropertiesFile.exists()) {
    keystorePropertiesFile.inputStream().use { keystoreProperties.load(it) }
}

android {
    namespace = "com.zaycho.app"
    compileSdk = 35

    defaultConfig {
        applicationId = (project.findProperty("APP_ID") as String?) ?: "com.myot68334.zaycho"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
        resValue("string", "app_name", "Lyra Shop")
        buildConfigField(
            "String",
            "APP_URL",
            "\"${(project.findProperty("APP_URL") as String?) ?: System.getenv("PUBLIC_BASE_URL") ?: "https://example.com"}\""
        )
    }

    signingConfigs {
        create("release") {
            storeFile = file(
                keystoreProperties.getProperty("storeFile")
                    ?: System.getenv("ZAYCHO_KEYSTORE_PATH")
                    ?: "release-keystore.jks"
            )
            storePassword =
                keystoreProperties.getProperty("storePassword") ?: System.getenv("ZAYCHO_KEYSTORE_PASSWORD")
            keyAlias = keystoreProperties.getProperty("keyAlias") ?: System.getenv("ZAYCHO_KEY_ALIAS")
            keyPassword = keystoreProperties.getProperty("keyPassword") ?: System.getenv("ZAYCHO_KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
}
