import React, { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import './ProfileAccountPage.css'

export default function ProfileAccountPage(){
  const { user: authUser, token } = useAuth()
  const [user, setUser] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchUserInfo()
  }, [])

  const fetchUserInfo = async () => {
    try {
      setLoading(true)
      const userId = authUser?.id
      
      if (!userId) {
        setMessage({ type: 'error', text: 'Không tìm thấy thông tin đăng nhập' })
        return
      }

      const response = await fetch(`http://localhost:8080/user/users/${userId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Không thể lấy thông tin user')
      }

      const data = await response.json()
      setUser(data)
      setFormData({
        name: data.name || '',
        email: data.email || '',
        phone: data.phone || ''
      })
    } catch (error) {
      setMessage({ type: 'error', text: error.message })
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setMessage({ type: '', text: '' })

      const userId = authUser?.id
      if (!userId) {
        throw new Error('Không tìm thấy thông tin đăng nhập')
      }

      const response = await fetch(`http://localhost:8080/user/users/${userId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error('Cập nhật thông tin thất bại')
      }

      const updatedData = await response.json()
      setUser(updatedData)
      setIsEditing(false)
      setMessage({ type: 'success', text: 'Cập nhật thông tin thành công' })
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: error.message })
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || ''
      })
    }
    setIsEditing(false)
    setMessage({ type: '', text: '' })
  }

  if (loading) {
    return <div className="profile-account-page"><p>Đang tải...</p></div>
  }

  return (
    <div className="profile-account-page">
      <div className="account-header">
        <h2>Thông tin tài khoản</h2>
        {!isEditing && (
          <button className="btn-edit" onClick={() => setIsEditing(true)}>
            Chỉnh sửa
          </button>
        )}
      </div>

      {message.text && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}

      {isEditing ? (
        <div className="account-form">
          <div className="form-group">
            <label htmlFor="name">Họ tên:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
              disabled
            />
            <small>Email không thể thay đổi</small>
          </div>

          <div className="form-group">
            <label htmlFor="phone">Số điện thoại:</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+84912345678"
              className="form-input"
            />
          </div>

          <div className="form-actions">
            <button 
              className="btn-save" 
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Đang lưu...' : 'Lưu'}
            </button>
            <button 
              className="btn-cancel" 
              onClick={handleCancel}
              disabled={saving}
            >
              Hủy
            </button>
          </div>
        </div>
      ) : (
        <div className="account-info">
          <div className="info-item">
            <label>Họ tên:</label>
            <p>{user?.name || '-'}</p>
          </div>

          <div className="info-item">
            <label>Email:</label>
            <p>{user?.email || '-'}</p>
          </div>

          <div className="info-item">
            <label>Số điện thoại:</label>
            <p>{user?.phone || 'Chưa cập nhật'}</p>
          </div>

          <div className="info-item">
            <label>Vai trò:</label>
            <p>{user?.role === 'CUSTOMER' ? 'Khách hàng' : user?.role || '-'}</p>
          </div>
        </div>
      )}
    </div>
  )
}
