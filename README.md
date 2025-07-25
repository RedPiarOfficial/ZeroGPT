# ZeroGPT

[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](https://github.com/username/project/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Stage](https://img.shields.io/badge/stage-alpha-red.svg)

[Documentation](https://red-3.gitbook.io/zerogpt/)

**ZeroGPT** is a Python library for interacting with AI APIs, providing capabilities for text and image generation.

## Features

* Text generation using various models
* Image creation based on textual descriptions
* Support for "uncensored" mode for more unrestricted responses
* Optimized memory and data handling
* Streamed data support
* Secure request authentication

## Installation

```bash
pip install zerogpt
```

## Usage

### Client Initialization

```python
from zerogpt import Client

client = Client()
```

### Text Generation

```python
# Simple request
response = client.send_message("Hi, how are you?")

# Request with instruction
response = client.send_message(
    "Tell me about space",
    instruction="You are an astronomy expert"
)

# Using "uncensored" mode
response = client.send_message(
    "Explain a complex topic",
    uncensored=True
)

# Using "think" mode (deeper reasoning)
response = client.send_message(
    "Solve a difficult math problem",
    think=True
)

# With context
messages=[
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"}
]
response = client.send_message(
    messages,
    think=True
)
```

### Image Generation

```python
# Create image
result = client.create_image(
    prompt="anime neko girl",
    samples=1,
    resolution=(768, 512),
    seed=-1,
    steps=50
)

# Get generated image
image = client.get_image(result['data']['request_id'])

# Save image
image.download(['path/to/save/image.png'])

# View image
image.open()
```

### Image to Prompt

```python
from zerogpt.utils.tools import image_to_prompt

resp = image_to_prompt('path/to/image.png')
```

### Working with Dummy Context[^1]

```python
from zerogpt.utils.prompt import Dummy

# Create context
dummy = Dummy()
dummy.create(messages=[
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"}
])

# Also possible for image generation
dummy = Dummy()
dummy.create(prompt='neko girl', steps=100)

# Save context
dummy.save("context.bin")

# Load context
dummy.load("context.bin")

# Use instead of messages:
# client.send_message(dummy)
# or
# client.create_image(dummy)
```


## Parameters

### send_message

* `input` (str or list): Text prompt or list of messages
* `instruction` (str, optional): System instruction
* `think` (bool, optional): Use model with deeper reasoning
* `uncensored` (bool, optional): Use unrestricted mode

### create_image

* `prompt` (str): Description of the desired image
* `samples` (int, optional): Number of samples
* `resolution` (tuple, optional): Image resolution (width, height)
* `seed` (int, optional): Seed for reproducibility
* `steps` (int, optional): Number of generation steps
* `negative_prompt` (str, optional): Description of undesired elements

## Security

The library uses HMAC-SHA256 to sign requests and ensure secure data transmission. All requests are authenticated using timestamps to prevent replay attacks.

## Requirements

* Python 3.8+

## License

MIT License
Copyright (c) 2025 RedPiar

## Author

[RedPiar](https://t.me/RedPiar)

[^1]: Dummy is used to compress context and data in general, very useful for systems with low RAM. It can also be saved for even greater memory efficiency!
