"use client"

import { useState, useRef, useEffect } from "react"

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  priority?: boolean
  quality?: number
  placeholder?: "blur" | "empty"
  blurDataURL?: string
  sizes?: string
  fill?: boolean
  objectFit?: "contain" | "cover" | "fill" | "none" | "scale-down"
  onLoad?: () => void
  onError?: () => void
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = "",
  priority = false,
  quality = 75,
  placeholder = "blur",
  blurDataURL,
  sizes,
  fill = false,
  objectFit = "cover",
  onLoad,
  onError,
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isInView, setIsInView] = useState(priority)
  const [hasError, setHasError] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true)
            observer.disconnect()
          }
        })
      },
      {
        rootMargin: "50px",
        threshold: 0.1,
      }
    )

    if (containerRef.current) {
      observer.observe(containerRef.current)
    }

    return () => observer.disconnect()
  }, [priority])

  // Generate optimized src with quality and format
  const getOptimizedSrc = (originalSrc: string, width?: number, height?: number) => {
    if (originalSrc.includes("placeholder.svg")) {
      return originalSrc
    }

    // In a real implementation, you would use a service like Cloudinary, Vercel Image Optimization, or similar
    const params = new URLSearchParams()
    if (width) params.set("w", width.toString())
    if (height) params.set("h", height.toString())
    params.set("q", quality.toString())
    params.set("f", "webp")

    return `${originalSrc}?${params.toString()}`
  }

  // Generate different sizes for responsive images
  const generateSrcSet = (originalSrc: string) => {
    if (originalSrc.includes("placeholder.svg")) {
      return undefined
    }

    const breakpoints = [640, 768, 1024, 1280, 1536]
    return breakpoints
      .map((bp) => `${getOptimizedSrc(originalSrc, bp)} ${bp}w`)
      .join(", ")
  }

  const handleLoad = () => {
    setIsLoaded(true)
    onLoad?.()
  }

  const handleError = () => {
    setHasError(true)
    onError?.()
  }

  // Generate blur placeholder\
  const defaultBlurDataURL = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R+Cp5O4wTw5T4z7VN+6+1Tftv8AqpvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4qb4V+Km+FfipvhX4
