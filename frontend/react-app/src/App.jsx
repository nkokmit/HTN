import React from 'react'
import { Routes, Route } from 'react-router-dom'
import SiteHeader from './components/layout/SiteHeader'
import SiteFooter from './components/layout/SiteFooter'
import Home from './pages/Home'
import Cart from './pages/Cart'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import ProductDetail from './pages/ProductDetail'
import { AuthProvider } from './context/AuthContext'
import AiChatbox from './components/assistant/AiChatbox'

export default function App(){
  return (
    <AuthProvider>
      <div className="app-shell">
        <SiteHeader />
        <main className="app-main">
          <Routes>
            <Route path="/cart" element={<Cart />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile/*" element={<Profile />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route path="/" element={<Home />} />
          </Routes>
        </main>
        <SiteFooter />
        <AiChatbox />
      </div>
    </AuthProvider>
  )
}
