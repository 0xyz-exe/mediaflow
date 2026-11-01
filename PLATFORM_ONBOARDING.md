# Registering official social-platform access for MediaFlow

MediaFlow cannot apply for a platform app or consent to legal terms on your behalf. App registration requires your developer account, product identity, privacy policy, redirect domain, requested scopes, and sometimes organizational and regional eligibility. Never send passwords or app secrets in chat. Once credentials exist, configure them locally in an ignored `.env` file.

## Recommended first: TikTok Data Portability

This is an authorized transfer of the signed-in user's own TikTok data, not arbitrary public URL scraping. TikTok says the API currently covers TikTok users in the EEA and UK; confirm current eligibility for the user and app before investing. Access requires two separate approvals: Data Portability API and Login Kit. App access to the Data Portability API is subject to review; TikTok's getting-started material says to submit its application and expect several weeks for review.

1. Sign in to [TikTok for Developers](https://developers.tiktok.com/) using your own TikTok/developer account.
2. Register a new app in the developer portal. Add **Login Kit** and **Data Portability API** products.
3. Configure the exact local callback URL for development, then a stable HTTPS callback domain for production. Do not use a wildcard callback.
4. Request only required scopes. The intended flow needs user authorization and permitted post/data transfer scopes; verify exact names in the portal/docs as scope names can change.
5. Submit the separate Data Portability API application. Describe MediaFlow accurately as a user-initiated personal-media export/import and local conversion tool. Explain data minimization, deletion, user control, security, and the precise post-file use. Do not claim access to arbitrary accounts or public posts.
6. Complete any security/privacy review and app review. Approval is TikTok's decision, not guaranteed.
7. After approval, copy the client key/secret into the local environment only. The secret must never be sent in chat, committed, or put in browser code.

Official docs:
- [Getting started](https://developers.tiktok.com/docs/en/data-portability-api-get-started)
- [Data Portability overview and availability](https://developers.tiktok.com/products/data-portability-api/)
- [Application guidelines](https://developers.tiktok.com/docs/en/data-portability-api-application-guidelines)
- [Data types](https://developers.tiktok.com/docs/en/data-portability-data-types)
- [Download transfer](https://developers.tiktok.com/docs/en/data-portability-api-download)

Alternative available now: request your TikTok data archive in TikTok's own app/account settings, then import the exported media files into MediaFlow for local conversion. Exact menu labels vary by region/app version.

## Instagram (only eligible professional-owned content)

Instagram's API is limited to eligible professional accounts and their own media; it is not a general public-post downloader. Meta's current setup supports Instagram Login. Register an app in [Meta for Developers](https://developers.facebook.com/), add Instagram API with Instagram Login, configure OAuth redirect and privacy/deletion URLs, request only necessary permissions, then test with an account you control. Serving accounts outside app roles/testers may require App Review and Advanced Access. Verify current media fields/permissions in official docs; tokens and media URLs are private credentials and must stay server-side.

- [Instagram API overview](https://developers.facebook.com/docs/instagram-platform/overview/)
- [Instagram Login setup](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/get-started/)
- [IG Media reference](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/)

## YouTube

Do not register a YouTube adapter for downloading video files: YouTube's developer policy disallows allowing users to download videos for offline play outside the YouTube Premium experience. The official captions-download endpoint is a separate, permissioned feature for users authorized to edit the video. Use YouTube's own export/download tools instead.

- [YouTube developer policies](https://developers.google.com/youtube/terms/developer-policies-guide)
- [Captions download API](https://developers.google.com/youtube/v3/docs/captions/download)

## Security and next step

OAuth approval is not a credential. After each platform explicitly approves the app, provide only non-secret facts (products, approved scopes, callback URL, region/eligibility). Store the resulting secrets directly in your machine's `.env`; do not paste them here. MediaFlow can then implement the narrow approved OAuth flow. Never use login passwords, browser cookies, session exports, or third-party scraper APIs as a substitute.
