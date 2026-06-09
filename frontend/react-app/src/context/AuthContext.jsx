import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AUTH_STORAGE_KEY = 'ecomerence.auth'

const AuthContext = createContext(null)

function readStoredAuth(){
  try{
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if(!raw) return { user: null, token: null }
    const parsed = JSON.parse(raw)
    return {
      user: parsed.user || null,
      token: parsed.token || null,
    }
  }catch{
    return { user: null, token: null }
  }
}

export function AuthProvider({ children }){
  const [auth, setAuth] = useState({ user: null, token: null, ready: false })

  useEffect(() => {
    const stored = readStoredAuth()
    setAuth({ ...stored, ready: true })
  }, [])

  useEffect(() => {
    if(!auth.ready) return
    if(auth.user && auth.token){
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ user: auth.user, token: auth.token }))
    }else{
      localStorage.removeItem(AUTH_STORAGE_KEY)
    }
  }, [auth])

  const value = useMemo(() => ({
    ready: auth.ready,
    user: auth.user,
    token: auth.token,
    isAuthenticated: Boolean(auth.user && auth.token),
    login(user, token){
      setAuth({ user, token, ready: true })
    },
    logout(){
      setAuth({ user: null, token: null, ready: true })
    },
  }), [auth])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(){
  const context = useContext(AuthContext)
  if(!context){
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
