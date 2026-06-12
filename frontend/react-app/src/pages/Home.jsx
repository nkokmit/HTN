import React, { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import ProductCard from '../components/home/ProductCard'

export default function Home() {
  const [categories, setCategories] = useState([{ icon: '✨', title: 'Tất cả', description: 'Xem toàn bộ sản phẩm' }])
  const [products, setProducts] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  
  // State cho thanh Live Search
  const [searchQuery, setSearchQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      try {
        // Dùng đúng đường dẫn nguyên bản của bạn
        const pResult = await api.request('/products')
        if (!mounted) return
        const prodList = Array.isArray(pResult) ? pResult : (pResult.results || pResult.data || [])

        // 1. GIỮ NGUYÊN LOGIC CHUẨN HÓA DỮ LIỆU CỦA BẠN
        const normalizedProducts = prodList.map((p) => ({
          id: p.id,
          icon: p.icon || '📦',
          title: p.title || p.name || p.description || 'Sản phẩm',
          price: p.price_display || (p.price ? `${Math.round(Number(p.price))}đ` : '—'),
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

        // 2. GIỮ NGUYÊN LOGIC LỌC DANH MỤC CỦA BẠN
        const derivedCategories = Array.from(
          new Map(
            prodList
              .map((p) => p.category_detail)
              .filter(Boolean)
              .map((category) => [category.name, category])
          ).values()
        )

        if (derivedCategories.length) {
          const mappedCategories = derivedCategories.map((c) => ({
            icon: c.icon || '▣',
            title: c.name || c.title,
            description: c.description || ''
          }))
          setCategories([
            { icon: '✨', title: 'Tất cả', description: 'Xem toàn bộ sản phẩm' },
            ...mappedCategories,
          ])
        }
      } catch (err) {
        console.warn('Failed to load products/categories', err)
        setError(err.message || String(err))
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  // Dữ liệu cho ô Dropdown tìm kiếm thông minh
  const liveResults = useMemo(() => {
    if (!searchQuery.trim()) return []
    const normalizedTerm = searchQuery.trim().toLowerCase()
    return products
      .filter(product => {
        return [product.title, product.category, product.description, product.productType]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(normalizedTerm))
      })
      .slice(0, 5) 
  }, [searchQuery, products])

  // Lọc sản phẩm hiển thị trên lưới theo Danh mục chọn ở cột trái
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      return selectedCategory === 'all' || product.category === selectedCategory
    })
  }, [products, selectedCategory])

  if (loading) {
    return <div className="page-wrap"><div className="section-card" style={{padding: 24}}>Đang tải trang chủ...</div></div>
  }

  return (
    <div className="page-wrap home-container">
      
      {/* 1. CỘT TRÁI: DANH MỤC */}
      <aside className="home-sidebar-left section-card">
        <h3 className="sidebar-title">Danh mục</h3>
        <ul className="category-menu">
          {categories.map((item, idx) => {
            const catValue = item.title === 'Tất cả' ? 'all' : item.title
            const isActive = selectedCategory === catValue
            return (
              <li key={idx} className={isActive ? 'active' : ''}>
                <a 
                  href="#!" 
                  onClick={(e) => {
                    e.preventDefault();
                    setSelectedCategory(catValue);
                  }}
                >
                  <span style={{marginRight: 8}}>{item.icon}</span>
                  {item.title}
                </a>
              </li>
            )
          })}
        </ul>
      </aside>

      {/* 2. CỘT GIỮA: TÌM KIẾM + SẢN PHẨM */}
      <main className="home-main-content">
        
        {/* Ô tìm kiếm Live Search */}
        <div className="live-search-wrapper">
          <input 
            type="text" 
            className="live-search-input"
            placeholder="Tìm theo tên, mô tả, danh mục..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)} 
          />
          
          {showSuggestions && searchQuery && (
            <div className="search-dropdown-overlay">
              {liveResults.length > 0 ? (
                liveResults.map(p => (
                  <Link key={p.id} to={`/products/${p.id}`} className="search-result-item">
                    <div className="search-result-icon">{p.icon}</div>
                    <div className="search-result-info">
                      <h4>{p.title}</h4>
                      <span>{p.price}</span>
                    </div>
                  </Link>
                ))
              ) : (
                <div className="search-no-result">Không tìm thấy "{searchQuery}"</div>
              )}
            </div>
          )}
        </div>

        {/* Lưới sản phẩm đã trả lại cấu trúc props nguyên bản */}
        {error ? (
          <div style={{color:'crimson', padding: 20}}>Lỗi khi tải dữ liệu: {error}</div>
        ) : (
          <div className="home-product-grid">
            {filteredProducts.length > 0 ? (
              filteredProducts.map(item => (
                <ProductCard 
                  key={item.id} 
                  {...item} 
                  onClick={() => navigate(`/products/${item.id}`)} 
                />
              ))
            ) : (
              <div style={{padding: 20, color: '#6b7280'}}>Không có sản phẩm nào trong danh mục này.</div>
            )}
          </div>
        )}
      </main>

      {/* 3. CỘT PHẢI: BANNERS QUẢNG CÁO */}
      <aside className="home-sidebar-right">
        <div className="side-banner banner-1"><span>🔥 Siêu Sale Hè</span></div>
        <div className="side-banner banner-2"><span>🚚 Freeship Từ 149k</span></div>
        <div className="side-banner banner-3"><span>🎁 Quà Tặng 199k</span></div>
      </aside>
      
    </div>
  )
}