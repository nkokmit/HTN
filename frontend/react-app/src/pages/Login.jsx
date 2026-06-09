import React, { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import api, { getUserApiOrigin } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Login(){
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated, user } = useAuth()
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
      const result = await api.request('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }, getUserApiOrigin())
      login(result.user, result.token)
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
          <p>Bạn đang ở trạng thái đăng nhập rồi. Đi tới trang tài khoản hoặc quay lại mua sắm.</p>
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
          <span className="hero-kicker">Đăng nhập thật</span>
          <h1>Vào tài khoản để đồng bộ giỏ hàng và profile</h1>
          <p>Dùng API đăng nhập của user-service. Sau khi đăng nhập, header sẽ đổi sang “Tài khoản”. Ngay bên dưới có luôn phần đăng ký để tạo tài khoản mới.</p>
        </div>

        <div className="auth-stack">
          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-headline">
              <h2>Đăng nhập</h2>
              <p>Vào tài khoản hiện có của bạn.</p>
            </div>
            <label>
              <span>Email</span>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
            </label>
            <label>
              <span>Mật khẩu</span>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
            </label>
            {error ? <p className="login-error">{error}</p> : null}
            <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? 'Đang đăng nhập...' : 'Đăng nhập'}</button>
            <Link className="btn btn-secondary" to="/register">Đăng ký</Link>
            <Link className="btn btn-secondary" to="/">Quay lại mua sắm</Link>
          </form>
        </div>
      </section>
    </div>
  )
}
