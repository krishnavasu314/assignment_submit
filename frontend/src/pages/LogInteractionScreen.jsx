import { useEffect, useMemo, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import { fetchHcps, seedHcps } from '../features/hcpSlice'
import { createInteraction, fetchInteractions } from '../features/interactionSlice'
import { addMessage, resetChat, sendChatMessage } from '../features/chatSlice'

const MODEL_OPTIONS = [
  { label: 'Groq Gemma 2 (9B)', value: 'gemma2-9b-it' },
  { label: 'Groq Llama 3.3 (70B)', value: 'llama-3.3-70b-versatile' }
]

const INITIAL_FORM = {
  interaction_type: 'Detailing',
  channel: 'In-person',
  interaction_date: new Date().toISOString().slice(0, 16),
  summary: '',
  raw_notes: '',
  attendees: '',
  outcomes: '',
  next_steps: '',
  products_discussed: '',
  sentiment: 'Neutral'
}

export default function LogInteractionScreen() {
  const dispatch = useDispatch()
  const { list: hcps } = useSelector((state) => state.hcp)
  const interactions = useSelector((state) => state.interactions.list)
  const chat = useSelector((state) => state.chat)

  const [activeTab, setActiveTab] = useState('form')
  const [selectedHcpId, setSelectedHcpId] = useState('')
  const [formState, setFormState] = useState(INITIAL_FORM)
  const [formStatus, setFormStatus] = useState('idle')
  const [formError, setFormError] = useState('')
  const [chatInput, setChatInput] = useState('')
  const [chatModel, setChatModel] = useState(MODEL_OPTIONS[0].value)

  useEffect(() => {
    dispatch(fetchHcps())
  }, [dispatch])

  useEffect(() => {
    if (selectedHcpId) {
      dispatch(fetchInteractions(selectedHcpId))
    }
  }, [dispatch, selectedHcpId])

  const selectedHcp = useMemo(
    () => hcps.find((hcp) => String(hcp.id) === String(selectedHcpId)),
    [hcps, selectedHcpId]
  )

  const handleFormChange = (event) => {
    const { name, value } = event.target
    setFormState((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!selectedHcpId) {
      setFormError('Select an HCP before submitting.')
      return
    }

    setFormStatus('loading')
    setFormError('')

    const payload = {
      hcp_id: Number(selectedHcpId),
      interaction_type: formState.interaction_type,
      channel: formState.channel,
      interaction_date: formState.interaction_date
        ? new Date(formState.interaction_date).toISOString()
        : null,
      summary: formState.summary || null,
      raw_notes: formState.raw_notes || null,
      attendees: formState.attendees || null,
      outcomes: formState.outcomes || null,
      next_steps: formState.next_steps || null,
      products_discussed: formState.products_discussed
        ? formState.products_discussed.split(',').map((item) => item.trim()).filter(Boolean)
        : null,
      sentiment: formState.sentiment || null,
      source: 'form'
    }

    try {
      await dispatch(createInteraction(payload)).unwrap()
      setFormStatus('success')
      setFormState(INITIAL_FORM)
    } catch (error) {
      setFormStatus('error')
      setFormError(error.message || 'Unable to save interaction.')
    }
  }

  const handleSendChat = async () => {
    if (!chatInput.trim()) {
      return
    }

    if (!selectedHcpId) {
      setFormError('Select an HCP before starting the chat.')
      return
    }

    const message = chatInput.trim()
    dispatch(addMessage({ role: 'user', content: message }))
    setChatInput('')
    await dispatch(sendChatMessage({ message, hcpId: selectedHcpId, model: chatModel }))
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI-First CRM HCP Module</p>
          <h1>Log Interaction Screen</h1>
          <p className="subtitle">
            Capture HCP engagement through structured forms or a conversational assistant powered by LangGraph.
          </p>
        </div>
        <button className="ghost" type="button" onClick={() => dispatch(seedHcps())}>
          Seed sample HCPs
        </button>
      </header>

      <section className="hcp-panel">
        <div>
          <label htmlFor="hcpSelect">Select HCP</label>
          <select
            id="hcpSelect"
            value={selectedHcpId}
            onChange={(event) => setSelectedHcpId(event.target.value)}
          >
            <option value="">Choose an HCP</option>
            {hcps.map((hcp) => (
              <option key={hcp.id} value={hcp.id}>
                {hcp.name} - {hcp.specialty || 'General'}
              </option>
            ))}
          </select>
        </div>
        {selectedHcp ? (
          <div className="hcp-summary">
            <h3>{selectedHcp.name}</h3>
            <p>{selectedHcp.specialty || 'Specialty'} - {selectedHcp.organization || 'Organization'}</p>
            <p>{selectedHcp.city || 'City'}, {selectedHcp.state || 'State'} - Tier {selectedHcp.tier || 'N/A'}</p>
          </div>
        ) : (
          <div className="hcp-summary empty">Select an HCP to load details.</div>
        )}
      </section>

      <section className="tabs">
        <button
          type="button"
          className={activeTab === 'form' ? 'active' : ''}
          onClick={() => setActiveTab('form')}
        >
          Structured Form
        </button>
        <button
          type="button"
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          Conversational Chat
        </button>
      </section>

      <section className="content-grid">
        {activeTab === 'form' ? (
          <div className="card">
            <h2>Structured Log</h2>
            <p className="helper">Use the form to capture mandatory fields. The AI can summarize raw notes.</p>
            <form onSubmit={handleSubmit} className="form-grid">
              <div>
                <label>Interaction Type</label>
                <input name="interaction_type" value={formState.interaction_type} onChange={handleFormChange} />
              </div>
              <div>
                <label>Channel</label>
                <input name="channel" value={formState.channel} onChange={handleFormChange} />
              </div>
              <div>
                <label>Interaction Date</label>
                <input
                  type="datetime-local"
                  name="interaction_date"
                  value={formState.interaction_date}
                  onChange={handleFormChange}
                />
              </div>
              <div>
                <label>Sentiment</label>
                <select name="sentiment" value={formState.sentiment} onChange={handleFormChange}>
                  <option value="Positive">Positive</option>
                  <option value="Neutral">Neutral</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div className="span-two">
                <label>Summary</label>
                <textarea name="summary" value={formState.summary} onChange={handleFormChange} />
              </div>
              <div className="span-two">
                <label>Raw Notes (AI extraction)</label>
                <textarea
                  name="raw_notes"
                  value={formState.raw_notes}
                  onChange={handleFormChange}
                  placeholder="Paste verbatim notes; the AI will auto-populate summary and entities if empty."
                />
              </div>
              <div>
                <label>Attendees</label>
                <input name="attendees" value={formState.attendees} onChange={handleFormChange} />
              </div>
              <div>
                <label>Outcomes</label>
                <input name="outcomes" value={formState.outcomes} onChange={handleFormChange} />
              </div>
              <div>
                <label>Next Steps</label>
                <input name="next_steps" value={formState.next_steps} onChange={handleFormChange} />
              </div>
              <div>
                <label>Products Discussed</label>
                <input
                  name="products_discussed"
                  value={formState.products_discussed}
                  onChange={handleFormChange}
                  placeholder="Comma separated"
                />
              </div>
              <div className="span-two form-footer">
                <button type="submit" className="primary" disabled={formStatus === 'loading'}>
                  {formStatus === 'loading' ? 'Saving...' : 'Log Interaction'}
                </button>
                {formStatus === 'success' && <span className="success">Saved.</span>}
                {formError && <span className="error">{formError}</span>}
              </div>
            </form>
          </div>
        ) : (
          <div className="card chat-card">
            <div className="chat-header">
              <div>
                <h2>Conversational Assistant</h2>
                <p className="helper">Prompt the agent to log, edit, or review interactions.</p>
              </div>
              <select value={chatModel} onChange={(event) => setChatModel(event.target.value)}>
                {MODEL_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="chat-window">
              {chat.messages.length === 0 ? (
                <div className="chat-empty">
                  Start with: "Log a follow-up with Dr. Iyer about cardiac outcomes."
                </div>
              ) : (
                chat.messages.map((message, index) => (
                  <div key={`${message.role}-${index}`} className={`chat-bubble ${message.role}`}>
                    <p>{message.content}</p>
                    {message.toolCalls && (
                      <pre>{JSON.stringify(message.toolCalls, null, 2)}</pre>
                    )}
                  </div>
                ))
              )}
            </div>
            <div className="chat-input">
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                placeholder="Ask the agent to log or update an interaction..."
              />
              <button type="button" className="primary" onClick={handleSendChat}>
                Send
              </button>
              <button type="button" className="ghost" onClick={() => dispatch(resetChat())}>
                Clear
              </button>
            </div>
          </div>
        )}

        <aside className="card activity-card">
          <h2>Recent Interactions</h2>
          <p className="helper">Latest interactions for the selected HCP.</p>
          {interactions.length === 0 ? (
            <div className="empty">No interactions logged yet.</div>
          ) : (
            <div className="interaction-list">
              {interactions.map((interaction) => (
                <article key={interaction.id}>
                  <div className="interaction-header">
                    <span>{interaction.interaction_type || 'Interaction'}</span>
                    <span>
                      {interaction.interaction_date
                        ? new Date(interaction.interaction_date).toLocaleString()
                        : 'Date pending'}
                    </span>
                  </div>
                  <p>{interaction.summary || interaction.notes || 'No summary provided.'}</p>
                  <div className="interaction-meta">
                    <span>{interaction.channel || 'Channel TBD'}</span>
                    <span>{interaction.sentiment || 'Sentiment TBD'}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </aside>
      </section>
    </div>
  )
}
