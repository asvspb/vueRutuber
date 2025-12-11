# Интеграция Qwen-Coder через Qwen-CLI API

## Обзор

Этот документ описывает реализацию интеграции Qwen-Coder через Qwen-CLI API для обеспечения интерактивного участия ИИ-агента в проекте VueExpert.

## Архитектура решения

### Общая схема

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Vue Frontend  │◄─────────────────┤  Backend API    │◄────────────────┤   Qwen-CLI API  │
└─────────────────┘                  └─────────────────┘                 └─────────────────┘
       ▲                                     ▲
       │                                     │
       └─────────────────────────────────────┘
                Direct Integration (опционально)
```

### Компоненты

1. **Фронтенд (Vue.js)** - пользовательский интерфейс для взаимодействия с ИИ-агентом
2. **Backend API** - промежуточный слой для обработки запросов и управления сессиями
3. **Qwen-CLI API** - внешний сервис, предоставляющий доступ к модели Qwen-Coder

## Реализация

### 1. Backend интеграция

Создадим новый модуль в backend для работы с Qwen-CLI API:

**backend/app/qwen_agent.py**
```python
import httpx
import asyncio
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException

class QwenAgent:
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = 300  # 5 минут для сложных задач кодирования
        
    async def generate_code(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Генерация кода с использованием Qwen-Coder"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        payload = {
            "model": "qwen-coder",
            "prompt": prompt,
            "context": context or {},
            "temperature": 0.2,
            "max_tokens": 2048
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/v1/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()["choices"][0]["text"]
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Qwen API error: {str(e)}")
    
    async def stream_code(self, prompt: str, context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """Потоковая генерация кода"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        payload = {
            "model": "qwen-coder",
            "prompt": prompt,
            "context": context or {},
            "temperature": 0.2,
            "max_tokens": 2048,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/v1/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    async for chunk in response.aiter_text():
                        if chunk:
                            yield chunk
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Qwen API streaming error: {str(e)}")
```

**backend/app/main.py** (дополнения)
```python
from app.qwen_agent import QwenAgent
import os

# Инициализация Qwen агента
QWEN_API_URL = os.getenv("QWEN_API_URL", "http://localhost:8001")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

qwen_agent = QwenAgent(QWEN_API_URL, QWEN_API_KEY)

@app.post("/api/ai/generate-code")
async def generate_code(request: dict):
    """Эндпоинт для генерации кода"""
    prompt = request.get("prompt")
    context = request.get("context", {})
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        code = await qwen_agent.generate_code(prompt, context)
        return {"code": code, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.websocket("/api/ai/stream-code")
async def stream_code(websocket: WebSocket):
    """WebSocket эндпоинт для потоковой генерации кода"""
    await websocket.accept()
    
    try:
        data = await websocket.receive_json()
        prompt = data.get("prompt")
        context = data.get("context", {})
        
        if not prompt:
            await websocket.send_json({"error": "Prompt is required"})
            await websocket.close()
            return
            
        async for chunk in qwen_agent.stream_code(prompt, context):
            await websocket.send_text(chunk)
            
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
```

### 2. Фронтенд компоненты

**src/components/AICodeAssistant.vue**
```vue
<template>
  <div class="ai-assistant">
    <div class="assistant-header">
      <h2>Qwen-Coder Assistant</h2>
      <div class="status-indicator" :class="{ active: isConnected }">
        {{ isConnected ? 'Connected' : 'Disconnected' }}
      </div>
    </div>
    
    <div class="chat-container">
      <div class="messages">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          class="message" 
          :class="message.role"
        >
          <div class="message-content">
            <pre v-if="message.role === 'assistant'"><code>{{ message.content }}</code></pre>
            <p v-else>{{ message.content }}</p>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <textarea
          v-model="userInput"
          placeholder="Опишите задачу для Qwen-Coder..."
          @keydown.enter.exact.prevent="sendMessage"
          rows="3"
        ></textarea>
        <button 
          @click="sendMessage" 
          :disabled="!userInput.trim() || isGenerating"
          class="send-button"
        >
          {{ isGenerating ? 'Generating...' : 'Send' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const messages = ref([]);
const userInput = ref('');
const isGenerating = ref(false);
const isConnected = ref(false);
const websocket = ref(null);

const connectWebSocket = () => {
  try {
    websocket.value = new WebSocket('ws://localhost:8000/api/ai/stream-code');

    websocket.value.onopen = () => {
      isConnected.value = true;
      console.log('Connected to Qwen-Coder');
    };

    websocket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        messages.value.push({ role: 'system', content: `Error: ${data.error}` });
        isGenerating.value = false;
      } else {
        // Обработка потоковых данных
        if (messages.value.length > 0 && messages.value[messages.value.length - 1].role === 'assistant') {
          messages.value[messages.value.length - 1].content += data;
        } else {
          messages.value.push({ role: 'assistant', content: data });
        }
      }
    };

    websocket.value.onclose = () => {
      isConnected.value = false;
      console.log('Disconnected from Qwen-Coder');
    };

    websocket.value.onerror = (error) => {
          console.error('WebSocket error:', error);
          isConnected.value = false;
        };
      } catch (error) {
        console.error('Failed to connect to Qwen-Coder:', error);
      }
    };
    
    const sendMessage = async () => {
      if (!userInput.value.trim() || isGenerating.value) return;
      
      const userMessage = userInput.value.trim();
      messages.value.push({ role: 'user', content: userMessage });
      userInput.value = '';
      isGenerating.value = true;
      
      try {
        // Отправка сообщения через WebSocket
        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.send(JSON.stringify({ prompt: userMessage }));
        } else {
          // Fallback к HTTP запросу
          const response = await fetch('/api/ai/generate-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: userMessage })
          });
          
          const data = await response.json();
          if (data.success) {
            messages.value.push({ role: 'assistant', content: data.code });
          } else {
            messages.value.push({ role: 'system', content: `Error: ${data.error}` });
          }
        }
      } catch (error) {
        messages.value.push({ role: 'system', content: `Error: ${error.message}` });
      } finally {
        isGenerating.value = false;
      }
    };
    
    onMounted(() => {
      connectWebSocket();
    });
    
    onUnmounted(() => {
      if (websocket.value) {
        websocket.value.close();
      }
    });
    
    return {
      messages,
      userInput,
      isGenerating,
      isConnected,
      sendMessage
    };
  }
};
</script>

<style scoped>
.ai-assistant {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.status-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-indicator.active {
  background-color: #4caf50;
  color: white;
}

.status-indicator:not(.active) {
  background-color: #f44336;
  color: white;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #fafafa;
}

.message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
}

.message.user {
  background-color: #e3f2fd;
  align-self: flex-end;
}

.message.assistant {
  background-color: #f1f8e9;
  align-self: flex-start;
}

.message-content pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 14px;
}

.input-area {
  display: flex;
  padding: 16px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.input-area textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
  margin-right: 8px;
}

.send-button {
  padding: 12px 24px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.send-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
```

### 3. Конфигурация окружения

**.env.example**
```env
# Qwen-Coder Configuration
QWEN_API_URL=http://localhost:8001
QWEN_API_KEY=your-api-key-here
QWEN_MODEL=qwen-coder
```

**docker-compose.yml** (дополнения)
```yaml
services:
  qwen-cli:
    image: qwen/qwen-cli:latest
    ports:
      - "8001:8000"
    environment:
      - QWEN_MODEL=qwen-coder
      - API_KEY=${QWEN_API_KEY}
    volumes:
      - ./qwen-data:/app/data
    restart: unless-stopped
```

### 4. Использование в проекте

Для интеграции компонента в существующее приложение:

**src/App.vue** (пример интеграции)
```vue
<template>
  <div id="app">
    <header>
      <h1>VueExpert Learning Project</h1>
    </header>
    <main>
      <div class="content">
        <DatabaseConnectionExample />
        <DatabaseExample />
        <Documentation />
        <!-- Добавляем AI ассистента -->
        <AICodeAssistant />
      </div>
    </main>
  </div>
</template>

<script>
import DatabaseConnectionExample from './components/DatabaseConnectionExample.vue';
import DatabaseExample from './components/DatabaseExample.vue';
import Documentation from './components/Documentation.vue';
import AICodeAssistant from './components/AICodeAssistant.vue';

export default {
  name: 'App',
  components: {
    DatabaseConnectionExample,
    DatabaseExample,
    Documentation,
    AICodeAssistant
  }
};
</script>
```

## Возможности Qwen-Coder агента

1. **Генерация кода** - автоматическое создание компонентов Vue, функций, классов
2. **Рефакторинг** - улучшение существующего кода по запросу
3. **Объяснение кода** - детальные пояснения работы кода на русском языке
4. **Поиск ошибок** - анализ кода на наличие багов и уязвимостей
5. **Тестирование** - генерация unit и e2e тестов
6. **Документация** - автоматическое создание документации

## Безопасность

1. **Валидация входных данных** - все запросы к ИИ должны проходить валидацию
2. **Ограничение контекста** - ИИ не должен иметь доступа к конфиденциальным данным
3. **Rate limiting** - ограничение количества запросов для предотвращения abuse
4. **Sandbox выполнение** - сгенерированный код должен проверяться в изолированной среде

## Мониторинг и логирование

1. Все взаимодействия с ИИ должны логироваться для анализа и отладки
2. Метрики использования: количество запросов, время ответа, успешность
3. Алертинг при ошибках подключения к Qwen-CLI API

## Расширяемость

Архитектура позволяет легко заменить Qwen-Coder на другие модели (GPT, Claude, Llama) путем изменения конфигурации и минимальной адаптации кода агента.