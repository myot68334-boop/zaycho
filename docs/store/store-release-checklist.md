# ZayCho Store Release Checklist

This project is prepared up to the point where the remaining steps are mostly account, signing, and store-metadata work.

## Apple App Store

- Build and archive the iOS app from [`mobile/ios`](/Users/myothant/Documents/New%20project/mobile/ios).
- Use a paid Apple Developer account.
- Create the App Store Connect app record, bundle identifier, signing certificate, and provisioning profile.
- Upload an iOS build through Xcode Organizer or Transporter.
- Prepare the App Store product page:
  - app name
  - subtitle
  - description
  - privacy information
  - age rating
  - support URL
  - marketing URL if available
  - screenshots
  - app icon in the Xcode asset catalog
- Keep backend services live during review.
- Provide demo credentials in review notes if login is required in a future version.

Official references:

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Apple screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications
- Apple app icon guidance: https://developer.apple.com/help/app-store-connect/manage-app-information/add-an-app-icon/

## Google Play Store

- Open the Android project from [`mobile/android`](/Users/myothant/Documents/New%20project/mobile/android) in Android Studio.
- Install Android SDK and create a signed app bundle (`.aab`).
- Use a Google Play Console account.
- Create the app record and upload the signed bundle.
- Complete the Play listing:
  - app name
  - short description
  - full description
  - privacy policy URL
  - app icon
  - feature graphic
  - screenshots
  - content rating
  - data safety
  - testing track setup
- Ensure the target SDK stays current before release.

Official references:

- Google Play target API requirements: https://developer.android.com/google/play/requirements/target-sdk
- Google Play app setup: https://support.google.com/googleplay/android-developer/answer/9859152
- Google Play preview assets: https://support.google.com/googleplay/android-developer/answer/1078870

## Assets in this repo

- Play icon base: [`docs/store/play-store-icon-512.png`](/Users/myothant/Documents/New%20project/docs/store/play-store-icon-512.png)
- Source icon crop: [`docs/store/zaycho-icon-source.png`](/Users/myothant/Documents/New%20project/docs/store/zaycho-icon-source.png)

## Honest limitation

Actual submission still requires your own Apple Developer and Google Play Console accounts, signing keys, app privacy declarations, and final screenshots from real device builds. Those parts cannot be completed from code alone.
