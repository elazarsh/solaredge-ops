# PixVerse API notes (verified against docs.platform.pixverse.ai on 2026-10-13)

Base URL `https://app-api.pixverse.ai`. All responses: `{ "ErrCode", "ErrMsg", "Resp" }`; success is `ErrCode == 0`.
Headers on every request: `API-KEY: <key>`, `Ai-trace-id: <fresh UUID>`. JSON endpoints add `Content-Type: application/json`.

| Purpose | Method + path |
|---|---|
| Text-to-video | `POST /openapi/v2/video/text/generate` |
| Image-to-video | `POST /openapi/v2/video/img/generate` (needs `img_id`) |
| First/last frame | `POST /openapi/v2/video/transition/generate` (`first_frame_img`, `last_frame_img`) |
| Multi-transition (2-7 frames, 1-30 s) | `POST /openapi/v2/video/multi_transition/generate` |
| Reference-to-video (Fusion) | `POST /openapi/v2/video/fusion/generate` |
| Extend (V6) | `POST /openapi/v2/video/extend/generate` (`source_video_id` or `video_media_id`) |
| Lip sync | `POST /openapi/v2/video/lip_sync/generate` |
| Sound effects | `POST /openapi/v2/video/sound_effect/generate` |
| Motion control (Mimic) | `POST /openapi/v2/video/mimic/generate` |
| Status | `GET /openapi/v2/video/result/{video_id}` |
| Upload image | `POST /openapi/v2/image/upload` (multipart `image` or `image_url`) -> `Resp.img_id` |
| Upload video/audio | `POST /openapi/v2/media/upload` -> media id |
| Balance | `GET /openapi/v2/account/balance` -> `credit_monthly`, `credit_package` |

## Text-to-video body (fields documented)

`prompt` (<= 5000 chars), `model` (v3.5/v4/v4.5/v5/v5.5/v5.6/v6/c1), `duration` (v6/c1: 1-15), `quality`
(360p/540p/720p/1080p), `aspect_ratio` (v6/c1: 16:9 4:3 1:1 3:4 9:16 2:3 3:2 21:9), `seed` (0-2147483647),
`generate_audio_switch` (v5.5+/v6/c1), `generate_multi_clip_switch` (v5.5/v6). Examples in the docs also show
`motion_mode` and `camera_movement` (e.g. `zoom_in`) and `template_id`. Older models additionally take
sound-effect and TTS lip-sync fields. `negative_prompt` appears in the docs' overview example and the MCP
parameters; if an endpoint rejects it, drop it.

## Flow

1. Submit -> `Resp.video_id`.
2. Poll status every 3-5 s: `Resp.status` 1 done, 5 generating, 6 deleted, 7 moderation failed, 8 failed.
3. On 1, `Resp.url` is the downloadable file (public CDN URL; do not send your API key to it).
4. Or use webhooks (create a `webhook_id` on the platform webhook page, include it in the request).

## Limits and money

- Concurrency by plan: Free 3, Essential 15, Scale 20, Business 25.
- Credits per second, V6 (no audio / audio): 360p 5/7, 540p 7/9, 720p 9/12, 1080p 18/23.
  C1: 360p 6/8, 540p 8/10, 720p 10/13, 1080p 19/24. Fusion with video references on V6 costs about double.
  Docs example: $1 = 5 videos of V6/720p/5 s/no audio (225 credits per dollar). Older models are priced
  per clip; see the pricing page.
- Upload limits: image <= 20 MB and <= 10000 px (JPG/PNG/WebP). Video/audio per feature, for example
  Extend/Sound-effect/Restyle: 50 MB, 30 s; Lip sync: 250 MB, 300 s; Swap/Modify/Mimic: 100 MB, 30 s.
  Video resolution up to 1920 px on a side.

## Error codes worth recognising

400017 invalid parameter; 400018/400019 prompt too long; 400032 invalid image id; 500044 concurrency limit;
500054 image moderation; 500063 video/image/text moderation; 500069 high load; 500071 effect does not
support 720p/1080p; 500090 insufficient balance.

## Official MCP server

`uvx pixverse-mcp` with `PIXVERSE_API_KEY` (needs Python 3.10+ and uv). Documented capabilities: text-to-video with
aspect ratio, duration 5 or 8 s, quality 360-1080p, motion mode. It follows the same billing as the API.
Config example: `video-studio/mcp/pixverse.mcp.json.example`.
