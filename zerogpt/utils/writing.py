from typing import Dict, Any
from uuid import uuid4
import codecs
import httpx

from ..core.transport import GPTTransport
decoder = codecs.getincrementaldecoder('utf-8')()

class WritingClient(GPTTransport):
    def __init__(self, http2=False, timeout=30):
        super().__init__(client_type=1)
        self.session = httpx.Client(http2=http2, timeout=timeout)

    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session_id = str(uuid4())
        req = self.get_req_data(payload)
        resp = self.session.post(req['url'], headers=req['headers'], data=req['payload'])
        
        resp.raise_for_status()
        return {'content': resp.text}
    
    def send_message(self, input, instruction=None, model='gemini-2.0-flash'):
        messages = []
        if isinstance(input, str):
            messages.append({'role': 'user', 'content': input})
        if isinstance(instruction, str):
            messages.insert(0, {'role': 'system', 'content': instruction})
        
        return self.send({
            'messages': messages or input,
            'model': model,
        })
    def get_models_list(self):
        return [
  {
    "label": "Google",
    "models": [
      { "name": "Gemini-2.5-Pro", "value": "gemini-2.5-pro" },
      { "name": "Gemini-2.5-Flash", "value": "gemini-2.5-flash" },
      { "name": "G-2.0-F-Thinking", "value": "gemini-2.0-flash-thinking" },
      { "name": "Gemini-2.0-Flash", "value": "gemini-2.0-flash" }
    ]
  },
  {
    "label": "OpenAI",
    "models": [
      { "name": "O3-Mini", "value": "o3-mini" },
      { "name": "GPT-4o (latest)", "value": "gpt-4o-latest" },
      { "name": "GPT-4o", "value": "gpt-4o" }
    ]
  },
  {
    "label": "ToolBaz",
    "models": [
      { "name": "ToolBaz-v4", "value": "toolbaz_v4" },
      { "name": "ToolBaz-v3.5-Pro", "value": "toolbaz_v3.5_pro" }
    ]
  },
  {
    "label": "xAI",
    "models": [
      { "name": "Grok-3-Beta", "value": "grok-3-beta" }
    ]
  },
  {
    "label": "Facebook",
    "models": [
      { "name": "Llama-4-Maverick", "value": "Llama-4-Maverick" },
      { "name": "Llama-3.3 (70B)", "value": "Llama-3.3-70B" }
    ]
  },
  {
    "label": "Others",
    "models": [
      { "name": "L3-Euryale-v2.1 🤬", "value": "L3-70B-Euryale-v2.1" },
      { "name": "Midnight-Rose", "value": "midnight-rose" },
      { "name": "Unfiltered_X (8x22b)", "value": "unfiltered_x" }
    ]
  }
]
