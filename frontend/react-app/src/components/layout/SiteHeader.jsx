import React, { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import api, { getCartApiOrigin } from '../../services/api'
import { useAuth } from '../../context/AuthContext'

export default function SiteHeader(){
  const location = useLocation()
  const [cartCount, setCartCount] = useState(0)
  const { ready, isAuthenticated, user } = useAuth()

  useEffect(() => {
    let mounted = true

    async function loadCount(){
      if(!ready || !isAuthenticated || !user?.id){
        if(mounted) setCartCount(0)
        return
      }
      try{
        const items = await api.request(`/carts/${user.id}/`, {}, getCartApiOrigin())
        if(!mounted) return
        setCartCount(Array.isArray(items) ? items.reduce((sum, item) => sum + Number(item.quantity || 0), 0) : 0)
      }catch{
        if(mounted) setCartCount(0)
      }
    }

    loadCount()
    return () => { mounted = false 
      window.removeEventListener('cart-updated', loadCount) }
  }, [location.pathname, ready, isAuthenticated, user?.id])

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link to="/" className="brand" aria-label="Ecomerence home">
          <div className="brand-badge">E</div>
          <div>
            <small>Marketplace</small>
            <span>Ecomerence</span>
          </div>
        </Link>

        <label className="searchbox" aria-label="Search products">
          <span>🔎</span>
          <input placeholder="Tìm sản phẩm, thương hiệu, danh mục..." />
          <span className="pill">Deal hôm nay</span>
        </label>

        <div className="top-actions">
          <Link className="action-chip" to={isAuthenticated ? '/profile' : '/login'}>
            <b>👤</b>
            <span>{isAuthenticated ? (location.pathname.startsWith('/profile') ? 'Tài khoản' : (user?.name || 'Tài khoản')) : 'Đăng nhập'}</span>
          </Link>
          <Link className="action-chip" to="/cart">
            <b>🛒</b>
            <span>{location.pathname.startsWith('/cart') ? 'Đang xem giỏ' : 'Giỏ hàng'}</span>
            <strong className="cart-count-badge">{cartCount}</strong>
          </Link>
          <div className="action-chip">
            <b>🚚</b>
            <span>Giao nhanh 2h</span>
          </div>
        </div>
      </div>
    </header>
  )
}