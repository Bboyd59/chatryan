URL: https://fal.ai/models/fal-ai/flux-pro/v1.1-ultra/api
---
[Status](https://status.fal.ai) [Docs](/docs) [Pricing](/pricing) [Enterprise](/enterprise)

[Log-in](/login?returnTo=/models/fal-ai/flux-pro/v1.1-ultra/api) [Sign-up](/login?returnTo=/models/fal-ai/flux-pro/v1.1-ultra/api)

# FLUX1.1 \[pro\] ultra Text to Image

fal-ai/flux-pro/v1.1-ultra

FLUX1.1 \[pro\] ultra is the newest version of FLUX1.1 \[pro\], maintaining professional-grade image quality while delivering up to 2K resolution with improved photo realism.

Inference

Commercial use

PlaygroundAPIMore

### Table of contents

JavaScript / Node.js

[**1\. Calling the API**](/models/fal-ai/flux-pro/v1.1-ultra/api#api-call)

- [Install the client](/models/fal-ai/flux-pro/v1.1-ultra/api#api-call-install)
- [Setup your API Key](/models/fal-ai/flux-pro/v1.1-ultra/api#api-call-setup)
- [Submit a request](/models/fal-ai/flux-pro/v1.1-ultra/api#api-call-submit-request)

[**2\. Authentication**](/models/fal-ai/flux-pro/v1.1-ultra/api#auth)

- [API Key](/models/fal-ai/flux-pro/v1.1-ultra/api#auth-api-key)

[**3\. Queue**](/models/fal-ai/flux-pro/v1.1-ultra/api#queue)

- [Submit a request](/models/fal-ai/flux-pro/v1.1-ultra/api#queue-submit)
- [Fetch request status](/models/fal-ai/flux-pro/v1.1-ultra/api#queue-status)
- [Get the result](/models/fal-ai/flux-pro/v1.1-ultra/api#queue-result)

[**4\. Files**](/models/fal-ai/flux-pro/v1.1-ultra/api#files)

- [Data URI (base64)](/models/fal-ai/flux-pro/v1.1-ultra/api#files-data-uri)
- [Hosted files (URL)](/models/fal-ai/flux-pro/v1.1-ultra/api#files-from-url)
- [Uploading files](/models/fal-ai/flux-pro/v1.1-ultra/api#files-upload)

[**5\. Schema**](/models/fal-ai/flux-pro/v1.1-ultra/api#schema)

- [Input](/models/fal-ai/flux-pro/v1.1-ultra/api#schema-input)
- [Output](/models/fal-ai/flux-pro/v1.1-ultra/api#schema-output)
- [Other](/models/fal-ai/flux-pro/v1.1-ultra/api#schema-other)

### About

FLUX1.1 \[pro\], next generation text-to-image model, with 10x accelerated speeds.

All usages of this model must comply with [FLUX.1 PRO Terms of Service](https://blackforestlabs.ai/terms-of-service/).

### 1\. Calling the API [\#](\#api-call-install)

### Install the client [\#](\#api-call-install)

The client provides a convenient way to interact with the model API.

npmyarnpnpmbun

```bg-transparent leading-normal whitespace-pre-wrap
npm install --save @fal-ai/client
```

##### Migrate to @fal-ai/client

The `@fal-ai/serverless-client` package has been deprecated in favor of `@fal-ai/client`. Please check the [migration guide](https://docs.fal.ai/clients/javascript#migration-from-serverless-client-to-client) for more information.

### Setup your API Key [\#](\#api-call-setup)

Set `FAL_KEY` as an environment variable in your runtime.

```bg-transparent leading-normal whitespace-pre-wrap
export FAL_KEY="YOUR_API_KEY"
```

### Submit a request [\#](\#api-call-submit-request)

The client API handles the API submit protocol. It will handle the request status updates and return the result when the request is completed.

```bg-transparent leading-normal whitespace-pre-wrap
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/flux-pro/v1.1-ultra", {
  input: {
    prompt: "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word \"FLUX\" is painted over it in big, white brush strokes with visible texture."
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  },
});
console.log(result.data);
console.log(result.requestId);
```

## 2\. Authentication [\#](\#auth)

The API uses an API Key for authentication. It is recommended you set the `FAL_KEY` environment variable in your runtime when possible.

### API Key [\#](\#auth-api-key)

In case your app is running in an environment where you cannot set environment variables, you can set the API Key manually as a client configuration.

```bg-transparent leading-normal whitespace-pre-wrap
import { fal } from "@fal-ai/client";

fal.config({
  credentials: "YOUR_FAL_KEY"
});
```

##### Protect your API Key

When running code on the client-side (e.g. in a browser, mobile app or GUI applications), make sure to not expose your `FAL_KEY`. Instead, **use a server-side proxy** to make requests to the API. For more information, check out our [server-side integration guide](https://docs.fal.ai/model-endpoints/server-side).

## 3\. Queue [\#](\#queue)

##### Long-running requests

For long-running requests, such as _training_ jobs or models with slower inference times, it is recommended to check the [Queue](https://docs.fal.ai/model-endpoints/queue) status and rely on [Webhooks](https://docs.fal.ai/model-endpoints/webhooks) instead of blocking while waiting for the result.

### Submit a request [\#](\#queue-submit)

The client API provides a convenient way to submit requests to the model.

```bg-transparent leading-normal whitespace-pre-wrap
import { fal } from "@fal-ai/client";

const { request_id } = await fal.queue.submit("fal-ai/flux-pro/v1.1-ultra", {
  input: {
    prompt: "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word \"FLUX\" is painted over it in big, white brush strokes with visible texture."
  },
  webhookUrl: "https://optional.webhook.url/for/results",
});
```

### Fetch request status [\#](\#queue-status)

You can fetch the status of a request to check if it is completed or still in progress.

```bg-transparent leading-normal whitespace-pre-wrap
import { fal } from "@fal-ai/client";

const status = await fal.queue.status("fal-ai/flux-pro/v1.1-ultra", {
  requestId: "764cabcf-b745-4b3e-ae38-1200304cf45b",
  logs: true,
});
```

### Get the result [\#](\#queue-result)

Once the request is completed, you can fetch the result. See the [Output Schema](#schema-output) for the expected result format.

```bg-transparent leading-normal whitespace-pre-wrap
import { fal } from "@fal-ai/client";

const result = await fal.queue.result("fal-ai/flux-pro/v1.1-ultra", {
  requestId: "764cabcf-b745-4b3e-ae38-1200304cf45b"
});
console.log(result.data);
console.log(result.requestId);
```

## 4\. Files [\#](\#files)

Some attributes in the API accept file URLs as input. Whenever that's the case you can pass your own URL or a Base64 data URI.

### Data URI (base64) [\#](\#files-data-uri)

You can pass a Base64 data URI as a file input. The API will handle the file decoding for you. Keep in mind that for large files, this alternative although convenient can impact the request performance.

### Hosted files (URL) [\#](\#files-from-url)

You can also pass your own URLs as long as they are publicly accessible. Be aware that some hosts might block cross-site requests, rate-limit, or consider the request as a bot.

### Uploading files [\#](\#files-upload)

We provide a convenient file storage that allows you to upload files and use them in your requests. You can upload files using the client API and use the returned URL in your requests.

```bg-transparent leading-normal whitespace-pre-wrap
import { fal } from "@fal-ai/client";

const file = new File(["Hello, World!"], "hello.txt", { type: "text/plain" });
const url = await fal.storage.upload(file);
```

##### Auto uploads

The client will auto-upload the file for you if you pass a binary object (e.g. `File`, `Data`).

Read more about file handling in our [file upload guide](https://docs.fal.ai/model-endpoints#file-uploads).

## 5\. Schema [\#](\#schema)

### Input [\#](\#schema-input)

`prompt` `string`\\* required

The prompt to generate an image from.

`seed` `integer`

The same seed and the same prompt given to the same version of the model
will output the same image every time.

`sync_mode` `boolean`

If set to true, the function will wait for the image to be generated and uploaded
before returning the response. This will increase the latency of the function but
it allows you to get the image directly in the response without going through the CDN.

`num_images` `integer`

The number of images to generate. Default value: `1`

`enable_safety_checker` `boolean`

If set to true, the safety checker will be enabled. Default value: `true`

`safety_tolerance` `SafetyToleranceEnum`

API only

The safety tolerance level for the generated image. 1 being the most strict and 5 being the most permissive. Default value: `"2"`

Possible enum values: `1, 2, 3, 4, 5, 6`

**Note:** This property is only available through API calls.

`output_format` `OutputFormatEnum`

The format of the generated image. Default value: `"jpeg"`

Possible enum values: `jpeg, png`

`aspect_ratio` `AspectRatioEnum`

The aspect ratio of the generated image. Default value: `"16:9"`

Possible enum values: `21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21`

`raw` `boolean`

Generate less processed, more natural-looking images.

```bg-transparent leading-normal whitespace-pre-wrap
{
  "prompt": "Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word \"FLUX\" is painted over it in big, white brush strokes with visible texture.",
  "num_images": 1,
  "enable_safety_checker": true,
  "safety_tolerance": "2",
  "output_format": "jpeg",
  "aspect_ratio": "16:9"
}
```

### Output [\#](\#schema-output)

`images` `list<Image>`\\* required

The generated image files info.

`timings` `Timings`\\* required

`seed` `integer`\\* required

Seed of the generated Image. It will be the same value of the one passed in the
input or the randomly generated that was used in case none was passed.

`has_nsfw_concepts` `list<boolean>`\\* required

Whether the generated images contain NSFW concepts.

`prompt` `string`\\* required

The prompt used for generating the image.

```bg-transparent leading-normal whitespace-pre-wrap
{
  "images": [\
    {\
      "url": "",\
      "content_type": "image/jpeg"\
    }\
  ],
  "prompt": ""
}
```

### Other types [\#](\#schema-other)

#### Image [\#](\#type-Image)

`url` `string`\\* required

`width` `integer`\\* required

`height` `integer`\\* required

`content_type` `string`

Default value: `"image/jpeg"`

#### FluxProUltraTextToImageInputRedux [\#](\#type-FluxProUltraTextToImageInputRedux)

`prompt` `string`

The prompt to generate an image from. Default value: `""`

`seed` `integer`

The same seed and the same prompt given to the same version of the model
will output the same image every time.

`sync_mode` `boolean`

If set to true, the function will wait for the image to be generated and uploaded
before returning the response. This will increase the latency of the function but
it allows you to get the image directly in the response without going through the CDN.

`num_images` `integer`

The number of images to generate. Default value: `1`

`enable_safety_checker` `boolean`

If set to true, the safety checker will be enabled. Default value: `true`

`safety_tolerance` `SafetyToleranceEnum`

API only

The safety tolerance level for the generated image. 1 being the most strict and 5 being the most permissive. Default value: `"2"`

Possible enum values: `1, 2, 3, 4, 5, 6`

**Note:** This property is only available through API calls.

`output_format` `OutputFormatEnum`

The format of the generated image. Default value: `"jpeg"`

Possible enum values: `jpeg, png`

`aspect_ratio` `AspectRatioEnum`

The aspect ratio of the generated image. Default value: `"16:9"`

Possible enum values: `21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21`

`raw` `boolean`

Generate less processed, more natural-looking images.

`image_url` `string`\\* required

The image URL to generate an image from. Needs to match the dimensions of the mask.

`image_prompt_strength` `float`

The strength of the image prompt, between 0 and 1. Default value: `0.1`

#### ImageSize [\#](\#type-ImageSize)

`width` `integer`

The width of the generated image. Default value: `512`

`height` `integer`

The height of the generated image. Default value: `512`

#### FluxProRedux [\#](\#type-FluxProRedux)

`prompt` `string`

The prompt to generate an image from. Default value: `""`

`image_size` `ImageSize | Enum`

The size of the generated image. Default value: `landscape_4_3`

Possible enum values: `square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9`

**Note:** For custom image sizes, you can pass the `width` and `height` as an object:

```bg-transparent leading-normal whitespace-pre-wrap
"image_size": {
  "width": 1280,
  "height": 720
}
```

`num_inference_steps` `integer`

The number of inference steps to perform. Default value: `28`

`seed` `integer`

The same seed and the same prompt given to the same version of the model
will output the same image every time.

`guidance_scale` `float`

The CFG (Classifier Free Guidance) scale is a measure of how close you want
the model to stick to your prompt when looking for a related image to show you. Default value: `3.5`

`sync_mode` `boolean`

If set to true, the function will wait for the image to be generated and uploaded
before returning the response. This will increase the latency of the function but
it allows you to get the image directly in the response without going through the CDN.

`num_images` `integer`

The number of images to generate. Default value: `1`

`safety_tolerance` `SafetyToleranceEnum`

API only

The safety tolerance level for the generated image. 1 being the most strict and 5 being the most permissive. Default value: `"2"`

Possible enum values: `1, 2, 3, 4, 5, 6`

**Note:** This property is only available through API calls.

`output_format` `OutputFormatEnum`

The format of the generated image. Default value: `"jpeg"`

Possible enum values: `jpeg, png`

`image_url` `string`\\* required

The image URL to generate an image from. Needs to match the dimensions of the mask.

### Related Models

[fal-ai/fooocus/upscale-or-vary\\
\\
text-to-image\\
\\
Default parameters with automated optimizations and quality improvements.\\
\\
text to image\\
\\
fooocus\\
\\
upscaling](/models/fal-ai/fooocus/upscale-or-vary) [fal-ai/fast-sdxl-controlnet-canny\\
\\
text-to-image\\
\\
Generate Images with ControlNet.\\
\\
stable diffusion\\
\\
controlnet\\
\\
text to image](/models/fal-ai/fast-sdxl-controlnet-canny) [fal-ai/recraft-v3\\
\\
text-to-image\\
\\
Recraft V3 is a text-to-image model with the ability to generate long texts, vector art, images in brand style, and much more. As of today, it is SOTA in image generation, proven by Hugging Face’s industry-leading Text-to-Image Benchmark by Artificial Analysis.\\
\\
image generation\\
\\
vector art\\
\\
typograph](/models/fal-ai/recraft-v3)