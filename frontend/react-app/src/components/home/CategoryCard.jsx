import React from 'react'

export default function CategoryCard({ icon, title, description, active = false, onClick }){
  return (
    <button
      type="button"
      className={`category-pill ${active ? 'is-active' : ''}`}
      onClick={onClick}
    >
      <div className="category-icon">{icon}</div>
      <div>
        <b>{title}</b>
        <span>{description}</span>
      </div>
    </button>
  )
}