import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import api, { getCartApiOrigin, getApiOrigin } from '../services/api'
import { useAuth } from '../context/AuthContext'

function formatMoney(value){
  const num = Number(value)
  if(Number.isNaN(num)) return '0đ'
  return `${Math.round(num)}đ`
}

export default function Cart(){
  const { ready, isAuthenticated, user } = useAuth()
  const [cart, setCart] = useState(null)
  const [items, setItems] = useState([])
  const [productMap, setProductMap] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updatingId, setUpdatingId] = useState(null)

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
            <button className="btn btn-primary cart-checkout" type="button">Tiến hành thanh toán</button>
            <div className="summary-note">
              <strong>Ưu đãi hiện tại</strong>
              <p>Đơn từ 149k được miễn ship. Đơn lớn hơn 500k giảm thêm 5%.</p>
            </div>
          </aside>
        </div>
      </section>
    </div>
  )
}
