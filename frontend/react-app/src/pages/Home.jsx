import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import CategoryCard from '../components/home/CategoryCard'
import ProductCard from '../components/home/ProductCard'
import api from '../services/api'

const staticCategories = [
  { icon: '📱', title: 'Điện tử', description: 'Săn deal chính hãng' },
  { icon: '👕', title: 'Thời trang', description: 'Phong cách mỗi ngày' },
  { icon: '🏠', title: 'Gia dụng', description: 'Nhà cửa gọn đẹp' },
  { icon: '📚', title: 'Sách', description: 'Đọc là biết ngay' },
  { icon: '🎮', title: 'Giải trí', description: 'Phụ kiện & gaming' },
  { icon: '🍎', title: 'Sức khỏe', description: 'Tiện lợi cho gia đình' }
]

export default function Home(){
  const [categories, setCategories] = useState(staticCategories)
  const [products, setProducts] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(()=>{
    let mounted = true
    async function load(){
      setLoading(true)
      try{
        // Use product-service paths; gateway is proxied under /product when using API gateway
        const pResult = await api.request('/products')
        if(!mounted) return
        const prodList = Array.isArray(pResult) ? pResult : (pResult.results || pResult.data || [])

        const normalizedProducts = prodList.map((p)=>({
          id: p.id,
          icon: p.icon || '📦',
          title: p.title || p.name || p.description || 'Sản phẩm',
          price: p.price_display || (p.price ? `${p.price}đ` : '—'),
          sold: p.sold || p.sold_count || '—',
          badge: p.badge || '',
          category: p.category_detail?.name || '',
          description: p.description || '',
          priceValue: p.price,
          stock: p.stock,
          productType: p.product_type || '',
          raw: p,
        }))

        setProducts(normalizedProducts)

        const derivedCategories = Array.from(
          new Map(
            prodList
              .map((p) => p.category_detail)
              .filter(Boolean)
              .map((category) => [category.name, category])
          ).values()
        )

        if(derivedCategories.length){
          const mappedCategories = derivedCategories.map((c)=>({
            icon: c.icon || '▣',
            title: c.name || c.title,
            description: c.description || ''
          }))
          setCategories([
            { icon: '✨', title: 'Tất cả', description: 'Xem toàn bộ sản phẩm' },
            ...mappedCategories,
          ])
        }
      }catch(err){
        console.warn('Failed to load products/categories', err)
        setError(err.message || String(err))
      }finally{
        if(mounted) setLoading(false)
      }
    }
    load()
    return ()=>{ mounted=false }
  },[])

  const filteredProducts = useMemo(() => {
    const normalizedTerm = searchTerm.trim().toLowerCase()
    return products.filter((product) => {
      const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory
      const matchesSearch = !normalizedTerm || [product.title, product.category, product.description, product.productType]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(normalizedTerm))
      return matchesCategory && matchesSearch
    })
  }, [products, selectedCategory, searchTerm])

  return (
    <div className="page-wrap">
      <section className="hero-grid">
        <div className="hero-card">
          <span className="hero-kicker">Marketplace / Tiki-style layout</span>
          <h1 className="hero-title">Một mặt tiền mua sắm rõ ràng hơn, nhiều danh mục hơn, và vẫn dễ mở rộng tiếp</h1>
          <p className="hero-copy">Giao diện này giờ kết nối tới backend để lấy danh sách sản phẩm và danh mục.</p>
          <div className="hero-search-inline">
            <input
              className="hero-search-input"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Tìm theo tên, mô tả, danh mục..."
              aria-label="Tìm kiếm sản phẩm"
            />
            <button className="btn btn-secondary" type="button" onClick={() => setSearchTerm('')}>
              Xóa tìm kiếm
            </button>
          </div>
          <div className="hero-actions">
            <button className="btn btn-primary">Khám phá deal hôm nay</button>
            <button className="btn btn-secondary">Xem danh mục nổi bật</button>
          </div>
          <div className="hero-stats">
            <div className="metric"><strong>{products.length || '—'}</strong><span>sản phẩm tải được</span></div>
            <div className="metric"><strong>2h</strong><span>giao nhanh nội thành</span></div>
            <div className="metric"><strong>98%</strong><span>đánh giá hài lòng</span></div>
          </div>
        </div>

        <aside className="side-card">
          <div className="mini-banner orange">
            <div>
              <strong>Giảm đến 50%</strong>
              <h3>Thiết bị công nghệ & phụ kiện</h3>
            </div>
            <p>Flash sale giới hạn cho nhóm hàng bán chạy nhất.</p>
          </div>
          <div className="mini-banner blue">
            <div>
              <strong>Miễn phí ship</strong>
              <h3>Đơn từ 149k, áp dụng hàng nghìn shop</h3>
            </div>
            <p>Tăng chuyển đổi với các ưu đãi rõ ràng, dễ nhìn.</p>
          </div>
        </aside>
      </section>

      <section className="section-card">
        <div className="section-head">
          <div>
            <h2>Danh mục nổi bật</h2>
            <p>Gợi ý cách bố cục như giao diện marketplace lớn: dễ scan, dễ click.</p>
          </div>
          <a className="see-more" href="#products">Xem tất cả</a>
        </div>
        <div className="category-row">
          {categories.map((item) => (
            <CategoryCard
              key={item.title}
              {...item}
              active={selectedCategory === (item.title === 'Tất cả' ? 'all' : item.title)}
              onClick={() => setSelectedCategory(item.title === 'Tất cả' ? 'all' : item.title)}
            />
          ))}
        </div>
      </section>

      <section className="promo-card">
        <div>
          <span className="hero-kicker" style={{background:'rgba(255,255,255,.16)',color:'#fff'}}>Deal hot</span>
          <h3>Mua sắm theo chiến dịch, không chỉ theo danh sách sản phẩm</h3>
          <p>
            Khối promo lớn tạo điểm nhấn kiểu Tiki: vừa có ưu đãi, vừa có cảm giác “chợ” mạnh hơn,
            phù hợp để phát triển tiếp các trang home, campaign và landing page sau này.
          </p>
          <div className="promo-points">
            <span className="promo-point">Ưu đãi theo ngày</span>
            <span className="promo-point">Gợi ý theo hành vi</span>
            <span className="promo-point">Bộ lọc nhanh</span>
            <span className="promo-point">Bán chạy theo trend</span>
          </div>
        </div>
        <div className="promo-art">🛍️</div>
      </section>

      <section className="section-card" id="products">
        <div className="section-head">
          <div>
            <h2>Sản phẩm bán chạy</h2>
            <p>
              Grid 4 cột trên desktop, tự co về mobile. {selectedCategory !== 'all' ? `Đang lọc theo ${selectedCategory}.` : 'Đang xem toàn bộ danh mục.'}
            </p>
          </div>
          <a className="see-more" href="/profile">Vào tài khoản</a>
        </div>

        {loading ? (
          <div style={{padding:24}}>Đang tải sản phẩm...</div>
        ) : error ? (
          <div style={{padding:24,color:'crimson'}}>Lỗi khi tải dữ liệu: {error}. Hiện đang hiển thị dữ liệu mẫu.</div>
        ) : (
          <div className="deal-grid">
            {filteredProducts.length ? filteredProducts.map((item)=> (
              <ProductCard
                key={item.id}
                {...item}
                onClick={() => navigate(`/products/${item.id}`)}
              />
            )) : <div>Không có sản phẩm nào trong danh mục này.</div>}
          </div>
        )}

      </section>
    </div>
  )
}