import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api, { getCartApiOrigin } from '../services/api'
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
              <button className="btn btn-secondary">Mua ngay</button>
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
      </div>
    </div>
  )
}
