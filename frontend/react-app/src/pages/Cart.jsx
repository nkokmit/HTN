// Cập nhật lại file: frontend/react-app/src/pages/Cart.jsx
import React, { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api, { getCartApiOrigin, getApiOrigin, getGatewayApiOrigin } from '../services/api'
import { useAuth } from '../context/AuthContext'

function formatMoney(value){
  const num = Number(value)
  if(Number.isNaN(num)) return '0đ'
  return `${Math.round(num)}đ`
}

export default function Cart(){
  const navigate = useNavigate()
  const { ready, isAuthenticated, user } = useAuth()
  const [cart, setCart] = useState(null)
  const [items, setItems] = useState([])
  const [productMap, setProductMap] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updatingId, setUpdatingId] = useState(null)

  // State cho việc hiển thị form thanh toán đơn hàng
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const [checkoutState, setCheckoutState] = useState({ loading: false, message: '' })
  const [checkoutForm, setCheckoutForm] = useState({
    shipping_address: '',
    shipping_phone: '',
    shipping_city: '',
    note: '',
    pay_method: 'COD',
    ship_method: 'STANDARD',
  })

  useEffect(() => {
    let mounted = true

    async function loadCart(){
      setLoading(true)
      try{
        if(!ready || !isAuthenticated || !user?.id){
          setCart(null)
          setItems([])
          setProductMap({})
          return
        }

        const cartData = await api.request(`/carts/customer/${user.id}/`, {}, getCartApiOrigin())
        if(!mounted) return
        setCart(cartData)

        const cartItems = await api.request(`/carts/${user.id}/`, {}, getCartApiOrigin())
        if(!mounted) return
        setItems(Array.isArray(cartItems) ? cartItems : [])

        const uniqueProductIds = [...new Set((Array.isArray(cartItems) ? cartItems : []).map((item) => item.product_id))]
        const productEntries = await Promise.all(uniqueProductIds.map(async (productId) => {
          const product = await api.request(`/products/${productId}/`, {}, getApiOrigin())
          return [productId, product]
        }))
        if(!mounted) return
        setProductMap(Object.fromEntries(productEntries))
      }catch(err){
        if(!mounted) return
        setError(err.message || String(err))
      }finally{
        if(mounted) setLoading(false)
      }
    }

    loadCart()
    return () => { mounted = false }
  }, [ready, isAuthenticated, user?.id])

  const subtotal = useMemo(() => {
    return items.reduce((sum, item) => {
      const unitPrice = Number(item.unit_price || 0)
      return sum + unitPrice * Number(item.quantity || 0)
    }, 0)
  }, [items])

  const shipping = subtotal > 0 ? (subtotal >= 149000 ? 0 : 22000) : 0
  const discount = subtotal >= 500000 ? Math.round(subtotal * 0.05) : 0
  const total = Math.max(0, subtotal + shipping - discount)

  async function updateQuantity(itemId, nextQuantity){
    if(nextQuantity <= 0) return
    setUpdatingId(itemId)
    try{
      await api.request(`/cart-items/${itemId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity: nextQuantity }),
      }, getCartApiOrigin())
      setItems((current) => current.map((item) => item.id === itemId ? { ...item, quantity: nextQuantity } : item))
    }catch(err){
      setError(err.message || String(err))
    }finally{
      setUpdatingId(null)
    }
  }

  async function removeItem(itemId){
    setUpdatingId(itemId)
    try{
      await api.request(`/cart-items/${itemId}/`, {
        method: 'DELETE'
      }, getCartApiOrigin())
      setItems((current) => current.filter((item) => item.id !== itemId))
    }catch(err){
      setError(err.message || String(err))
    }finally{
      setUpdatingId(null)
    }
  }

  // Mở form thanh toán và điền sẵn số điện thoại user
  function openCheckout(){
    setCheckoutForm({
      shipping_address: '',
      shipping_phone: user?.phone || '',
      shipping_city: '',
      note: '',
      pay_method: 'COD',
      ship_method: 'STANDARD',
    })
    setCheckoutState({ loading: false, message: '' })
    setCheckoutOpen(true)
  }

  function handleCheckoutChange(event){
    const { name, value } = event.target
    setCheckoutForm((current) => ({ ...current, [name]: value }))
  }

  // Gửi thông tin thanh toán đơn hàng từ Giỏ hàng
  async function submitCheckout(event){
    event.preventDefault()
    if(!items.length || !user?.id) return

    const shippingAddress = checkoutForm.shipping_address.trim()
    const shippingPhone = checkoutForm.shipping_phone.trim()
    const shippingCity = checkoutForm.shipping_city.trim()

    if(!shippingAddress || !shippingPhone || !shippingCity){
      setCheckoutState({ loading: false, message: 'Vui lòng điền đầy đủ SĐT, Thành phố và Địa chỉ.' })
      return
    }

    setCheckoutState({ loading: true, message: 'Đang tiến hành đặt hàng...' })

    try {
      // Gọi API Gateway để tạo đơn hàng lớn cho cả giỏ hàng 
      // (Hệ thống microservices nhận danh sách items hoặc tạo dựa trên item đầu tiên/tổng hợp tùy thuộc spec backend)
      const createdOrder = await api.request('/order/orders/', {
        method: 'POST',
        body: JSON.stringify({
          customer_id: user.id,
          total_amount: total.toFixed(2),
          pay_method: checkoutForm.pay_method,
          ship_method: checkoutForm.ship_method,
          shipping_address: shippingAddress,
          shipping_phone: shippingPhone,
          shipping_city: shippingCity,
          note: checkoutForm.note.trim(),
          // Gửi thông tin các mặt hàng để Backend xử lý
          items: items.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity,
            unit_price: Number(item.unit_price).toFixed(2),
            title: productMap[item.product_id]?.name || ''
          }))
        }),
      }, getGatewayApiOrigin())

      // Xóa sạch giỏ hàng cục bộ sau khi đã đặt hàng thành công
      // (Hoặc backend tự động clear giỏ hàng khi có đơn từ cart)
      try {
        await Promise.all(items.map(item => 
          api.request(`/cart-items/${item.id}/`, { method: 'DELETE' }, getCartApiOrigin())
        ))
      } catch(e) {
        console.error("Lỗi khi clear giỏ hàng:", e)
      }

      setCheckoutOpen(false)
      navigate('/profile/orders', {
        state: {
          successMessage: `Đã đặt đơn hàng giỏ hàng thành công!`,
        },
      })
    } catch(err) {
      setCheckoutState({ loading: false, message: err.message || String(err) })
    }
  }

  if(loading){
    return <div className="page-wrap"><div className="section-card" style={{padding:24}}>Đang tải giỏ hàng...</div></div>
  }

  if(!isAuthenticated || !user?.id){
    return (
      <div className="page-wrap">
        <div className="section-card cart-shell">
          <span className="hero-kicker">Cần đăng nhập</span>
          <h1>Giỏ hàng gắn theo từng tài khoản</h1>
          <p>Vui lòng đăng nhập để xem giỏ hàng riêng của bạn.</p>
          <Link className="btn btn-primary" to="/login">Đi tới đăng nhập</Link>
        </div>
      </div>
    )
  }

  if(error && !cart){
    return (
      <div className="page-wrap">
        <div className="section-card cart-shell">
          <p style={{color:'crimson'}}>Không tải được giỏ hàng: {error}</p>
          <Link className="see-more" to="/">← Quay lại mua sắm</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page-wrap">
      <section className="section-card cart-shell">
        <div className="cart-header">
          <div>
            <span className="hero-kicker">Giỏ hàng của bạn</span>
            <h1>Thanh toán gọn hơn, theo kiểu marketplace lớn</h1>
            <p>Giỏ đang gắn với tài khoản #{user.id}. Bạn có thể tăng giảm số lượng, xóa sản phẩm và xem tổng tiền ngay.</p>
          </div>
          <Link className="btn btn-secondary" to="/">Tiếp tục mua sắm</Link>
        </div>

        <div className="cart-grid">
          <div className="cart-items-panel">
            <div className="cart-panel-head">
              <h2>Sản phẩm trong giỏ</h2>
              <span>{items.length} mục</span>
            </div>

            {items.length ? items.map((item) => {
              const product = productMap[item.product_id] || {}
              return (
                <article key={item.id} className="cart-item-card">
                  <div className="cart-item-thumb">{product.icon || '📦'}</div>
                  <div className="cart-item-copy">
                    <div className="cart-item-topline">
                      <div>
                        <Link to={`/products/${item.product_id}`} className="cart-item-title">{product.name || `Sản phẩm #${item.product_id}`}</Link>
                        <p>{product.category_detail?.name || 'Danh mục'}</p>
                      </div>
                      <button className="cart-remove" type="button" onClick={() => removeItem(item.id)} disabled={updatingId === item.id}>Xóa</button>
                    </div>

                    <div className="cart-item-bottom">
                      <div className="cart-qty">
                        <button type="button" onClick={() => updateQuantity(item.id, Number(item.quantity) - 1)} disabled={updatingId === item.id}>−</button>
                        <strong>{item.quantity}</strong>
                        <button type="button" onClick={() => updateQuantity(item.id, Number(item.quantity) + 1)} disabled={updatingId === item.id}>+</button>
                      </div>
                      <div className="cart-item-price">
                        <span>{formatMoney(item.unit_price)}</span>
                        <small>Tổng {formatMoney(Number(item.unit_price || 0) * Number(item.quantity || 0))}</small>
                      </div>
                    </div>
                  </div>
                </article>
              )
            }) : (
              <div className="cart-empty">
                <div className="cart-empty-art">🛒</div>
                <h3>Giỏ hàng đang trống</h3>
                <p>Hãy quay lại Home hoặc trang chi tiết sản phẩm để thêm món đầu tiên.</p>
                <Link className="btn btn-primary" to="/">Xem sản phẩm</Link>
              </div>
            )}
          </div>

          <aside className="cart-summary-panel">
            <h2>Thanh toán</h2>
            <div className="summary-row"><span>Tạm tính</span><strong>{formatMoney(subtotal)}</strong></div>
            <div className="summary-row"><span>Phí ship</span><strong>{shipping ? formatMoney(shipping) : 'Miễn phí'}</strong></div>
            <div className="summary-row"><span>Giảm giá</span><strong>- {formatMoney(discount)}</strong></div>
            <div className="summary-total"><span>Tổng cộng</span><strong>{formatMoney(total)}</strong></div>
            <button className="btn btn-primary cart-checkout" type="button" onClick={openCheckout} disabled={!items.length}>
              Tiến hành thanh toán
            </button>
            <div className="summary-note">
              <strong>Ưu đãi hiện tại</strong>
              <p>Đơn từ 149k được miễn ship. Đơn lớn hơn 500k giảm thêm 5%.</p>
            </div>
          </aside>
        </div>
      </section>

      {/* Modal form thông tin giao hàng khi nhấn Tiến hành thanh toán từ giỏ */}
      {checkoutOpen ? (
        <div className="buy-now-backdrop" role="presentation" onClick={() => setCheckoutOpen(false)}>
          <div className="buy-now-modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <div className="buy-now-header">
              <div>
                <span className="hero-kicker">Thanh toán</span>
                <h2>Thông tin giao hàng</h2>
                <p>Xác nhận địa chỉ để xử lý toàn bộ giỏ hàng của bạn.</p>
              </div>
              <button className="buy-now-close" type="button" onClick={() => setCheckoutOpen(false)}>×</button>
            </div>

            <form className="buy-now-form" onSubmit={submitCheckout}>
              <div className="buy-now-summary">
                <div><span>Tổng số món</span><strong>{items.length} món</strong></div>
                <div><span>Tổng thanh toán</span><strong>{formatMoney(total)}</strong></div>
              </div>

              <div className="buy-now-grid">
                <label>
                  <span>Số điện thoại</span>
                  <input name="shipping_phone" value={checkoutForm.shipping_phone} onChange={handleCheckoutChange} placeholder="Ví dụ: 0912345678" />
                </label>
                <label>
                  <span>Thành phố</span>
                  <input name="shipping_city" value={checkoutForm.shipping_city} onChange={handleCheckoutChange} placeholder="Ví dụ: Hà Nội" />
                </label>
                <label className="buy-now-full">
                  <span>Địa chỉ nhận hàng</span>
                  <input name="shipping_address" value={checkoutForm.shipping_address} onChange={handleCheckoutChange} placeholder="Số nhà, đường, phường/xã..." />
                </label>
                <label>
                  <span>Thanh toán</span>
                  <select name="pay_method" value={checkoutForm.pay_method} onChange={handleCheckoutChange}>
                    <option value="COD">COD</option>
                    <option value="CARD">CARD</option>
                    <option value="BANK">BANK</option>
                  </select>
                </label>
                <label>
                  <span>Vận chuyển</span>
                  <select name="ship_method" value={checkoutForm.ship_method} onChange={handleCheckoutChange}>
                    <option value="STANDARD">STANDARD</option>
                    <option value="FAST">FAST</option>
                    <option value="EXPRESS">EXPRESS</option>
                  </select>
                </label>
                <label className="buy-now-full">
                  <span>Ghi chú</span>
                  <textarea name="note" rows="2" value={checkoutForm.note} onChange={handleCheckoutChange} placeholder="Ghi chú thêm cho shipper..." />
                </label>
              </div>

              {checkoutState.message ? <p className="detail-feedback">{checkoutState.message}</p> : null}

              <div className="buy-now-actions">
                <button className="btn btn-secondary" type="button" onClick={() => setCheckoutOpen(false)}>Hủy</button>
                <button className="btn btn-primary" type="submit" disabled={checkoutState.loading}>
                  {checkoutState.loading ? 'Đang tạo đơn...' : 'Xác nhận đặt hàng'}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  )
}