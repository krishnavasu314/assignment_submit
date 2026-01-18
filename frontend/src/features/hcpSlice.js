import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'

import { apiGet, apiPost } from '../api'

export const fetchHcps = createAsyncThunk('hcp/fetchHcps', async () => {
  return apiGet('/hcps')
})

export const seedHcps = createAsyncThunk('hcp/seedHcps', async () => {
  return apiPost('/hcps/seed', {})
})

const hcpSlice = createSlice({
  name: 'hcp',
  initialState: {
    list: [],
    status: 'idle',
    error: null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.pending, (state) => {
        state.status = 'loading'
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.list = action.payload
      })
      .addCase(fetchHcps.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message
      })
      .addCase(seedHcps.fulfilled, (state, action) => {
        state.list = action.payload
      })
  }
})

export default hcpSlice.reducer
