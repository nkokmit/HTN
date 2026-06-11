import React, { useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import api, { getGatewayApiOrigin } from '../../services/api'
import { useAuth } from '../../context/AuthContext'

const ORDER_STATUS_META = {
  PAYMENT_AND_SHIPPING_CREATED: { label: 'Đã tạo thanh toán và vận chuyển', tone: 'success' },
  PARTIAL_FAILED: { label: 'Tạo đơn lỗi một phần', tone: 'warning' },
  DEPENDENCY_UNAVAILABLE: { label: 'Đang chờ dịch vụ thanh toán / vận chuyển', tone: 'warning' },
}

const SHIPMENT_STATUS_META = {
  CREATED: { label: 'Mới tạo', tone: 'info', step: 1 },
  PROCESSING: { label: 'Đang xử lý', tone: 'info', step: 2 },
  SHIPPED: { label: 'Đã bàn giao đơn vị vận chuyển', tone: 'success', step: 3 },
  IN_TRANSIT: { label: 'Đang giao', tone: 'success', step: 3 },
  DELIVERED: { label: 'Đã giao', tone: 'success', step: 4 },
  CANCELLED: { label: 'Đã hủy', tone: 'danger', step: 0 },
}

const PROGRESS_STEPS = [
  { key: 'created', label: 'Đã tạo' },
  { key: 'processing', label: 'Xử lý' },
  { key: 'shipping', label: 'Vận chuyển' },
  { key: 'delivered', label: 'Hoàn tất' },
]

function formatMoney(value){
  const num = Number(value)
  if(Number.isNaN(num)) return '0đ'
  return `${new Intl.NumberFormat('vi-VN').format(Math.round(num))}đ`
}

function formatDateTime(value){
  if(!value) return 'Chưa có thời gian'
  const date = new Date(value)
  if(Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

function getStatusMeta(status, map, fallbackTone = 'neutral'){
  const normalized = String(status || '').toUpperCase()
  return map[normalized] || {
    label: status || 'Chưa cập nhật',
    tone: fallbackTone,
  }
}

function getProgressStep(shipmentStatus, orderStatus){
  const normalizedShipment = String(shipmentStatus || '').toUpperCase()
  const normalizedOrder = String(orderStatus || '').toUpperCase()

  if(normalizedOrder === 'PARTIAL_FAILED' || normalizedOrder === 'DEPENDENCY_UNAVAILABLE'){
    return 0
  }

  if(normalizedShipment === 'DELIVERED') return 4
  if(normalizedShipment === 'IN_TRANSIT' || normalizedShipment === 'SHIPPED') return 3
  if(normalizedShipment === 'PROCESSING') return 2
  return 1
}

function OrderProgress({ step }){
  return (
    <div className="order-progress" aria-label="Tiến trình đơn hàng">
      <div className="order-progress-track" aria-hidden="true">
        {PROGRESS_STEPS.map((item, index) => (
          <span
            key={item.key}
            className={`order-progress-step ${step >= index + 1 ? 'is-active' : ''}`}
          />
        ))}
      </div>
      <div className="order-progress-labels">
        {PROGRESS_STEPS.map((item, index) => (
          <span key={item.key} className={step >= index + 1 ? 'is-active' : ''}>
            {item.label}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function ProfileOrdersPage(){
  const { ready, isAuthenticated, user } = useAuth()
  const location = useLocation()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadOrders(){
      try{
        setLoading(true)
        setError('')

        if(!ready || !isAuthenticated || !user?.id){
          if(mounted) setOrders([])
          return
        }

        const gatewayOrigin = getGatewayApiOrigin()
        const orderList = await api.request(`/order/orders/?customer_id=${user.id}`, {}, gatewayOrigin)
        const baseOrders = Array.isArray(orderList) ? orderList : []

        const enrichedOrders = await Promise.all(baseOrders.map(async (order) => {
          try{
            const shipment = await api.request(`/ship/shipments/order/${order.id}/`, {}, gatewayOrigin)
            return { ...order, shipment }
          }catch(shipmentError){
            if(shipmentError?.status === 404){
              return { ...order, shipment: null }
            }
            return { ...order, shipmentError: shipmentError.message || String(shipmentError) }
          }
        }))

        if(mounted) setOrders(enrichedOrders)
      }catch(fetchError){
        if(mounted) setError(fetchError.message || String(fetchError))
      }finally{
        if(mounted) setLoading(false)
      }
    }

    loadOrders()
    return () => { mounted = false }
  }, [ready, isAuthenticated, user?.id])

  const stats = useMemo(() => {
    const total = orders.length
    const delivered = orders.filter((order) => String(order.shipment?.status || '').toUpperCase() === 'DELIVERED').length
    const shipping = orders.filter((order) => ['CREATED', 'PROCESSING', 'SHIPPED', 'IN_TRANSIT'].includes(String(order.shipment?.status || '').toUpperCase())).length
    const failed = orders.filter((order) => ['PARTIAL_FAILED', 'DEPENDENCY_UNAVAILABLE'].includes(String(order.status || '').toUpperCase())).length

    return { total, delivered, shipping, failed }
  }, [orders])

  const successMessage = location.state?.successMessage

  if(loading){
    return <div className="profile-content">Đang tải đơn hàng...</div>
  }

  if(!isAuthenticated || !user?.id){
    return (
      <div className="profile-content profile-orders-empty">
        <span className="hero-kicker">Cần đăng nhập</span>
        <h2>Đơn hàng của bạn</h2>
        <p>Đăng nhập để xem trạng thái xử lý và vận chuyển của từng đơn hàng.</p>
        <Link className="btn btn-primary" to="/login">Đi tới đăng nhập</Link>
      </div>
    )
  }

  if(error && !orders.length){
    return (
      <div className="profile-content profile-orders-empty">
        <span className="hero-kicker">Không thể tải đơn hàng</span>
        <h2>Đã có lỗi khi lấy dữ liệu</h2>
        <p>{error}</p>
        <Link className="btn btn-secondary" to="/profile">Thử lại sau</Link>
      </div>
    )
  }

  if(!orders.length){
    return (
      <div className="profile-content profile-orders-empty">
        <span className="hero-kicker">Đơn hàng</span>
        <h2>Chưa có đơn nào</h2>
        <p>Khi bạn đặt hàng, mình sẽ hiển thị trạng thái đơn và tiến trình giao hàng ở đây.</p>
        <Link className="btn btn-primary" to="/">Bắt đầu mua sắm</Link>
      </div>
    )
  }

  return (
    <div className="profile-orders">
      {successMessage ? <div className="profile-alert">{successMessage}</div> : null}
      <div className="profile-orders-hero">
        <div>
          <span className="hero-kicker">Theo dõi đơn hàng</span>
          <h2>Trạng thái thanh toán và vận chuyển</h2>
          <p>Danh sách này lấy trực tiếp từ order-service và ship-service qua API gateway.</p>
        </div>
        <div className="profile-orders-metrics">
          <div className="profile-metric-card">
            <strong>{stats.total}</strong>
            <span>Tổng đơn</span>
          </div>
          <div className="profile-metric-card">
            <strong>{stats.shipping}</strong>
            <span>Đang giao</span>
          </div>
          <div className="profile-metric-card">
            <strong>{stats.delivered}</strong>
            <span>Đã giao</span>
          </div>
          <div className="profile-metric-card">
            <strong>{stats.failed}</strong>
            <span>Đơn lỗi</span>
          </div>
        </div>
      </div>

      <div className="order-list">
        {orders.map((order) => {
          const orderMeta = getStatusMeta(order.status, ORDER_STATUS_META)
          const shipmentMeta = getStatusMeta(order.shipment?.status, SHIPMENT_STATUS_META, 'neutral')
          const progressStep = getProgressStep(order.shipment?.status, order.status)
          const items = Array.isArray(order.items) ? order.items : []
          const visibleItems = items.slice(0, 3)
          const extraItemCount = Math.max(0, items.length - visibleItems.length)

          return (
            <article key={order.id} className="order-card">
              <div className="order-card-head">
                <div>
                  <div className="order-card-title-row">
                    <h3>Đơn #{order.id}</h3>
                    <span className={`order-badge is-${orderMeta.tone}`}>{orderMeta.label}</span>
                  </div>
                  <p className="order-card-subtitle">
                    Đặt lúc {formatDateTime(order.created_at || order.updated_at)}
                  </p>
                </div>

                <div className="order-card-snapshot">
                  <div>
                    <span>Tổng tiền</span>
                    <strong>{formatMoney(order.total_amount)}</strong>
                  </div>
                  <div>
                    <span>Thanh toán</span>
                    <strong>{order.pay_method || '---'}</strong>
                  </div>
                  <div>
                    <span>Vận chuyển</span>
                    <strong>{order.ship_method || '---'}</strong>
                  </div>
                </div>
              </div>

              <div className="order-status-grid">
                <div className="order-status-panel">
                  <span className="order-panel-label">Trạng thái đơn hàng</span>
                  <strong>{orderMeta.label}</strong>
                  <p>{order.status || 'Chưa cập nhật'}</p>
                </div>
                <div className="order-status-panel">
                  <span className="order-panel-label">Trạng thái vận chuyển</span>
                  <strong>{shipmentMeta.label}</strong>
                  {order.shipment?.tracking_number ? (
                    <p>Mã vận đơn: {order.shipment.tracking_number}</p>
                  ) : order.shipmentError ? (
                    <p>{order.shipmentError}</p>
                  ) : (
                    <p>Chưa có mã vận đơn.</p>
                  )}
                </div>
              </div>

              <OrderProgress step={progressStep} />

              <div className="order-detail-grid">
                <div className="order-items-panel">
                  <div className="order-panel-head">
                    <h4>Sản phẩm trong đơn</h4>
                    <span>{items.length} sản phẩm</span>
                  </div>
                  {visibleItems.length ? visibleItems.map((item) => (
                    <div key={item.id || `${order.id}-${item.product_id}`} className="order-item-row">
                      <div>
                        <strong>{item.title || `Sản phẩm #${item.product_id}`}</strong>
                        <p>
                          SL {item.quantity || 1} x {formatMoney(item.unit_price)}
                        </p>
                      </div>
                      <span>{formatMoney(item.subtotal || Number(item.unit_price || 0) * Number(item.quantity || 0))}</span>
                    </div>
                  )) : (
                    <p className="order-muted">Đơn hàng chưa có danh sách sản phẩm.</p>
                  )}
                  {extraItemCount > 0 && (
                    <p className="order-muted">+ {extraItemCount} sản phẩm khác</p>
                  )}
                </div>

                <div className="order-fulfillment-panel">
                  <div className="order-panel-head">
                    <h4>Ghi chú giao hàng</h4>
                    <span>{shipmentMeta.label}</span>
                  </div>
                  <div className="order-fulfillment-list">
                    {PROGRESS_STEPS.map((step, index) => (
                      <div key={step.key} className={`order-fulfillment-item ${progressStep >= index + 1 ? 'is-active' : ''}`}>
                        <strong>{step.label}</strong>
                        <span>{progressStep >= index + 1 ? 'Đã hoàn tất' : 'Đang chờ'}</span>
                      </div>
                    ))}
                  </div>
                  <p className="order-muted">
                    Nếu đơn đã tạo shipment nhưng chưa có tracking number, trạng thái vận chuyển sẽ cập nhật sau khi ship-service hoàn tất.
                  </p>
                </div>
              </div>
            </article>
          )
        })}
      </div>
    </div>
  )
}
