# Model Capabilities (Modalities)

This page lists which input and output modalities (text, image, audio, video) each model configured in ExpertGPTs supports **at the provider API level**.

> **Important**: This describes what the models accept, not what ExpertGPTs sends. The app sends **text and images**: text files are embedded into the user message (see `ATTACHMENT_FILE_TYPES` in `lib/shared/constants.py`), and images can be attached for models marked `"vision": True` in `LLM_PROVIDERS`. Voice input is transcribed to text first (see [Speech-to-text](#integration-notes)). There is no audio or video upload, so the video capabilities listed below are not usable in the app yet.

**Last verified**: 2026-10-10 against the provider documentation listed under [Sources](#sources).

## Overview

✅ supported · ❌ not supported · ⚠️ supported according to third-party sources, not confirmed by the provider's own docs

| Provider | Model | Model ID | Context | Text | Image | Audio | Video | Output |
|---|---|---|---|:-:|:-:|:-:|:-:|---|
| **DeepSeek** | DeepSeek V4.1 Flash | `deepseek-flash` | 1M | ✅ | ✅ | ❌ | ❌ | Text |
| | DeepSeek V4 Pro | `deepseek-v4-pro` | 1M | ✅ | ❌ | ❌ | ❌ | Text |
| **OpenAI** | GPT-6.1 Sol | `gpt-6.1-sol` | 1.05M | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-6 Astra | `gpt-6-astra` | 1.05M | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-6 Luna | `gpt-6-luna` | 1.05M | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-5.6 Sol | `gpt-5.6-sol` | 1.05M | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-5.6 Terra | `gpt-5.6-terra` | 1.05M | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-5.6 Luna | `gpt-5.6-luna` | 1.05M | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-5.4 Mini | `gpt-5.4-mini` | 400K | ✅ | ✅ | ❌ | ❌ | Text |
| | GPT-5.4 Nano | `gpt-5.4-nano` | 400K | ✅ | ✅ | ❌ | ❌ | Text |
| **Z.AI** | GLM-5.3 | `glm-5.3` | 1M | ✅ | ❌ | ❌ | ❌ | Text |
| | GLM-5.2 | `glm-5.2` | 1M | ✅ | ❌ | ❌ | ❌ | Text |
| | GLM-5 | `glm-5` | 200K | ✅ | ❌ | ❌ | ❌ | Text |
| | GLM-4.7-Flash | `glm-4.7-flash` | 200K | ✅ | ❌ | ❌ | ❌ | Text |
| **KIMI** | KIMI K3 | `kimi-k3` | 1M | ✅ | ✅ | ❌ | ✅ | Text |
| | KIMI K2.7 Code | `kimi-k2.7-code` | 256K | ✅ | ✅ | ❌ | ✅ | Text |
| | KIMI K2.7 Code HighSpeed | `kimi-k2.7-code-highspeed` | 256K | ✅ | ⚠️ | ❌ | ⚠️ | Text |
| | KIMI K2.6 | `kimi-k2.6` | 256K | ✅ | ✅ | ❌ | ✅ | Text |

Context sizes come from `LLM_PROVIDERS` in `lib/shared/constants.py`.

## Summary

- **Audio**: no configured model accepts audio input.
- **Output**: every model returns text only (no image, audio or video generation).
- **Video**: only the KIMI models accept video input.
- **Image**: all OpenAI models, all KIMI models and DeepSeek V4.1 Flash.
- **Text only**: DeepSeek V4 Pro and all configured Z.AI models.

## Notes per Provider

### DeepSeek

- `deepseek-flash` (V4.1 Flash) accepts images; the pricing page marks Vision as supported.
- `deepseek-v4-pro` is text-only ("Not supported" for Vision).
- The earlier experimental model, V4-Flash Vision Exp, has been retired; DeepSeek recommends `deepseek-flash` for image input.

### OpenAI

- Every configured model lists "Input modalities: text, image" and "Output modalities: text" on its model page.
- Audio and video endpoints (speech, transcription, videos) are marked "Not supported" for these models.

### Z.AI

- GLM-5.3: "currently supports text-only inputs". It shares its base model with GLM-5.2, which is also text in, text out.
- GLM-5 and GLM-4.7(-Flash) are text-only as well.
- Z.AI's multimodal models are separate model IDs that ExpertGPTs does not configure: GLM-5.3-Flash/FlashX (text, image, video, file input), GLM-5V-Turbo and GLM-4.6V-Flash.

### KIMI

- K3, K2.7 Code and K2.6 accept text, image and video input according to the Kimi API overview and quickstart guides. Images are passed as base64 or `ms://<file-id>`; videos are uploaded as files with `purpose="video"`.
- `kimi-k2.7-code-highspeed` is a faster serving tier of K2.7 Code with the same weights. The official docs do not state its modalities; Alibaba Cloud Model Studio, Vercel AI Gateway and OpenCode list text, image and video input.
- Some third-party sources still describe video input as experimental.

## Other Provider Models (Not Configured)

Models from the same providers that cover the missing capabilities (audio, video input, media generation). None of them are configured as chat models in ExpertGPTs; only GPT-Transcribe and GLM-ASR-2512 are used, for voice input.

| Capability | DeepSeek | OpenAI | Z.AI | KIMI |
|---|---|---|---|---|
| **Audio input** (speech understanding) | – | GPT-Audio-1.5 (text + audio in and out, 128K)<br>GPT-Transcribe, GPT-Live-Transcribe (speech → text) | GLM-ASR-2512 (speech → text, incl. streaming) | – (Kimi-Audio exists only as open weights for self-hosting) |
| **Audio output** (speech) | – | GPT-Audio-1.5, GPT-4o Mini TTS, GPT-Realtime-2.1 / GPT-Live 1 (voice conversation) | – (no TTS model found) | – |
| **Video input** | – | – (no OpenAI model accepts video) | GLM-5.3-Flash / FlashX (text, image, video, file), GLM-4.6V | Configured models already support it |
| **Image input** (where missing today) | `deepseek-flash` already supports it | Configured models already support it | GLM-5.3-Flash / FlashX, GLM-4.6V(-Flash), GLM-OCR (documents) | Configured models already support it |
| **Image generation** | – | GPT-Image-2, GPT-Image-2.5 Sunburst / Flare | GLM-Image, CogView-4 | – |
| **Video generation** | – | – (no Sora model on OpenAI's current model list) | CogVideoX-3 | – |

### Integration Notes

ExpertGPTs sends requests to the Chat Completions endpoint, so only chat models plug into the existing flow:

- **GLM-5.3-Flash / FlashX (Z.AI)**: the simplest addition. It is a regular chat model that takes image and video as message content, and it would give Z.AI image and video input. It needs an entry in `LLM_PROVIDERS` with `"vision": True` for image input; video input would also need a video upload in the chat UI.
- **GPT-Audio-1.5 (OpenAI)**: the only audio model on Chat Completions (Responses and Realtime are not supported). It needs audio recording/upload and playback of audio responses in the UI.

The other models use their own endpoints:

- **Speech-to-text** (GPT-Transcribe, GLM-ASR-2512): works as a pre-processing step. Transcribe audio to text, then send it to any configured model; this gives all models indirect voice input. ExpertGPTs uses both for voice input in the chat toolbox: GPT-Transcribe for OpenAI experts, GLM-ASR-2512 for all others (see `lib/audio/transcription.py`).
- **Text-to-speech** (GPT-4o Mini TTS): could read responses aloud, independent of the chat model.
- **Image and video generation** (GPT-Image, GLM-Image, CogView-4, CogVideoX-3): separate features, not chat extensions.

### Open Questions

- **GLM-5V-Turbo**: reportedly removed from Z.AI's pricing page in late August 2026 but still listed on OpenRouter; status unclear, so it is omitted above.
- **DeepSeek V4.1 Flash audio**: one third-party source claims audio support; DeepSeek's own changelog only mentions visual understanding.
- **Sora**: not on OpenAI's current model list; current status unknown.

## Keeping This Page Current

When adding or changing a model in `LLM_PROVIDERS` (`lib/shared/constants.py`), check the model's modalities on the provider's model page and update the overview table. Move it out of [Other Provider Models](#other-provider-models-not-configured) if it was listed there. Also update the **Last verified** date.

## Sources

- **OpenAI**: [Models overview](https://developers.openai.com/api/docs/models), [All models](https://developers.openai.com/api/docs/models/all), [GPT-Audio-1.5](https://developers.openai.com/api/docs/models/gpt-audio-1.5), [Speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text), [Changelog](https://platform.openai.com/docs/changelog), [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [GPT-5.4 Mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini), [GPT-5.4 Nano](https://developers.openai.com/api/docs/models/gpt-5.4-nano)
- **DeepSeek**: [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing), [Change Log](https://api-docs.deepseek.com/updates/)
- **Z.AI**: [Models overview](https://docs.z.ai/guides/overview/overview), [GLM-5.3](https://docs.z.ai/guides/llm/glm-5.3), [GLM-5.2](https://docs.z.ai/guides/llm/glm-5.2), [GLM-5](https://docs.z.ai/guides/llm/glm-5), [GLM-4.7](https://docs.z.ai/guides/llm/glm-4.7), [GLM-5.3-Flash](https://docs.z.ai/guides/vlm/glm-5.3-flash)
- **KIMI**: [API overview](https://platform.kimi.ai/docs/overview), [Model list](https://platform.kimi.ai/docs/models), [Kimi-Audio-7B-Instruct](https://huggingface.co/moonshotai/Kimi-Audio-7B-Instruct), [K3 quickstart](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart), [K2.6 quickstart](https://platform.kimi.ai/docs/guide/kimi-k2-6-quickstart), [Alibaba Model Studio: K2.7 Code HighSpeed](https://help.aliyun.com/en/model-studio/kimi-k2-7-code-highspeed), [Vercel AI Gateway: K2.7 Code HighSpeed](https://vercel.com/ai-gateway/models/kimi-k2.7-code-highspeed/about)

---

**Related**: [Providers](providers.md) · [Multi-Provider LLM](../architecture/multi-provider-llm.md)
