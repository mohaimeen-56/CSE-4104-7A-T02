import React, { useState, useRef, useEffect } from 'react'
import { aiApi } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { ChatMessage } from '../components/chatbot/ChatMessage'
import { ChatInput } from '../components/chatbot/ChatInput'
import { MessageSquare, Bot, Sparkles, Trash2 } from 'lucide-react'

const WELCOME_TEXT =
  "Hello! I'm **SalesIQ AI Assistant**.\n\nI can help you with:\n• **Analytics** — revenue, orders, products, regions\n• **Forecasts** — next-month revenue prediction\n• **Anomalies** — unusual sales activity\n• **Scenarios** — what-if analysis\n• **Navigation** — take me to the forecast page\n\nAsk me anything about your sales data, or just chat naturally."

const nowTime = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const welcomeMessage = () => ({
  id: 'welcome',
  sender: 'ai',
  text: WELCOME_TEXT,
  time: nowTime(),
})

export const AIChatbot = () => {
  const { user } = useAuth()
  const [messages, setMessages] = useState([welcomeMessage()])
  const [conversationId, setConversationId] = useState(null)
  const [loading, setLoading] = useState(false)
  const chatEndRef = useRef(null)

  const quickPrompts = [
    'How much revenue did we make this month?',
    'Which product had the best sales?',
    'Which region is growing fastest?',
    'Show unusual sales activity',
    'Generate a sales forecast',
  ]

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const sendToBackend = async (text) => {
    setLoading(true)
    try {
      const res = await aiApi.chat({ message: text, conversation_id: conversationId })
      const data = res.data || {}
      if (data.conversation_id) setConversationId(data.conversation_id)

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: data.ai_response || "Sorry, I couldn't process that.",
          time: nowTime(),
          route: data.route,
          intent: data.intent_detected,
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: err.message || 'Something went wrong reaching SalesIQ AI. Please try again.',
          time: nowTime(),
          error: true,
          retryText: text,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (text) => {
    const trimmed = text.trim()
    if (!trimmed) return
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), sender: 'user', text: trimmed, time: nowTime() },
    ])
    await sendToBackend(trimmed)
  }

  const handleRetry = async (failedMessage) => {
    setMessages((prev) => prev.filter((m) => m.id !== failedMessage.id))
    await sendToBackend(failedMessage.retryText)
  }

  const clearChat = () => {
    setMessages([welcomeMessage()])
    setConversationId(null)
  }

  return (
    <div className="space-y-4 max-w-4xl h-[calc(100vh-100px)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight flex items-center gap-2">
            <Bot className="w-5 h-5 text-secondary" />
            <span>AI Sales Chatbot</span>
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Chat naturally, or ask about your sales data — SalesIQ AI understands both.
          </p>
        </div>

        <button
          onClick={clearChat}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-surface border border-border hover:bg-slate-50 text-text-muted hover:text-danger rounded-lg text-xs font-semibold shadow-xs transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Chat Conversation Window */}
      <div className="flex-1 bg-surface border border-border rounded-2xl p-4 sm:p-5 overflow-y-auto shadow-sm flex flex-col">
        <div className="flex-1 space-y-1">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} onRetry={handleRetry} />
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-xs text-text-muted p-3 bg-[#EEF2F7] rounded-2xl rounded-bl-sm w-fit animate-pulse">
              <Sparkles className="w-3.5 h-3.5 text-secondary animate-spin" />
              <span>SalesIQ AI is typing…</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Chat Input & Suggestions Bar */}
      <ChatInput
        onSend={handleSendMessage}
        loading={loading}
        suggestions={quickPrompts}
      />
    </div>
  )
}
