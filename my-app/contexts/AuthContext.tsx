/**
 * User Authentication Context for Frontend
 */
"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface User {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  phone?: string
  nationality?: string
  location?: string
  bio?: string
  role: 'user' | 'admin' | 'moderator'
  email_verified: boolean
  is_active: boolean
  created_at: string
  updated_at?: string
  last_login?: string
  total_reviews?: number
  total_bookings?: number
  favorite_destinations?: string[]
  travel_preferences?: {
    interests: string[]
    preferred_destinations: string[]
    travel_style?: 'solo' | 'couple' | 'family' | 'group'
    budget_level: 'budget' | 'mid_range' | 'luxury'
    adventure_level: number
    accessibility_needs?: string
    dietary_restrictions: string[]
    accommodation_preferences: string[]
    transportation_preferences: string[]
    activity_preferences: string[]
  }
}

export interface AuthToken {
  access_token: string
  token_type: string
  expires_in: number
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  full_name: string
  password: string
  confirm_password: string
  phone?: string
  nationality?: string
  location?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
  updatePassword: (currentPassword: string, newPassword: string, confirmPassword: string) => Promise<void>
  saveDestination: (destinationId: string) => Promise<void>
  unsaveDestination: (destinationId: string) => Promise<void>
  getSavedDestinations: () => Promise<string[]>
  refreshToken: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  // Ensure we're mounted on client before accessing localStorage
  useEffect(() => {
    setMounted(true)
  }, [])

  // Initialize auth state from localStorage - only on client
  useEffect(() => {
    if (!mounted) return

    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('authToken')
        const storedUser = localStorage.getItem('user')

        if (storedToken && storedUser) {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          
          // Verify token and refresh user data
          await fetchUserProfile(storedToken)
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        // Clear invalid data
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [mounted])

  const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
    const url = `${API_BASE_URL}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  const fetchUserProfile = async (authToken?: string) => {
    try {
      const currentToken = authToken || token
      if (!currentToken) return

      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${currentToken}`,
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/me`, { headers })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
      } else {
        // Token is invalid, clear auth state
        logout()
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
    }
  }

  const login = async (credentials: LoginCredentials) => {
    try {
      setLoading(true)
      const response = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      })

      const { user: userData, token: tokenData } = response
      
      setUser(userData)
      setToken(tokenData.access_token)
      
      // Store in localStorage
      localStorage.setItem('authToken', tokenData.access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (data: RegisterData) => {
    try {
      setLoading(true)
      const response = await apiRequest('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      })

      // After successful registration, you might want to auto-login
      // or redirect to a verification page
      console.log('Registration successful:', response)
      
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await apiRequest('/api/auth/me', {
        method: 'PUT',
        body: JSON.stringify(data),
      })

      setUser(response)
      localStorage.setItem('user', JSON.stringify(response))
    } catch (error) {
      console.error('Profile update failed:', error)
      throw error
    }
  }

  const updatePassword = async (currentPassword: string, newPassword: string, confirmPassword: string) => {
    try {
      await apiRequest('/api/auth/me/password', {
        method: 'PUT',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      })
    } catch (error) {
      console.error('Password update failed:', error)
      throw error
    }
  }

  const saveDestination = async (destinationId: string) => {
    try {
      await apiRequest(`/api/auth/me/saved-destinations/${destinationId}`, {
        method: 'POST',
      })
      
      // Update user's favorite destinations
      if (user) {
        const updatedUser = {
          ...user,
          favorite_destinations: [...(user.favorite_destinations || []), destinationId]
        }
        setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
      }
    } catch (error) {
      console.error('Save destination failed:', error)
      throw error
    }
  }

  const unsaveDestination = async (destinationId: string) => {
    try {
      await apiRequest(`/api/auth/me/saved-destinations/${destinationId}`, {
        method: 'DELETE',
      })
      
      // Update user's favorite destinations
      if (user) {
        const updatedUser = {
          ...user,
          favorite_destinations: (user.favorite_destinations || []).filter(id => id !== destinationId)
        }
        setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
      }
    } catch (error) {
      console.error('Unsave destination failed:', error)
      throw error
    }
  }

  const getSavedDestinations = async (): Promise<string[]> => {
    try {
      const response = await apiRequest('/api/auth/me/saved-destinations')
      return response.saved_destinations
    } catch (error) {
      console.error('Get saved destinations failed:', error)
      return []
    }
  }

  const refreshToken = async () => {
    try {
      const response = await apiRequest('/api/auth/refresh-token', {
        method: 'POST',
      })

      setToken(response.access_token)
      localStorage.setItem('authToken', response.access_token)
    } catch (error) {
      console.error('Token refresh failed:', error)
      logout()
    }
  }

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile,
    updatePassword,
    saveDestination,
    unsaveDestination,
    getSavedDestinations,
    refreshToken,
    isAuthenticated: !!user && !!token,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
