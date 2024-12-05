URL: https://docs.fal.ai/clients/javascript#migration-from-serverless-client-to-client
---


# Client Library for JavaScript / TypeScript

## Introduction

The client for JavaScript / TypeScript provides a seamless interface to interact with fal.

## Installation

First, add the client as a dependency in your project:

- [npm](#tab-panel-2)
- [yarn](#tab-panel-3)
- [pnpm](#tab-panel-4)
- [bun](#tab-panel-5)

```

npm install --save @fal-ai/client
```

```

yarn add @fal-ai/client
```

```

pnpm add @fal-ai/client
```

```

bun add @fal-ai/client
```

## Features

### 1\. Call an endpoint

Endpoints requests are managed by a queue system. This allows fal to provide a reliable and scalable service.

The `subscribe` method allows you to submit a request to the queue and wait for the result.

```

import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/flux/dev", {

  input: {

    prompt: "a cat",

    seed: 6252023,

    image_size: "landscape_4_3",

    num_images: 4,

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

### 2\. Queue Management

You can manage the queue using the following methods:

#### Submit a Request

Submit a request to the queue using the `queue.submit` method.

```

import { fal } from "@fal-ai/client";

const { request_id } = await fal.queue.submit("fal-ai/flux/dev", {

  input: {

    prompt: "a cat",

    seed: 6252023,

    image_size: "landscape_4_3",

    num_images: 4,

  },

  webhookUrl: "https://optional.webhook.url/for/results",

});
```

This is useful when you want to submit a request to the queue and retrieve the result later. You can save the `request_id` and use it to retrieve the result later.

#### Check Request Status

Retrieve the status of a specific request in the queue:

```

import { fal } from "@fal-ai/client";

const status = await fal.queue.status("fal-ai/flux/dev", {

  requestId: "764cabcf-b745-4b3e-ae38-1200304cf45b",

  logs: true,

});
```

#### Retrieve Request Result

Get the result of a specific request from the queue:

```

import { fal } from "@fal-ai/client";

const result = await fal.queue.result("fal-ai/flux/dev", {

  requestId: "764cabcf-b745-4b3e-ae38-1200304cf45b",

});

console.log(result.data);

console.log(result.requestId);
```

### 3\. File Uploads

Some endpoints require files as input. However, since the endpoints run asynchronously, processed by the queue, you will need to provide URLs to the files instead of the actual file content.

Luckily, the client library provides a way to upload files to the server and get a URL to use in the request.

```

import { fal } from "@fal-ai/client";

const file = new File(["Hello, World!"], "hello.txt", { type: "text/plain" });

const url = await fal.storage.upload(file);
```

### 4\. Streaming

Some endpoints support streaming:

```

import { fal } from "@fal-ai/client";

const stream = await fal.stream("fal-ai/flux/dev", {

  input: {

    prompt: "a cat",

    seed: 6252023,

    image_size: "landscape_4_3",

    num_images: 4,

  },

});

for await (const event of stream) {

  console.log(event);

}

const result = await stream.done();
```

### 5\. Realtime Communication

For the endpoints that support real-time inference via WebSockets, you can use the realtime client that abstracts the WebSocket connection, re-connection, serialization, and provides a simple interface to interact with the endpoint:

```

import { fal } from "@fal-ai/client";

const connection = fal.realtime.connect("fal-ai/flux/dev", {

  onResult: (result) => {

    console.log(result);

  },

  onError: (error) => {

    console.error(error);

  },

});

connection.send({

  prompt: "a cat",

  seed: 6252023,

  image_size: "landscape_4_3",

  num_images: 4,

});
```

### 6\. Run

The endpoints can also be called directly instead of using the queue system.

```

import { fal } from "@fal-ai/client";

const result = await fal.run("fal-ai/flux/dev", {

  input: {

    prompt: "a cat",

    seed: 6252023,

    image_size: "landscape_4_3",

    num_images: 4,

  },

});

console.log(result.data);

console.log(result.requestId);
```

## API Reference

For a complete list of available methods and their parameters, please refer to [JavaScript / TypeScript API Reference documentation](https://fal-ai.github.io/fal-js/reference).

## Examples

Check out some of the examples below to see real-world use cases of the client library:

- See `fal.realtime` in action with SDXL Lightning: [https://github.com/fal-ai/sdxl-lightning-demo-app](https://github.com/fal-ai/sdxl-lightning-demo-app)

## Support

If you encounter any issues or have questions, please visit the [GitHub repository](https://github.com/fal-ai/fal-js) or join our [Discord Community](https://discord.gg/fal-ai).

## Migration from `serverless-client` to `client`

As fal no longer uses “serverless” as part of the AI provider branding, we also made sure that’s reflected in our libraries. However, that’s not the only thing that changed in the new client. There was lot’s of improvements that happened thanks to our community feedback.

So, if you were using the `@fal-ai/serverless-client` package, you can upgrade to the new `@fal-ai/client` package by following these steps:

1. Remove the `@fal-ai/serverless-client` package from your project:



```


npm uninstall @fal-ai/serverless-client
```

2. Install the new `@fal-ai/client` package:



```


npm install --save @fal-ai/client
```

3. Update your imports:



```


import * as fal from "@fal-ai/serverless-client";

import { fal } from "@fal-ai/client";
```

4. Now APIs return a `Result<Output>` type that contains the `data` which is the API output and the `requestId`. This is a breaking change from the previous version, that allows us to return extra data to the caller without future breaking changes.



```


const data = fal.subscribe(endpointId, { input });

const { data, requestId } = fal.subscribe(endpointId, { input });
```