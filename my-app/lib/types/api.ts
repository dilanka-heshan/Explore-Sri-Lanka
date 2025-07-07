export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
  pagination?: PaginationInfo
  meta?: {
    total: number
    count: number
    timestamp: string
  }
}

export interface ApiError {
  message: string
  code?: string | number
  details?: any
  timestamp?: string
  path?: string
}

export interface PaginationInfo {
  page: number
  limit: number
  total: number
  totalPages: number
  hasNextPage: boolean
  hasPrevPage: boolean
}

export interface PaginationParams {
  page?: number
  limit?: number
}

export interface SearchParams extends PaginationParams {
  query?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, any>
}

export interface RequestConfig {
  timeout?: number
  retries?: number
  cache?: boolean
  headers?: Record<string, string>
}
