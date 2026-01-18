import { configureStore } from '@reduxjs/toolkit'

import hcpReducer from './features/hcpSlice'
import interactionReducer from './features/interactionSlice'
import chatReducer from './features/chatSlice'

export const store = configureStore({
  reducer: {
    hcp: hcpReducer,
    interactions: interactionReducer,
    chat: chatReducer
  }
})
