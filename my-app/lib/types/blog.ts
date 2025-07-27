export interface BlogPost {
  id: string | number
  title: string
  excerpt: string
  content?: string
  image: string
  author: string
  date: string
  publishedAt?: string
  updatedAt?: string
  tags?: string[]
  category?: string
  readTime?: number
  slug?: string
  featured?: boolean
  status?: 'draft' | 'published' | 'archived'
  views?: number
  likes?: number
  comments?: Comment[]
}

export interface Comment {
  id: string | number
  author: string
  email?: string
  content: string
  date: string
  replies?: Comment[]
  approved?: boolean
}

export interface BlogCategory {
  id: string | number
  name: string
  slug: string
  description?: string
  count?: number
}

export interface BlogSearchParams {
  query?: string
  category?: string
  tag?: string
  author?: string
  featured?: boolean
  page?: number
  limit?: number
  sortBy?: 'date' | 'title' | 'views' | 'likes'
  sortOrder?: 'asc' | 'desc'
}
