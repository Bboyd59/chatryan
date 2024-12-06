URL: https://elevenlabs.io/docs/conversational-ai/api-reference/get-conversational-ai-agents
---
[ElevenLabs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/elevenlabs-docs/logo/favicon.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/elevenlabs-docs/logo/favicon.png)](/docs)

Search or ask...

Ctrl K

Search...

Navigation

Agents

Get Agents

[Product](/docs/product/introduction) [API Reference](/docs/api-reference/overview) [Developer Guides](/docs/developer-guides/quickstart) [Conversational AI](/docs/conversational-ai/docs/introduction) [Changelog](/docs/changelog/product-updates)

GET

/

v1

/

convai

/

agents

Send

Header

xi-api-key

string

xi-api-key

string

Your API key. This is required by most endpoints to access our API programatically. You can view your xi-api-key using the 'Profile' tab on the website.

Query

cursor

string

cursor

string

Used for fetching next page. Cursor is returned in the response.

page\_size

integer

page\_size

integer

How many Agents to return at maximum. Can not exceed 100, defaults to 30.

search

string

search

string

Search by agents name.

cURL

Python

JavaScript

PHP

Go

Java

Copy

```
curl --request GET \
  --url https://api.elevenlabs.io/v1/convai/agents
```

200

422

Copy

```
{
  "agents": [\
    {\
      "agent_id": "<string>",\
      "name": "<string>",\
      "created_at_unix_secs": 123\
    }\
  ],
  "next_cursor": "<string>",
  "has_more": true
}
```

#### Headers

xi-api-key

string

Your API key. This is required by most endpoints to access our API programatically. You can view your xi-api-key using the 'Profile' tab on the website.

#### Query Parameters

cursor

string

Used for fetching next page. Cursor is returned in the response.

page\_size

integer

default:30

How many Agents to return at maximum. Can not exceed 100, defaults to 30.

Required range: `1 < x < 100`

search

string

Search by agents name.

#### Response

200 - application/json

agents

object\[\]

required

Showchild attributes

has\_more

boolean

required

next\_cursor

string

Was this page helpful?

YesNo

[Suggest edits](https://github.com/elevenlabs/elevenlabs-docs/edit/main/conversational-ai/api-reference/get-conversational-ai-agents.mdx) [Raise issue](https://github.com/elevenlabs/elevenlabs-docs/issues/new?title=Issue on docs&body=Path: /conversational-ai/api-reference/get-conversational-ai-agents)

[WebSocket](/docs/conversational-ai/api-reference/websocket) [Create Agent](/docs/conversational-ai/api-reference/post-conversational-ai-agent)

cURL

Python

JavaScript

PHP

Go

Java

Copy

```
curl --request GET \
  --url https://api.elevenlabs.io/v1/convai/agents
```

200

422

Copy

```
{
  "agents": [\
    {\
      "agent_id": "<string>",\
      "name": "<string>",\
      "created_at_unix_secs": 123\
    }\
  ],
  "next_cursor": "<string>",
  "has_more": true
}
```

### Terms and conditions

By clicking "Continue," I agree to the Terms of Service, acknowledge
ElevenLabs' Privacy Policy.


I consent to the recording, collection and use of my voice and data
derived from my voice to interpret my speech and provide customer
support services.


I consent to sharing my voice and data derived from my voice with
third-party service providers to train and improve our customer
support models.


I understand that if I do not consent to the collection as
described above, ElevenLabs services cannot be provided to
me.