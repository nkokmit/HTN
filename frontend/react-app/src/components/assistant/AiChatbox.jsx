import React, { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../services/api'

const QUICK_PROMPTS = [
  'Gợi ý sản phẩm điện tử',
  'Tìm quà tặng giá tốt',
  'Sản phẩm gia dụng bán chạy',
  'Món nào hợp cho trẻ em?',
]

const STOP_WORDS = new Set([
  'cho', 'giup', 'giúp', 'toi', 'tôi', 'mình', 'muốn', 'can', 'cần', 'tim', 'tìm', 'san', 'sản', 'pham', 'phẩm',
  'nhung', 'những', 'loai', 'loại', 'theo', 'và', 'va', 'la', 'là', 'một', 'mot', 'nhé', 'nhe', 'giá', 're', 'rẻ', 'hot', 'bán', 'chạy'
])

const CATEGORY_HINTS = [
  {
    name: 'Electronics',
    aliases: ['dien tu', 'dien thoai', 'laptop', 'may tinh', 'tai nghe', 'camera', 'loa', 'sac nhanh', 'smartwatch', 'phu kien'],
  },
  {
    name: 'Books',
    aliases: ['sach', 'doc sach', 'lap trinh', 'ebook', 'kien thuc', 'giao trinh'],
  },
  {
    name: 'Fashion',
    aliases: ['thoi trang', 'ao', 'quan', 'vay', 'sneaker', 'giay', 'do mac', 'outfit'],
  },
  {
    name: 'Home',
    aliases: ['gia dung', 'nha cua', 'noi that', 'dung cu', 'be bep', 'may xay', 'noi', 'chan goi', 'dien gia dung'],
  },
  {
    name: 'Toys',
    aliases: ['do choi', 'tre em', 'bup be', 'xe dieu khien', 'xep hinh', 'lego', 'do choi tre em'],
  },
  {
    name: 'Health',
    aliases: ['suc khoe', 'y te', 'vitamin', 'cham soc da', 'ban chai', 'suc khoe gia dinh'],
  },
]

function normalizeText(value){
  return String(value || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

function tokenize(value){
  return normalizeText(value)
    .split(/[^a-z0-9]+/)
    .map((word) => word.trim())
    .filter((word) => word && !STOP_WORDS.has(word))
}

function productLabel(product){
  return product?.name || product?.title || 'Sản phẩm'
}

function buildSearchSuggestions(query, products){
  const baseTokens = tokenize(query)
  const categoryNames = [...new Set(products.map((product) => product.category_detail?.name).filter(Boolean))]
  const matchedCategory = detectCategoryHint(query)

  const suggestions = []
  if(baseTokens.length){
    suggestions.push(baseTokens.slice(0, 3).join(' '))
  }

  if(matchedCategory){
    suggestions.push(`tìm ${normalizeText(matchedCategory.name)}`)
    suggestions.push(`sản phẩm ${normalizeText(matchedCategory.name)}`)
  }

  categoryNames.slice(0, 3).forEach((category) => suggestions.push(`tìm ${normalizeText(category)}`))
  suggestions.push('sản phẩm bán chạy')
  suggestions.push('giảm giá hôm nay')
  suggestions.push('quà tặng')

  return [...new Set(suggestions)].slice(0, 5)
}

function detectCategoryHint(query){
  const normalizedQuery = normalizeText(query)
  return CATEGORY_HINTS.find((hint) => hint.aliases.some((alias) => normalizedQuery.includes(alias))) || null
}

function matchesCategoryHint(product, hint){
  if(!hint) return true
  const categoryName = normalizeText(product.category_detail?.name)
  const productType = normalizeText(product.product_type)
  const hintName = normalizeText(hint.name)
  return categoryName === hintName || productType === hintName
}

function scoreProduct(product, queryTokens){
  if(!queryTokens.length) return 0
  const queryNormalized = normalizeText(queryTokens.join(' '))
  const fields = [
    productLabel(product),
    product.description,
    product.category_detail?.name,
    product.product_type,
  ]
    .filter(Boolean)
    .map(normalizeText)

  let score = 0

  const categoryName = normalizeText(product.category_detail?.name)
  const categoryType = normalizeText(product.product_type)
  const matchedCategory = CATEGORY_HINTS.find((hint) =>
    hint.aliases.some((alias) => queryNormalized.includes(alias)) && (
      normalizeText(hint.name) === categoryName || normalizeText(hint.name) === categoryType
    )
  )

  if(matchedCategory){
    score += 20
  }

  queryTokens.forEach((token) => {
    fields.forEach((field) => {
      if(field.includes(token)) score += field === normalizeText(productLabel(product)) ? 5 : 2
    })
  })

  CATEGORY_HINTS.forEach((hint) => {
    const categoryMatch = hint.aliases.some((alias) => queryNormalized.includes(alias))
    if(categoryMatch){
      const productCategoryMatched = normalizeText(hint.name) === categoryName || normalizeText(hint.name) === categoryType
      if(productCategoryMatched) score += 10
    }
  })

  return score
}

function fallbackRecommendations(products){
  return [...products]
    .sort((left, right) => Number(right.sold || 0) - Number(left.sold || 0))
    .slice(0, 4)
}

export default function AiChatbox(){
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [products, setProducts] = useState([])
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      text: 'Tôi có thể gợi ý sản phẩm trong hệ thống và đề xuất từ khóa tìm kiếm. Hãy hỏi kiểu: “tìm laptop giá tốt” hoặc “gợi ý quà tặng”.',
      products: [],
      suggestions: [],
    },
  ])

  useEffect(() => {
    let active = true

    async function loadProducts(){
      try{
        const result = await api.request('/products')
        const list = Array.isArray(result) ? result : (result.results || result.data || [])
        if(!active) return
        setProducts(list)
      }catch{
        if(active) setProducts([])
      }finally{
        if(active) setLoading(false)
      }
    }

    loadProducts()
    return () => { active = false }
  }, [])

  const recentProducts = useMemo(() => fallbackRecommendations(products).slice(0, 3), [products])

  function respondToQuery(queryText){
    const queryTokens = tokenize(queryText)
    const queryNormalized = normalizeText(queryText)
    const matchedHint = detectCategoryHint(queryText)
    const candidateProducts = matchedHint ? products.filter((product) => matchesCategoryHint(product, matchedHint)) : products
    const ranked = [...candidateProducts]
      .map((product) => ({ product, score: scoreProduct(product, queryTokens) }))
      .filter((item) => item.score > 0)
      .sort((left, right) => right.score - left.score)
      .slice(0, 4)
      .map((item) => item.product)

    const suggestions = buildSearchSuggestions(queryText, products)
    const resultProducts = ranked.length ? ranked : fallbackRecommendations(products).slice(0, 4)

    const categoryHit = resultProducts[0]?.category_detail?.name
    let text = 'Tôi đã lọc một số lựa chọn phù hợp từ catalog hiện tại.'
    if(queryNormalized.includes('giá') || queryNormalized.includes('rẻ')){
      text = 'Tôi ưu tiên các món có vẻ phù hợp để so giá và mua nhanh.'
    }else if(queryNormalized.includes('quà')){
      text = 'Tôi gợi ý vài món dễ mua làm quà, ưu tiên sản phẩm nhìn nổi bật và dễ chọn.'
    }else if(matchedHint){
      text = `Tôi tìm được vài sản phẩm thuộc nhóm ${matchedHint.name}.`
    }else if(categoryHit){
      text = `Tôi tìm được vài sản phẩm thuộc nhóm ${categoryHit}.`
    }

    return {
      text,
      products: resultProducts,
      suggestions,
    }
  }

  function sendMessage(value){
    const text = String(value || input).trim()
    if(!text) return

    const assistantResponse = respondToQuery(text)
    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text,
      products: [],
      suggestions: [],
    }
    const botMessage = {
      id: `${Date.now()}-bot`,
      role: 'assistant',
      text: assistantResponse.text,
      products: assistantResponse.products,
      suggestions: assistantResponse.suggestions,
    }

    setMessages((current) => [...current, userMessage, botMessage])
    setInput('')
    setOpen(true)
  }

  function handleSubmit(event){
    event.preventDefault()
    sendMessage(input)
  }

  function handlePromptClick(prompt){
    sendMessage(prompt)
  }

  function insertSuggestion(suggestion){
    setInput(suggestion)
    setOpen(true)
  }

  return (
    <div className={`ai-chatbox ${open ? 'is-open' : ''}`}>
      {open ? (
        <section className="ai-chat-panel" aria-label="AI chat assistant">
          <header className="ai-chat-header">
            <div>
              <span className="hero-kicker">AI Assistant</span>
              <h3>Gợi ý sản phẩm & tìm kiếm</h3>
              <p>Dựa trên catalog thật của hệ thống.</p>
            </div>
            <button type="button" className="ai-chat-close" onClick={() => setOpen(false)} aria-label="Đóng chat box">×</button>
          </header>

          <div className="ai-chat-body">
            {loading ? (
              <div className="ai-chat-loading">Đang nạp catalog để gợi ý...</div>
            ) : null}

            {!loading && messages.length === 1 ? (
              <div className="ai-chat-quick">
                {QUICK_PROMPTS.map((prompt) => (
                  <button key={prompt} type="button" className="ai-chip" onClick={() => handlePromptClick(prompt)}>
                    {prompt}
                  </button>
                ))}
              </div>
            ) : null}

            {messages.map((message) => (
              <article key={message.id} className={`ai-message ${message.role}`}>
                <div className="ai-message-bubble">{message.text}</div>

                {message.role === 'assistant' && message.products.length ? (
                  <div className="ai-product-grid">
                    {message.products.map((product) => (
                      <button
                        key={product.id}
                        type="button"
                        className="ai-product-card"
                        onClick={() => navigate(`/products/${product.id}`)}
                      >
                        <div className="ai-product-icon">{product.icon || '📦'}</div>
                        <div className="ai-product-copy">
                          <strong>{productLabel(product)}</strong>
                          <span>{product.price_display || `${Math.round(Number(product.price || 0))}đ`}</span>
                          <small>{product.category_detail?.name || 'Danh mục'}</small>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : null}

                {message.role === 'assistant' && message.suggestions.length ? (
                  <div className="ai-suggestions-row">
                    {message.suggestions.map((suggestion) => (
                      <button key={suggestion} type="button" className="ai-suggestion" onClick={() => insertSuggestion(suggestion)}>
                        {suggestion}
                      </button>
                    ))}
                  </div>
                ) : null}
              </article>
            ))}
          </div>

          <footer className="ai-chat-footer">
            <form className="ai-chat-form" onSubmit={handleSubmit}>
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Nhập nhu cầu: laptop, quà tặng, đồ gia dụng..."
                aria-label="Nhập câu hỏi cho AI"
              />
              <button type="submit" className="btn btn-primary">Gửi</button>
            </form>
            <div className="ai-chat-footer-actions">
              <Link className="ai-mini-link" to="/">Xem home</Link>
              <button type="button" className="ai-mini-link" onClick={() => setMessages((current) => current.slice(0, 1))}>
                Xóa hội thoại
              </button>
            </div>
          </footer>
        </section>
      ) : null}

      <button type="button" className="ai-chat-launcher" onClick={() => setOpen((current) => !current)} aria-label="Mở AI chat box">
        <span>AI</span>
      </button>

      {!open ? (
        <div className="ai-chat-teaser">
          {recentProducts.map((product) => (
            <button key={product.id} type="button" onClick={() => navigate(`/products/${product.id}`)}>
              <strong>{productLabel(product)}</strong>
              <span>{product.category_detail?.name || 'Danh mục'}</span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
