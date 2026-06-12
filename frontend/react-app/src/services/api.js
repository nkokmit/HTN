const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || ''
const CART_API_ORIGIN = import.meta.env.VITE_CART_API_ORIGIN || API_ORIGIN
const USER_API_ORIGIN = import.meta.env.VITE_USER_API_ORIGIN || API_ORIGIN
const GATEWAY_API_ORIGIN = import.meta.env.VITE_GATEWAY_API_ORIGIN || API_ORIGIN.replace(/\/product$/, '')

export async function request(path, opts = {}, origin = API_ORIGIN){
  const url = origin + path
  
  // 1. Tự động lấy Token từ localStorage (Đảm bảo key khớp với tên bạn lưu khi đăng nhập thành công)
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')

  // 2. Thiết lập Header, tự động chèn Authorization nếu có Token
  const headers = Object.assign(
    {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}) // Chèn mã Bearer Token để vượt qua lỗi 403
    }, 
    opts.headers || {}
  )

  const res = await fetch(url, Object.assign({}, opts, { headers }))
  if(!res.ok){
    const text = await res.text()
    const err = new Error(res.status + ' ' + res.statusText + ' - ' + text)
    err.status = res.status
    throw err
  }
  const ct = res.headers.get('content-type') || ''
  if(ct.includes('application/json')) return res.json()
  return res.text()
}

export function getApiOrigin(){
  return API_ORIGIN
}

export function getCartApiOrigin(){
  return CART_API_ORIGIN
}

export function getUserApiOrigin(){
  return USER_API_ORIGIN
}

export function getGatewayApiOrigin(){
  return GATEWAY_API_ORIGIN
}

export default { request, getApiOrigin, getCartApiOrigin, getUserApiOrigin, getGatewayApiOrigin }