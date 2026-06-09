import React from 'react'
import { Link } from 'react-router-dom'

export default function ProductCard({ id, icon, title, price, sold, badge, category }){
  return (
    <Link className="product-card product-card-clickable" to={`/products/${id}`}>
      <div className="product-image"><span>{icon}</span></div>
      <div>
        <p className="product-title">{title}</p>
        {category ? <p className="product-category">{category}</p> : null}
        <div className="price-row">
          <div className="price">{price}</div>
          <div className="badge">{badge}</div>
        </div>
      </div>
      <div className="meta-row">
        <span>Đã bán {sold}</span>
        <span>★★★★★ 4.9</span>
      </div>
    </Link>
  )
}