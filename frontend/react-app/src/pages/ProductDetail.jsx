import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api, { getCartApiOrigin, getGatewayApiOrigin } from '../services/api'
import { useAuth } from '../context/AuthContext'

function formatCurrency(value){
  if(value === null || value === undefined || value === '') return '—'
  const num = Number(value)
  if(Number.isNaN(num)) return `${value}`
  return `${Math.round(num)}đ`
}

function subtypeSections(product){
  return [
    { key: 'book', title: 'Book', value: product.book },
    { key: 'electronics', title: 'Electronics', value: product.electronics },
    { key: 'fashion', title: 'Fashion', value: product.fashion },
    { key: 'home', title: 'Home', value: product.home },
    { key: 'toy', title: 'Toy', value: product.toy },
    { key: 'health', title: 'Health', value: product.health },
  ].filter((section) => section.value)
}

export default function ProductDetail(){
  const navigate = useNavigate()
  const { id } = useParams()
  const { ready, isAuthenticated, user } = useAuth()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [cartState, setCartState] = useState({ loading: false, message: '' })
  const [buyNowOpen, setBuyNowOpen] = useState(false)
  const [buyNowState, setBuyNowState] = useState({ loading: false, message: '' })
  const [buyNowForm, setBuyNowForm] = useState({
    shipping_address: '',
    shipping_phone: '',
    shipping_city: '',
    note: '',
    quantity: 1,
    pay_method: 'COD',
    ship_method: 'STANDARD',
  })

  useEffect(() => {
    let active = true

    async function load(){
      setLoading(true)
      try{
        const result = await api.request(`/products/${id}/`)
        if(!active) return
        setProduct(result)
      }catch(err){
        if(!active) return
        setError(err.message || String(err))
      }finally{
        if(active) setLoading(false)
      }
    }

    load()
    return () => { active = false }
  }, [id])

  async function addToCart(){
    if(!ready || !isAuthenticated || !user?.id){
      navigate('/login', { state: { from: { pathname: `/products/${id}` } } })
      return
    }
    setCartState({ loading: true, message: 'Đang thêm vào giỏ...' })
    try{
      const cart = await api.request(`/carts/customer/${user.id}/`, {}, getCartApiOrigin())
      await api.request('/cart-items/', {
        method: 'POST',
        body: JSON.stringify({ cart: cart.id, product_id: product.id, quantity: 1 }),
      }, getCartApiOrigin())
      setCartState({ loading: false, message: 'Đã thêm vào giỏ hàng' })
    }catch(err){
      setCartState({ loading: false, message: err.message || String(err) })
    }
  }

  function openBuyNow(){
    if(!ready || !isAuthenticated || !user?.id){
      navigate('/login', { state: { from: { pathname: `/products/${id}` } } })
      return
    }

    setBuyNowState({ loading: false, message: '' })
    setBuyNowForm({
      shipping_address: '',
      shipping_phone: user?.phone || '',
      shipping_city: '',
      note: '',
      quantity: 1,
      pay_method: 'COD',
      ship_method: 'STANDARD',
    })
    setBuyNowOpen(true)
  }

  function handleBuyNowChange(event){
    const { name, value } = event.target
    setBuyNowForm((current) => ({
      ...current,
      [name]: name === 'quantity' ? Math.max(1, Number(value || 1)) : value,
    }))
  }

  async function submitBuyNow(event){
    event.preventDefault()

    if(!product || !user?.id){
      return
    }

    const shippingAddress = buyNowForm.shipping_address.trim()
    const shippingPhone = buyNowForm.shipping_phone.trim()
    const shippingCity = buyNowForm.shipping_city.trim()
    const quantity = Math.max(1, Number(buyNowForm.quantity || 1))

    if(!shippingAddress || !shippingPhone || !shippingCity){
      setBuyNowState({ loading: false, message: 'Vui lòng nhập đầy đủ địa chỉ, số điện thoại và thành phố.' })
      return
    }

    setBuyNowState({ loading: true, message: 'Đang tạo đơn hàng...' })

    try{
      const totalAmount = Number(product.price || 0) * quantity
      const createdOrder = await api.request('/order/orders/', {
        method: 'POST',
        body: JSON.stringify({
          customer_id: user.id,
          total_amount: totalAmount.toFixed(2),
          pay_method: buyNowForm.pay_method,
          ship_method: buyNowForm.ship_method,
          shipping_address: shippingAddress,
          shipping_phone: shippingPhone,
          shipping_city: shippingCity,
          note: buyNowForm.note.trim(),
          product_id: product.id,
          product_type: product.category_detail?.name?.toUpperCase?.() || 'BOOK',
          title: product.name,
          quantity,
          unit_price: Number(product.price || 0).toFixed(2),
        }),
      }, getGatewayApiOrigin())

      setBuyNowOpen(false)
      setBuyNowState({ loading: false, message: '' })
      navigate('/profile/orders', {
        state: {
          successMessage: `Đã tạo đơn #${createdOrder?.order?.id || createdOrder?.id || ''} thành công`,
        },
      })
    }catch(err){
      setBuyNowState({ loading: false, message: err.message || String(err) })
    }
  }

  if(loading){
    return <div className="page-wrap"><div className="section-card" style={{padding:24}}>Đang tải chi tiết sản phẩm...</div></div>
  }

  if(error || !product){
    return (
      <div className="page-wrap">
        <div className="section-card product-detail-shell">
          <p style={{color:'crimson'}}>Không tải được chi tiết sản phẩm: {error || 'Không có dữ liệu'}</p>
          <Link className="see-more" to="/">Quay lại trang chủ</Link>
        </div>
      </div>
    )
  }

  const categoryName = product.category_detail?.name || 'Danh mục'
  const details = subtypeSections(product)

  return (
    <div className="page-wrap">
      <div className="section-card product-detail-shell">
        <div className="detail-breadcrumbs">
          <Link to="/">Trang chủ</Link>
          <span>/</span>
          <span>{categoryName}</span>
        </div>

        <div className="product-detail-grid">
          <div className="product-detail-visual">
            <div className="product-detail-art">{product.icon || '📦'}</div>
          </div>

          <div className="product-detail-copy">
            <span className="hero-kicker">{categoryName}</span>
            <h1>{product.name}</h1>
            <p className="detail-description">{product.description || 'Sản phẩm này đã được nạp từ backend và có thể xem chi tiết ngay tại đây.'}</p>

            <div className="detail-price-row">
              <div>
                <span className="detail-label">Giá</span>
                <strong>{product.price_display || formatCurrency(product.price)}</strong>
              </div>
              <div>
                <span className="detail-label">Tồn kho</span>
                <strong>{product.stock ?? '—'}</strong>
              </div>
              <div>
                <span className="detail-label">Đã bán</span>
                <strong>{product.sold ?? '—'}</strong>
              </div>
            </div>

            <div className="detail-actions">
              <button className="btn btn-primary" onClick={addToCart} disabled={cartState.loading}>
                {cartState.loading ? 'Đang thêm...' : 'Thêm vào giỏ'}
              </button>
              <button className="btn btn-secondary" type="button" onClick={openBuyNow}>Mua ngay</button>
            </div>

            {(!ready || !isAuthenticated || !user?.id) ? (
              <p className="detail-feedback">Giỏ hàng sẽ theo từng tài khoản sau khi đăng nhập.</p>
            ) : null}

            {cartState.message ? <p className="detail-feedback">{cartState.message}</p> : null}

            {details.length ? (
              <div className="detail-meta-card">
                <h3>Thông tin chi tiết</h3>
                <div className="detail-sections">
                  {details.map((section) => (
                    <section key={section.key} className="detail-section-block">
                      <h4>{section.title}</h4>
                      <dl className="detail-specs">
                        {Object.entries(section.value).map(([key, value]) => (
                          <React.Fragment key={key}>
                            <dt>{key}</dt>
                            <dd>{String(value)}</dd>
                          </React.Fragment>
                        ))}
                      </dl>
                    </section>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {buyNowOpen ? (
          <div className="buy-now-backdrop" role="presentation" onClick={() => setBuyNowOpen(false)}>
            <div className="buy-now-modal" role="dialog" aria-modal="true" aria-labelledby="buy-now-title" onClick={(event) => event.stopPropagation()}>
              <div className="buy-now-header">
                <div>
                  <span className="hero-kicker">Mua ngay</span>
                  <h2 id="buy-now-title">Hoàn tất đơn hàng</h2>
                  <p>Nhập địa chỉ giao hàng để tạo đơn trực tiếp từ trang sản phẩm.</p>
                </div>
                <button className="buy-now-close" type="button" onClick={() => setBuyNowOpen(false)} aria-label="Đóng">×</button>
              </div>

              <form className="buy-now-form" onSubmit={submitBuyNow}>
                <div className="buy-now-summary">
                  <div>
                    <span>Sản phẩm</span>
                    <strong>{product.name}</strong>
                  </div>
                  <div>
                    <span>Đơn giá</span>
                    <strong>{product.price_display || formatCurrency(product.price)}</strong>
                  </div>
                  <div>
                    <span>Tạm tính</span>
                    <strong>{formatCurrency(Number(product.price || 0) * Number(buyNowForm.quantity || 1))}</strong>
                  </div>
                </div>

                <div className="buy-now-grid">
                  <label>
                    <span>Số điện thoại</span>
                    <input name="shipping_phone" value={buyNowForm.shipping_phone} onChange={handleBuyNowChange} placeholder="Ví dụ: 0912345678" />
                  </label>
                  <label>
                    <span>Thành phố</span>
                    <input name="shipping_city" value={buyNowForm.shipping_city} onChange={handleBuyNowChange} placeholder="Ví dụ: Hà Nội" />
                  </label>
                  <label className="buy-now-full">
                    <span>Địa chỉ nhận hàng</span>
                    <input name="shipping_address" value={buyNowForm.shipping_address} onChange={handleBuyNowChange} placeholder="Số nhà, đường, phường/xã, quận/huyện" />
                  </label>
                  <label>
                    <span>Số lượng</span>
                    <input name="quantity" type="number" min="1" value={buyNowForm.quantity} onChange={handleBuyNowChange} />
                  </label>
                  <label>
                    <span>Thanh toán</span>
                    <select name="pay_method" value={buyNowForm.pay_method} onChange={handleBuyNowChange}>
                      <option value="COD">COD</option>
                      <option value="CARD">CARD</option>
                      <option value="BANK">BANK</option>
                    </select>
                  </label>
                  <label>
                    <span>Vận chuyển</span>
                    <select name="ship_method" value={buyNowForm.ship_method} onChange={handleBuyNowChange}>
                      <option value="STANDARD">STANDARD</option>
                      <option value="FAST">FAST</option>
                      <option value="EXPRESS">EXPRESS</option>
                    </select>
                  </label>
                  <label className="buy-now-full">
                    <span>Ghi chú</span>
                    <textarea name="note" rows="3" value={buyNowForm.note} onChange={handleBuyNowChange} placeholder="Ví dụ: gọi trước khi giao" />
                  </label>
                </div>

                {buyNowState.message ? <p className="detail-feedback">{buyNowState.message}</p> : null}

                <div className="buy-now-actions">
                  <button className="btn btn-secondary" type="button" onClick={() => setBuyNowOpen(false)}>Hủy</button>
                  <button className="btn btn-primary" type="submit" disabled={buyNowState.loading}>
                    {buyNowState.loading ? 'Đang tạo đơn...' : 'Tạo đơn ngay'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
