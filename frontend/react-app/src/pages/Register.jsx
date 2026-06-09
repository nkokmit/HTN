import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import api, { getUserApiOrigin } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Register(){
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated, user } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const from = location.state?.from?.pathname || '/profile'

  async function handleSubmit(event){
    event.preventDefault()
    setLoading(true)
    setError('')
    try{
      await api.request('/auth/register/', {
        method: 'POST',
        body: JSON.stringify({
          name,
          email,
          password,
          role: 'CUSTOMER',
        }),
      }, getUserApiOrigin())

      const loginResult = await api.request('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }, getUserApiOrigin())

      login(loginResult.user, loginResult.token)
      navigate(from, { replace: true })
    }catch(err){
      setError(err.message || String(err))
    }finally{
      setLoading(false)
    }
  }

  if(isAuthenticated){
    return (
      <div className="page-wrap">
        <section className="section-card login-shell">
          <span className="hero-kicker">Đã đăng nhập</span>
          <h1>Xin chào {user?.name || 'bạn'}</h1>
          <p>Bạn đã có tài khoản sẵn rồi.</p>
          <div className="hero-actions">
            <Link className="btn btn-primary" to="/profile">Vào tài khoản</Link>
            <Link className="btn btn-secondary" to="/">Về trang chủ</Link>
          </div>
        </section>
      </div>
    )
  }

  return (
    <div className="page-wrap">
      <section className="section-card login-shell">
        <div className="login-copy">
          <span className="hero-kicker">Đăng ký tài khoản</span>
          <h1>Tạo tài khoản mới để mua sắm và quản lý profile</h1>
          <p>Đây là trang riêng cho đăng ký. Sau khi tạo xong, hệ thống sẽ tự đăng nhập luôn.</p>
        </div>

        <form className="register-form" onSubmit={handleSubmit}>
          <div className="form-headline">
            <h2>Đăng ký</h2>
            <p>Điền thông tin để tạo tài khoản mới.</p>
          </div>
          <label>
            <span>Họ và tên</span>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Nguyễn Văn A" required />
          </label>
          <label>
            <span>Email</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="new@example.com" required />
          </label>
          <label>
            <span>Mật khẩu</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Tối thiểu 6 ký tự" required />
          </label>
          {error ? <p className="login-error">{error}</p> : null}
          <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? 'Đang đăng ký...' : 'Đăng ký'}</button>
          <Link className="btn btn-secondary" to="/login">Quay lại đăng nhập</Link>
        </form>
      </section>
    </div>
  )
}
