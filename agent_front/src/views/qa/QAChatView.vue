<template>
  <div class="qa-page">
    <!-- 左侧：会话列表 -->
    <div class="session-panel">
      <div class="session-header">
        <span>会话列表</span>
        <el-button :icon="Plus" circle size="small" :disabled="isStreaming" @click="newSession" />
      </div>
      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === currentSessionId }"
          @click="switchSession(s.id)"
        >
          <el-icon><ChatDotRound /></el-icon>
          <span class="session-name">{{ s.name }}</span>
          <el-icon class="delete-btn" @click.stop="deleteSession(s.id)"><Close /></el-icon>
        </div>
      </div>
    </div>

    <!-- 右侧：聊天区 -->
    <div class="chat-panel">
      <div class="chat-messages" ref="messagesEl" @scroll="handleMessagesScroll">
        <div v-if="messages.length === 0 && !isStreaming" class="empty-hint">
          <p>🤖 你好！我是 EduAgent 智能助手</p>
          <p>有任何 IT 学习问题，随时问我</p>
        </div>

        <ChatBubble
          v-for="msg in messages"
          :key="msg.id"
          :role="msg.role"
          :sources="msg.sources"
        >
          <MarkdownRenderer v-if="msg.content" :content="msg.content" />
          <span v-else-if="msg.streaming && progressStage" class="progress-hint">
            <span class="dot" /><span class="dot" /><span class="dot" />
            {{ progressStage }}
          </span>
          <span v-else-if="msg.streaming" class="thinking">
            <span class="dot" /><span class="dot" /><span class="dot" />
          </span>
          <p v-if="msg.error" class="stream-error">{{ msg.error }}</p>
        </ChatBubble>
      </div>

      <div class="chat-input-area">
        <el-input
          ref="inputRef"
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="输入问题，Enter 发送，Shift+Enter 换行"
          resize="none"
          :disabled="isStreaming"
          @keydown="handleKeydown"
        />
        <div class="input-actions">
          <el-tooltip
            :content="webSearchEnabled ? 'Web Search 已开启：低置信度时先搜索互联网再回答' : 'Web Search 已关闭：低置信度时直接由大模型回答'"
            placement="top"
          >
            <el-switch
              v-model="webSearchEnabled"
              :disabled="isStreaming"
              active-text="🌐"
              inactive-text=""
              size="small"
            />
          </el-tooltip>
          <el-tag
            v-if="lastAnswerMode"
            size="small"
            :type="answerModeTagType"
          >
            {{ answerModeLabel }}
          </el-tag>
          <el-button
            type="primary"
            :loading="isStreaming"
            :disabled="!inputText.trim() || isStreaming"
            @click="sendMessage"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, ChatDotRound, Close } from '@element-plus/icons-vue'
import { v4 as uuidv4 } from 'uuid'
import { ElMessage } from 'element-plus'
import ChatBubble from '@/components/chat/ChatBubble.vue'
import MarkdownRenderer from '@/components/chat/MarkdownRenderer.vue'
import { useAuthStore } from '@/stores/auth'
import { readSSE } from '@/utils/sse'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  streaming?: boolean
  error?: string
}

interface Session {
  id: string
  name: string
  messages: Message[]
}

const router = useRouter()
const auth = useAuthStore()

const sessions = ref<Session[]>([])
const currentSessionId = ref('')
const messages = ref<Message[]>([])
const inputText = ref('')
const messagesEl = ref<HTMLElement>()

const isStreaming = ref(false)
const progressStage = ref('')   // 进度提示文字
const lastAnswerMode = ref('')
const lastConfidence = ref(0)
let activeController: AbortController | null = null
let followLatest = true

// Web Search 开关（会话级，默认开启）
const webSearchEnabled = ref(true)

// ── 回答模式标签 ──────────────────────────────────────────────
const answerModeTagType = computed(() => {
  switch (lastAnswerMode.value) {
    case 'rag':           return 'success'   // 绿色
    case 'web_augmented': return 'primary'   // 蓝色
    case 'general':       return 'warning'   // 橙色
    default:              return 'info'      // 灰色 (llm_direct)
  }
})

const answerModeLabel = computed(() => {
  switch (lastAnswerMode.value) {
    case 'rag':           return `RAG ${lastConfidence.value}%`
    case 'web_augmented': return `🌐 Web增强`
    case 'general':       return '通用回答'
    default:              return 'LLM直答'
  }
})

// ── 会话管理 ──────────────────────────────────────────────────

function newSession() {
  if (isStreaming.value) return
  const id = `student_session_${uuidv4()}`
  const session: Session = { id, name: `会话 ${sessions.value.length + 1}`, messages: [] }
  sessions.value.unshift(session)
  switchSession(id)
}

function switchSession(id: string) {
  if (isStreaming.value) return
  currentSessionId.value = id
  const s = sessions.value.find(s => s.id === id)
  // 直接引用 session.messages，后续只需操作 messages.value，不再单独操作 session.messages
  messages.value = s ? s.messages : []
  lastAnswerMode.value = ''
  followLatest = true
  scrollToBottom()
}

function deleteSession(id: string) {
  if (isStreaming.value) return
  const idx = sessions.value.findIndex(s => s.id === id)
  if (idx === -1) return
  sessions.value.splice(idx, 1)
  if (currentSessionId.value === id) {
    sessions.value.length > 0 ? switchSession(sessions.value[0].id) : newSession()
  }
}

// ── 键盘处理：Enter 发送，Shift+Enter 换行 ────────────────────

function handleKeydown(e: KeyboardEvent) {
  // IME 输入法合成期间（isComposing）不触发发送
  if (e.isComposing) return
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// ── 发送消息：读取 SSE，批量刷新同一个回答气泡 ────────────────

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  if (!currentSessionId.value) newSession()

  // 立即清空输入框，防止用户重复触发
  inputText.value = ''

  const session = sessions.value.find(s => s.id === currentSessionId.value)

  const userMsg: Message = { id: uuidv4(), role: 'user', content: text }
  messages.value.push(userMsg)
  if (session && session.messages.filter(m => m.role === 'user').length === 1) {
    session.name = text.slice(0, 20) + (text.length > 20 ? '…' : '')
  }

  // 在第一个 await 前锁定发送，避免 Enter 与按钮重复提交。
  isStreaming.value = true
  progressStage.value = ''
  lastAnswerMode.value = ''
  lastConfidence.value = 0
  followLatest = true
  const assistantMsg = reactive<Message>({
    id: uuidv4(),
    role: 'assistant',
    content: '',
    streaming: true,
    sources: [],
  })
  messages.value.push(assistantMsg)
  const controller = new AbortController()
  activeController = controller
  let pendingText = ''
  let flushTimer: ReturnType<typeof setTimeout> | undefined
  let receivedDone = false

  function flushTokens() {
    if (flushTimer !== undefined) clearTimeout(flushTimer)
    flushTimer = undefined
    if (!pendingText) return
    assistantMsg.content += pendingText
    pendingText = ''
    if (followLatest) void scrollToBottom()
  }

  function appendToken(content: string) {
    pendingText += content
    // 不等待 Markdown 重绘来读取下一个网络块，每 32ms 合并一次更新。
    if (flushTimer === undefined) flushTimer = setTimeout(flushTokens, 32)
  }

  try {
    await scrollToBottom()
    const resp = await fetch('/api/v1/qa/chat/stream', {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Authorization': `Bearer ${auth.token}`,
      },
      body: JSON.stringify({
        session_id:        currentSessionId.value,
        message:           text,
        enable_web_search: webSearchEnabled.value,
      }),
    })

    if (resp.status === 401) {
      auth.logout()
      await router.push('/login')
      return
    }
    if (!resp.ok || !resp.body) {
      throw new Error(resp.status >= 500
        ? '问答服务异常，请稍后重试'
        : `请求失败（HTTP ${resp.status}），请重试`)
    }

    await readSSE(resp.body, frame => {
      if (frame.data.trim() === '[DONE]') {
        receivedDone = true
        return false
      }
      let evt
      try {
        evt = JSON.parse(frame.data)
      } catch {
        throw new Error('流式响应格式异常，请重试')
      }
      const type = evt.type ?? frame.event
      if (type === 'progress' && typeof evt.stage === 'string') {
        progressStage.value = evt.stage
      } else if (type === 'token' && typeof evt.content === 'string') {
        progressStage.value = ''
        appendToken(evt.content)
      } else if (type === 'meta') {
        lastAnswerMode.value = evt.answer_mode ?? ''
        lastConfidence.value = Math.round((evt.confidence ?? 0) * 100)
        assistantMsg.sources = evt.sources ?? []
      } else if (type === 'error') {
        // 与 JSON 解析分开处理，后端异常必须传到外层 catch。
        throw new Error(evt.message || '流式回答失败，请重试')
      } else if (type === 'done') {
        receivedDone = true
        return false
      }
    })
    if (!receivedDone) {
      throw new Error('连接中断，回答未完成，请重试')
    }
    if (!assistantMsg.content && !pendingText) {
      throw new Error('未收到回答内容，请重试')
    }
  } catch (err) {
    if (!controller.signal.aborted) {
      assistantMsg.error = err instanceof Error ? err.message : '请求失败，请重试'
      ElMessage.error(assistantMsg.error)
      console.error('[QA SSE]', err)
    }
  } finally {
    flushTokens()
    assistantMsg.streaming = false
    isStreaming.value = false
    progressStage.value = ''
    if (activeController === controller) activeController = null
    if (followLatest) await scrollToBottom()
  }
}

function handleMessagesScroll() {
  const el = messagesEl.value
  if (el) followLatest = el.scrollHeight - el.scrollTop - el.clientHeight < 80
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

onMounted(() => {
  newSession()
})

onBeforeUnmount(() => activeController?.abort())
</script>

<style scoped>
.qa-page {
  display: flex;
  height: calc(100vh - 56px - 48px);
  gap: 16px;
}

/* ── 左侧会话列表 ── */
.session-panel {
  width: 200px;
  background: #fff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  font-weight: 500;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #595959;
  transition: background 0.15s;
}
.session-item:hover { background: #f5f7fa; }
.session-item.active { background: #e6f4ff; color: #1677ff; }
.session-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.delete-btn {
  opacity: 0;
  flex-shrink: 0;
  color: #bfbfbf;
  transition: opacity 0.15s, color 0.15s;
}
.session-item:hover .delete-btn { opacity: 1; }
.delete-btn:hover { color: #ff4d4f !important; }

/* ── 右侧聊天区 ── */
.chat-panel {
  flex: 1;
  min-width: 0;
  min-height: 0;
  background: #fff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 20px;
}
.empty-hint {
  text-align: center;
  color: #8c8c8c;
  margin-top: 80px;
  font-size: 15px;
  line-height: 2;
}
.chat-input-area {
  border-top: 1px solid #f0f0f0;
  padding: 12px 16px;
}
.input-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

/* ── 思考中跳点动画 ── */
.thinking {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 0;
}
.stream-error {
  margin: 8px 0 0;
  color: #f56c6c;
  font-size: 13px;
}
.progress-hint {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: 13px;
  color: #8c8c8c;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #bfbfbf;
  animation: bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
  40%            { transform: scale(1.1); opacity: 1; }
}
</style>
