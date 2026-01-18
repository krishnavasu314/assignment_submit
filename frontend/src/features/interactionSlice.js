import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'

import { apiGet, apiPost, apiPut } from '../api'

export const fetchInteractions = createAsyncThunk(
  'interactions/fetch',
  async (hcpId) => apiGet(`/interactions?hcp_id=${hcpId}`)
)

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (payload) => apiPost('/interactions', payload)
)

export const editInteraction = createAsyncThunk(
  'interactions/edit',
  async ({ interactionId, payload }) => apiPut(`/interactions/${interactionId}`, payload)
)

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    status: 'idle',
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.status = 'loading'
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.list = action.payload
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.list = [action.payload, ...state.list]
      })
      .addCase(editInteraction.fulfilled, (state, action) => {
        state.list = state.list.map((item) =>
          item.id === action.payload.id ? action.payload : item
        )
      })
  }
})

export default interactionSlice.reducer
