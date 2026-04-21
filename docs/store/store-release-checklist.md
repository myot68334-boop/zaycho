# Lyra Shop Store Release Checklist

This project now includes login, account deletion, admin tools, Stripe-ready card payments, image upload, and delivery tracking. The remaining work is mostly secrets, certificates, account ownership, and actual store-console submission.

## Apple App Store

- Build and archive the iOS app from [`mobile/ios`](/Users/myothant/Documents/New%20project/mobile/ios).
- Use a paid Apple Developer account.
- Create the App Store Connect app record, bundle identifier, signing certificate, and provisioning profile.
- Upload an iOS build through Xcode Organizer or Transporter.
- Set the real production web URL in [`mobile/ios/project.yml`](/Users/myothant/Documents/New%20project/mobile/ios/project.yml) before generating the Xcode project.
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
- Provide demo credentials in review notes because login and admin areas exist in this app.
- Include a valid privacy policy URL. Apple requires a privacy policy URL for all apps.
- Make sure the build is complete and functional with no placeholder URLs or unfinished payment flows. Apple’s App Review Guidelines section 2.1(a) explicitly rejects incomplete submissions.
- Upload one to ten screenshots per device family in accepted `.jpeg`, `.jpg`, or `.png` formats. If you do not provide 6.9-inch screenshots, Apple scales compatible 6.5-inch screenshots.

Official references:

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Apple screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications
- Apple app icon guidance: https://developer.apple.com/help/app-store-connect/manage-app-information/add-an-app-icon/
- Apple app privacy requirements: https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy

## Google Play Store

- Open the Android project from [`mobile/android`](/Users/myothant/Documents/New%20project/mobile/android) in Android Studio.
- Install Android SDK and create a signed app bundle (`.aab`).
- Use a Google Play Console account.
- Create the app record and upload the signed bundle.
- Set the real production web URL via `APP_URL` or `PUBLIC_BASE_URL` before release build.
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
- Ensure the target SDK stays current before release. According to Google’s official requirement, new apps and updates submitted on or after August 31, 2025 must target Android 15 / API level 35 or higher.
- Configure Play App Signing for the release upload key.
- Add reviewer instructions on the App content page, including demo customer and admin credentials if review needs access behind login.
- Add both an in-app privacy policy link and an external account deletion link because the app supports account creation.

Official references:

- Google Play target API requirements: https://developer.android.com/google/play/requirements/target-sdk
- Google Play app signing: https://developer.android.com/studio/publish/app-signing
- Google Play app setup: https://support.google.com/googleplay/android-developer/answer/9859152
- Google Play preview assets: https://support.google.com/googleplay/android-developer/answer/1078870
- Google Play Data safety requirements: https://support.google.com/googleplay/android-developer/answer/10787469
- Google Play user data and privacy policy requirements: https://support.google.com/googleplay/android-developer/answer/9888076

## Assets in this repo

- Play icon base: [`docs/store/play-store-icon-512.png`](/Users/myothant/Documents/New%20project/docs/store/play-store-icon-512.png)
- Source icon crop: [`docs/store/zaycho-icon-source.png`](/Users/myothant/Documents/New%20project/docs/store/zaycho-icon-source.png)

## Environment secrets to set before production

- `PUBLIC_BASE_URL`: public HTTPS URL of the deployed app
- `STRIPE_SECRET_KEY`: Stripe secret key for Payment Intents
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key for the Payment Element
- `LYRA_ADMIN_EMAIL`: production admin email
- `LYRA_ADMIN_PASSWORD`: production admin password

## Honest limitation

Actual submission still requires your own Apple Developer and Google Play Console accounts, signing keys, Stripe account, legal privacy review, app privacy answers, Data safety declarations, and final screenshots from real device builds. Those account-owned steps cannot be completed from code alone.
