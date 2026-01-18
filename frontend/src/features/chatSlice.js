import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'

import { apiPost } from '../api'

export const sendChatMessage = createAsyncThunk(
  'chat/send',
  async ({ message, hcpId, model }) => {
    return apiPost('/agent/chat', {
      message,
      hcp_id: hcpId || null,
      model: model || null
    })
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    status: 'idle',
    error: null,
    lastInteractionId: null
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload)
    },
    resetChat: (state) => {
      state.messages = []
      state.status = 'idle'
      state.error = null
      state.lastInteractionId = null
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.status = 'loading'
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = 'succeeded'
        const responseMessages = action.payload.messages
          .filter((message) => message.role !== 'user')
          .map((message) => ({
            role: message.role,
            content: message.content,
            toolCalls: message.tool_calls || null
          }))

        state.messages.push(...responseMessages)
        state.lastInteractionId = action.payload.interaction_id || null
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message
      })
  }
})

export const { addMessage, resetChat } = chatSlice.actions
export default chatSlice.reducer
