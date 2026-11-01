# Social platform support policy

There is no safe, stable, universally authorized download method for every social-media platform. MediaFlow will not scrape logged-in pages, reuse browser cookies, defeat DRM/paywalls/access controls, or claim third-party extraction support it has not tested.

The upstream platform documentation must be reviewed before each adapter. An official metadata API does not by itself authorize downloading the underlying media file. YouTube's developer policies explicitly prohibit allowing users to download videos for offline playback outside the YouTube Premium experience: https://developers.google.com/youtube/terms/developer-policies-guide. The official YouTube captions download endpoint is scoped to caption tracks and requires permission to edit the video: https://developers.google.com/youtube/v3/docs/captions/download.

Potential compliant paths: let a user export/download their own account data from the platform, then convert files locally; or integrate a platform's official export API only where its current terms explicitly authorize the desired operation and the user has appropriate permission. Generic direct public media URLs remain available when the origin serves the media directly without access barriers.

Current verified platform-specific adapters: none. This is deliberate, not a claim of broad support.
