import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import UserDashboard from '../components/profile/UserDashboard'
import ProfileAccount from './profile/ProfileAccountPage'
import ProfileOrders from './profile/ProfileOrdersPage'
import ProfileReturns from './profile/ProfileReturnsPage'
import ProfileAddress from './profile/ProfileAddressPage'
import ProfilePayment from './profile/ProfilePaymentPage'
import ProfileReviews from './profile/ProfileReviewsPage'
import { useAuth } from '../context/AuthContext'

export default function Profile(){
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <div className="page-wrap">
      <div className="profile-header">
        <h1>Trang tài khoản</h1>
        <p style={{margin:'8px 0 0',color:'var(--muted)'}}>
          Thiết kế theo hướng dashboard của các marketplace lớn để dễ mở rộng các mục sau này.
        </p>
        <div className="profile-auth-banner">
          <div>
            <strong>{isAuthenticated ? `Xin chào, ${user?.name || 'bạn'}` : 'Bạn chưa đăng nhập'}</strong>
            <p>{isAuthenticated ? `Email: ${user?.email || '---'}` : 'Đăng nhập để đồng bộ giỏ hàng và tài khoản.'}</p>
          </div>
          {isAuthenticated ? (
            <button className="btn btn-secondary" type="button" onClick={() => logout()}>
              Đăng xuất
            </button>
          ) : (
            <Link className="btn btn-primary" to="/login">Đăng nhập</Link>
          )}
        </div>
        <div style={{marginTop:10,fontSize:13}}>
          <Link to="/">← Quay về trang chủ</Link>
        </div>
      </div>

      <div className="profile-shell">
        <UserDashboard />
        <section className="profile-panel">
        <Routes>
          <Route path="account" element={<ProfileAccount />} />
          <Route path="orders" element={<ProfileOrders />} />
          <Route path="returns" element={<ProfileReturns />} />
          <Route path="address" element={<ProfileAddress />} />
          <Route path="payment" element={<ProfilePayment />} />
          <Route path="reviews" element={<ProfileReviews />} />
          <Route path="/" element={<div className="profile-content">Chọn một mục ở thanh bên để xem nội dung.</div>} />
        </Routes>
        </section>
      </div>
    </div>
  )
}
