export interface HeroSlide {
  id: number
  image: string
  title: string
  subtitle: string
  cta?: {
    text: string
    link: string
  }
}

export interface SeasonalPick {
  id: number
  title: string
  image: string
  description: string
  season: string
  highlights?: string[]
  bestFor?: string[]
}

export interface SearchFormData {
  destination: string
  experience: string
  date: string
  travelers?: number
}

export interface NavigationItem {
  name: string
  href: string
  icon?: string
  dropdown?: NavigationItem[]
}

export interface SocialLink {
  platform: string
  url: string
  icon: string
}

export interface ContactInfo {
  email: string
  phone: string
  address: string
  hours: string
}

export interface FooterSection {
  title: string
  links: {
    name: string
    href: string
  }[]
}
