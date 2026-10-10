import { useEffect, useRef, useState } from 'react'
import { PEOPLE_INFO } from './talk.js'

// Chat with an AI avatar through the FastAPI backend (backend/main.py).
// Locally, /api is proxied to http://127.0.0.1:8000 by vite.config.js; VITE_API_URL can point elsewhere.
const API = import.meta.env.VITE_API_URL ?? ''
const MAX_CHARS = 2000
const OFFLINE = "Can't reach the backend. Start it on port 8000 (see README: Talk to people (backend))."

// one conversation per person, kept across closing and reopening the panel
const CONVOS = new Map()
const convo = (id) => {
  if (!CONVOS.has(id)) CONVOS.set(id, { messages: [], sessionId: null })
  return CONVOS.get(id)
}

// tiny markdown: ``` code blocks, `code`, **bold**, after escaping HTML so replies can't inject markup
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
function md(text) {
  return esc(text)
    .split(/```/)
    .map((chunk, i) =>
      i % 2
        ? `<pre><code>${chunk.replace(/^[a-z]*\n/, '')}</code></pre>`
        : chunk
            .replace(/`([^`\n]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>')
            .replace(/\n/g, '<br>'),
    )
    .join('')
}

export default function ChatPanel({ id, onClose }) {
  const info = PEOPLE_INFO[id]
  const c = convo(id)
  const [messages, setMessages] = useState(c.messages)
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const scroller = useRef()
  const input = useRef()

  const push = (m) => {
    c.messages = [...c.messages, m]
    setMessages(c.messages)
  }

  useEffect(() => {
    input.current?.focus()
    const esc = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', esc)
    return () => window.removeEventListener('keydown', esc)
  }, [onClose])

  useEffect(() => {
    scroller.current?.scrollTo(0, scroller.current.scrollHeight)
  }, [messages, busy])

  async function send() {
    const message = text.trim()
    if (!message || busy) return
    setText('')
    push({ from: 'you', text: message })
    setBusy(true)
    try {
      const res = await fetch(`${API}/api/people/${id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: c.sessionId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        // no JSON detail = the dev proxy (or the static site) couldn't reach the backend at all
        push({ from: 'system', text: data.detail || OFFLINE })
        return
      }
      c.sessionId = data.session_id
      push({ from: 'them', text: data.reply })
    } catch {
      push({ from: 'system', text: OFFLINE }) // network error: backend not running
    } finally {
      setBusy(false)
      input.current?.focus()
    }
  }

  return (
    <aside className="chat" onMouseDown={(e) => e.stopPropagation()}>
      <header>
        <div>
          <div className="chat-name">{info?.name ?? id}</div>
          <div className="chat-sub">AI avatar · {info?.course} · {info?.room}</div>
        </div>
        <button className="chat-x" onClick={onClose} aria-label="Close chat">
          ✕
        </button>
      </header>
      <div className="chat-log" ref={scroller}>
        {messages.length === 0 && (
          <div className="msg system">You're chatting with an AI avatar, not the real professor. Say hi!</div>
        )}
        {messages.map((m, i) =>
          m.from === 'them' ? (
            <div key={i} className="msg them" dangerouslySetInnerHTML={{ __html: md(m.text) }} />
          ) : (
            <div key={i} className={`msg ${m.from}`}>
              {m.text}
            </div>
          ),
        )}
        {busy && <div className="msg them typing">…</div>}
      </div>
      <form
        className="chat-send"
        onSubmit={(e) => {
          e.preventDefault()
          send()
        }}
      >
        <textarea
          ref={input}
          value={text}
          maxLength={MAX_CHARS}
          rows={2}
          placeholder="Ask about the course…"
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              send()
            }
          }}
        />
        <button type="submit" disabled={busy || !text.trim()}>
          Send
        </button>
      </form>
    </aside>
  )
}
