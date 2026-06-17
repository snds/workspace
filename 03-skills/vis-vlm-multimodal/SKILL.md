---
name: vis-vlm-multimodal
description: >
  Vision-language and multimodal models — systems that connect pixels to text. CLIP-style joint
  embeddings and zero-shot classification/retrieval; generative VLMs for captioning, VQA, visual
  grounding, and document/OCR understanding; open-vocabulary detection/segmentation; and multimodal
  RAG. How to prompt, ground, and evaluate VLMs — and where they hallucinate. Reach here for "describe /
  ask about / search / reason over images with language." Triggers: VLM, vision language, CLIP,
  multimodal, image captioning, VQA, visual grounding, OCR, document understanding, embeddings, zero-shot.
aliases: [vis-vlm-multimodal, vlm, multimodal-vision]
triggers: [vlm, vision language model, clip, multimodal, image captioning, visual question answering, vqa, visual grounding, open vocabulary, ocr, document understanding, image embedding, zero-shot classification, image retrieval, multimodal rag]
tier: spoke
hub: vision-foundations
domain: vision
prerequisites: [data-foundations]
surfaces: ["*"]
spec_version: "2.0"
---

# Vision — Vision-Language & Multimodal

Where computer vision meets language models. VLMs let you query images the way you query text —
"what's wrong in this photo," "find the frame with a forklift," "extract this invoice" — and they've
collapsed many bespoke CV tasks into prompting. The evaluation + data discipline is [[data-foundations]];
the perception substrate is [[vision-foundations]].

## Two families, two jobs
- **Contrastive / embedding (CLIP, SigLIP):** map images and text into one vector space. Powers **zero-shot
  classification** (compare image to label *names*), **semantic image search / retrieval**, dedup, and as the
  vision encoder inside bigger systems. Cheap, fast, no generation.
- **Generative VLMs (GPT-4V-class, Qwen-VL, LLaVA, etc.):** an image encoder feeding an LLM — they *produce
  text*: captioning, **VQA**, reasoning, step-by-step inspection, structured extraction (image → JSON).

## What VLMs unlock
- **Open-vocabulary detection/segmentation:** name the class in text, no retraining ("segment every crack") —
  pairs with [[vis-detection-tracking]] / [[vis-segmentation]] (GroundingDINO + SAM = text → mask).
- **Document & OCR understanding:** modern VLMs read layouts, tables, and forms end-to-end — often beating
  classical OCR pipelines for structured extraction.
- **Visual grounding:** tie a phrase to a region ("the red valve, top-left") — the bridge between language and pixels.
- **Multimodal RAG:** embed images + text, retrieve the relevant frames/pages, and ground the answer in them.

## Prompt, ground, and constrain
- **Be specific and structured.** Ask for JSON with named fields; give the schema. Provide a reference or example
  for consistent extraction.
- **Ground every claim** — require the model to cite the region/text it used; ungrounded answers are where
  hallucination lives.
- **Decompose** hard questions (detect → crop → ask about the crop) rather than one mega-prompt; feed a detector's
  crops to the VLM for reliable per-object reasoning.

## Evaluate against hallucination
The dangerous failure is a **fluent, confident, wrong** answer about something not in the image.
- Use **grounded** metrics (does the cited region support the claim), held-out VQA accuracy, and human spot-checks
  on *your* images ([[data-foundations]]).
- Watch for **prompt sensitivity** and **bias** (the model "sees" what it expects). Calibrate trust to the task's
  cost of error — a VLM triaging is fine; a VLM as sole authority on a safety call is not.

## Cost & latency
Generative VLMs are heavy (API cost or large local weights). Use a cheap embedding model to **filter/retrieve**,
then spend a generative call only on the candidates that matter. For video, sample frames — don't caption every one
([[vis-video-pipelines]]).

## Related
- foundation → [[data-foundations]]
- hub → [[vision-foundations]]
- peer ↔ [[vis-segmentation]]
