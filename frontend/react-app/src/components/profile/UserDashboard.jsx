import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function UserDashboard(){
  const nav = useNavigate()
  const { logout } = useAuth()
  function handleMenuClick(key){
    const routeMap = {
      account: '/profile/account',
      orders: '/profile/orders',
      returns: '/profile/returns',
      address: '/profile/address',
      payment: '/profile/payment',
      reviews: '/profile/reviews'
    }
    if(key === 'logout'){
      logout()
      nav('/login')
      return
    }
    const r = routeMap[key]
    if(r) nav(r)
  }

  return (
    <div className="dashboard-card">
      <h3>Tài khoản của bạn</h3>
      <p style={{margin:'0 0 14px',color:'var(--muted)',fontSize:13,lineHeight:1.6}}>
        Quản lý hồ sơ, đơn hàng, địa chỉ và đánh giá ở một nơi.
      </p>
      <button type="button" onClick={()=>handleMenuClick('account')}>Thông tin tài khoản</button>
      <button type="button" onClick={()=>handleMenuClick('orders')}>Đơn hàng của tôi</button>
      <button type="button" onClick={()=>handleMenuClick('returns')}>Yêu cầu trả hàng</button>
      <button type="button" onClick={()=>handleMenuClick('address')}>Sổ địa chỉ</button>
      <button type="button" onClick={()=>handleMenuClick('payment')}>Phương thức thanh toán</button>
      <button type="button" onClick={()=>handleMenuClick('reviews')}>Đánh giá của tôi</button>
      <button type="button" onClick={()=>handleMenuClick('logout')}>Đăng xuất</button>
    </div>
  )
}
