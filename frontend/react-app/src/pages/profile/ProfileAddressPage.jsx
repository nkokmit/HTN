import React, { useEffect, useState } from 'react'
import api, { getUserApiOrigin } from '../../services/api'
import { useAuth } from '../../context/AuthContext'

export default function ProfileAddressPage() {
  const { user, isAuthenticated } = useAuth()
  const [addresses, setAddresses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Điều khiển đóng mở và trạng thái Form
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingAddressId, setEditingAddressId] = useState(null) // null: Thêm mới | Khác null: ID địa chỉ đang sửa
  const [formState, setFormState] = useState({ loading: false, message: '' })
  const [formData, setFormData] = useState({
    full_name: '',
    phone_number: '',
    city: '',
    district: '',
    ward: '',
    detail_address: '',
    is_default: false
  })

  // Lấy danh sách địa chỉ từ user-service
  const loadAddresses = async () => {
    setLoading(true)
    try {
      if (!isAuthenticated || !user?.id) return
      const data = await api.request('/addresses/', {}, getUserApiOrigin())
      setAddresses(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Không thể tải danh sách địa chỉ.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAddresses()
  }, [isAuthenticated, user?.id])

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  // Bật modal thêm mới địa chỉ
  const openAddModal = () => {
    setEditingAddressId(null)
    setFormData({
      full_name: user?.name || '', // Lấy mặc định tên user nếu có
      phone_number: user?.phone || '', // Lấy mặc định số điện thoại user nếu có
      city: '',
      district: '',
      ward: '',
      detail_address: '',
      is_default: addresses.length === 0 // Nếu chưa có địa chỉ nào, tự động đặt làm mặc định
    })
    setFormState({ loading: false, message: '' })
    setIsFormOpen(true)
  }

  // Bật modal chỉnh sửa địa chỉ đang có
  const openEditModal = (address) => {
    setEditingAddressId(address.id)
    setFormData({
      full_name: address.full_name || '',
      phone_number: address.phone_number || '',
      city: address.city || '',
      district: address.district || '',
      ward: address.ward || '',
      detail_address: address.detail_address || '',
      is_default: address.is_default || false
    })
    setFormState({ loading: false, message: '' })
    setIsFormOpen(true)
  }

  // Xử lý gửi biểu mẫu (Thêm / Cập nhật)
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.full_name.trim() || !formData.phone_number.trim() || !formData.city.trim() || !formData.detail_address.trim()) {
      setFormState({ loading: false, message: 'Vui lòng điền các thông tin bắt buộc (*)' })
      return
    }

    setFormState({ loading: true, message: 'Đang lưu thông tin...' })

    try {
      if (editingAddressId) {
        // Gửi lệnh cập nhật dữ liệu (PUT)
        await api.request(`/addresses/${editingAddressId}/`, {
          method: 'PUT',
          body: JSON.stringify(formData)
        }, getUserApiOrigin())
      } else {
        // Gửi lệnh tạo mới dữ liệu (POST)
        await api.request('/addresses/', {
          method: 'POST',
          body: JSON.stringify(formData)
        }, getUserApiOrigin())
      }
      
      setIsFormOpen(false)
      loadAddresses() // Làm mới danh sách hiển thị
    } catch (err) {
      setFormState({ loading: false, message: err.message || 'Đã có lỗi xảy ra.' })
    }
  }

  // Xử lý xóa địa chỉ
  const handleDelete = async (addressId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa địa chỉ nhận hàng này không?')) return
    try {
      await api.request(`/addresses/${addressId}/`, { method: 'DELETE' }, getUserApiOrigin())
      loadAddresses()
    } catch (err) {
      alert(err.message || 'Không thể xóa địa chỉ này.')
    }
  }

  if (loading) return <div className="page-wrap"><div className="section-card">Đang tải danh sách địa chỉ...</div></div>

  return (
    <div className="profile-address-container" style={{ padding: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '22px' }}>Địa chỉ nhận hàng</h2>
          <p style={{ color: '#666', fontSize: '14px', margin: '4px 0 0 0' }}>Quản lý các địa điểm nhận hàng của bạn để tối ưu hóa quá trình thanh toán.</p>
        </div>
        <button className="btn btn-primary" onClick={openAddModal}>
          + Thêm địa chỉ mới
        </button>
      </div>

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {/* Render danh sách thẻ địa chỉ */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {addresses.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px', background: '#fcfcfc', borderRadius: '8px', border: '1px dashed #bbb' }}>
            <p style={{ color: '#777', margin: 0 }}>Sổ địa chỉ của bạn đang trống.</p>
          </div>
        ) : (
          addresses.map((addr) => (
            <div 
              key={addr.id} 
              style={{ 
                padding: '20px', 
                border: addr.is_default ? '2px solid #007bff' : '1px solid #e0e0e0', 
                borderRadius: '8px',
                background: '#fff',
                position: 'relative',
                boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
              }}
            >
              {addr.is_default && (
                <span style={{ position: 'absolute', top: '20px', right: '20px', background: '#007bff', color: '#fff', fontSize: '12px', padding: '3px 10px', borderRadius: '4px', fontWeight: 'bold' }}>
                  Mặc định
                </span>
              )}
              
              <h3 style={{ margin: '0 0 10px 0', fontSize: '18px', color: '#333' }}>{addr.full_name}</h3>
              <p style={{ margin: '4px 0', color: '#555', fontSize: '15px' }}><strong>Số điện thoại:</strong> {addr.phone_number}</p>
              <p style={{ margin: '4px 0', color: '#555', fontSize: '15px', lineHeight: '1.4' }}>
                <strong>Địa chỉ:</strong> {addr.detail_address}{addr.ward ? `, ${addr.ward}` : ''}{addr.district ? `, ${addr.district}` : ''}, {addr.city}
              </p>

              <div style={{ marginTop: '16px', display: 'flex', gap: '16px' }}>
                <button 
                  style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', padding: 0, fontSize: '14px', fontWeight: '500' }}
                  onClick={() => openEditModal(addr)}
                >
                  Chỉnh sửa
                </button>
                {!addr.is_default && (
                  <button 
                    style={{ background: 'none', border: 'none', color: 'crimson', cursor: 'pointer', padding: 0, fontSize: '14px', fontWeight: '500' }}
                    onClick={() => handleDelete(addr.id)}
                  >
                    Xóa
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal Popup để nhập dữ liệu Form */}
      {isFormOpen && (
        <div className="buy-now-backdrop" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1100 }}>
          <div className="buy-now-modal" style={{ backgroundColor: '#fff', padding: '28px', borderRadius: '8px', width: '90%', maxWidth: '520px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ margin: 0, fontSize: '20px' }}>{editingAddressId ? 'Cập nhật thông tin địa chỉ' : 'Thêm địa chỉ giao hàng mới'}</h3>
              <button style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#88px' }} onClick={() => setIsFormOpen(false)}>×</button>
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#444' }}>Họ và tên người nhận *</span>
                <input style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }} type="text" name="full_name" value={formData.full_name} onChange={handleInputChange} placeholder="Ví dụ: Nguyễn Văn Đô" />
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#444' }}>Số điện thoại liên hệ *</span>
                <input style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }} type="text" name="phone_number" value={formData.phone_number} onChange={handleInputChange} placeholder="Ví dụ: 0987654321" />
              </label>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500', color: '#444' }}>Tỉnh/Thành phố *</span>
                  <input style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }} type="text" name="city" value={formData.city} onChange={handleInputChange} placeholder="Ví dụ: Hà Nội" />
                </label>
                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500', color: '#444' }}>Quận/Huyện</span>
                  <input style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }} type="text" name="district" value={formData.district} onChange={handleInputChange} placeholder="Ví dụ: Cầu Giấy" />
                </label>
              </div>

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#444' }}>Phường/Xã</span>
                <input style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }} type="text" name="ward" value={formData.ward} onChange={handleInputChange} placeholder="Ví dụ: Dịch Vọng Hậu" />
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#444' }}>Địa chỉ chi tiết *</span>
                <input style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }} type="text" name="detail_address" value={formData.detail_address} onChange={handleInputChange} placeholder="Số nhà, ngõ ngách, tên đường..." />
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '6px', cursor: 'pointer' }}>
                <input type="checkbox" name="is_default" checked={formData.is_default} onChange={handleInputChange} disabled={editingAddressId && addresses.find(a => a.id === editingAddressId)?.is_default} />
                <span style={{ fontSize: '14px', color: '#444' }}>Đặt địa chỉ này làm địa chỉ nhận hàng mặc định</span>
              </label>

              {formState.message && <p style={{ margin: '6px 0 0 0', color: 'crimson', fontSize: '14px' }}>{formState.message}</p>}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setIsFormOpen(false)}>Hủy</button>
                <button type="submit" className="btn btn-primary" disabled={formState.loading}>
                  {formState.loading ? 'Đang lưu...' : 'Lưu địa chỉ'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}