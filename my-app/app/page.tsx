"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Search, MapPin, Calendar, Star, ArrowRight, ChevronLeft, ChevronRight } from "lucide-react"
import { apiClient } from "@/lib/api"
import { Destination, BlogPost, HeroSlide, SeasonalPick } from "@/lib/types"
import "./globals.css"

const heroSlides: HeroSlide[] = [
  {
    id: 1,
    image: "/pexels-shaani-sewwandi-1401278-2937148.jpg",
    title: "Discover Paradise",
    subtitle: "Experience the magic of Sri Lanka",
  },
  {
    id: 2,
    image: "/pexels-srkportraits-10710560.jpg",
    title: "Ancient Wonders",
    subtitle: "Explore 2,500 years of history",
  },
  {
    id: 3,
    image: "/pexels-freestockpro-320260 (1).jpg",
    title: "Tropical Beaches",
    subtitle: "Relax on pristine golden shores",
  },
]

const seasonalPicks: SeasonalPick[] = [
  {
    id: 1,
    title: "Monsoon Magic",
    image: "/placeholder.svg?height=200&width=300",
    description: "Experience the lush green landscapes during monsoon season",
    season: "May - September",
  },
  {
    id: 2,
    title: "Festival Season",
    image: "/placeholder.svg?height=200&width=300",
    description: "Join colorful celebrations and cultural festivals",
    season: "December - April",
  },
  {
    id: 3,
    title: "Wildlife Safari",
    image: "/placeholder.svg?height=200&width=300",
    description: "Best time for leopard and elephant spotting",
    season: "February - June",
  },
]

export default function HomePage() {
  const [currentSlide, setCurrentSlide] = useState(0)
  const [featuredDestinations, setFeaturedDestinations] = useState<Destination[]>([])
  const [journalPreviews, setJournalPreviews] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)

      // Fetch featured destinations
      const destinationsData = await apiClient.getDestinations({ limit: 8 }) as Destination[]
      setFeaturedDestinations(destinationsData)

      // Fetch recent blog posts
      const blogData = await apiClient.getBlogPosts({ limit: 5 }) as BlogPost[]
      setJournalPreviews(blogData)
    } catch (error) {
      console.error("Failed to fetch data:", error)
    } finally {
      setLoading(false)
    }
  }

    // Add auto-slide functionality
  useEffect(() => {
    if (isPaused) return

    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length)
    }, 10000)

    return () => clearInterval(interval)
  }, [isPaused])


  const nextSlide = () => {
    console.log("Next slide clicked, current:", currentSlide)
    setCurrentSlide((prev) => (prev + 1) % heroSlides.length)
  }

  const prevSlide = () => {
    console.log("Prev slide clicked, current:", currentSlide)
    setCurrentSlide((prev) => (prev - 1 + heroSlides.length) % heroSlides.length)
  }


  // Add loading state for featured destinations section
  const renderFeaturedDestinations = () => {
    if (loading) {
      return <div className="text-center">Loading destinations...</div>
    }

    return (
      <div className="overflow-x-auto pb-4">
        <div className="flex space-x-6 w-max">
          {featuredDestinations.map((destination, index) => (
            <div
              key={destination.id}
              className="w-80 bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="relative">
                <img
                  src={destination.image || "/placeholder.svg"}
                  alt={destination.name}
                  className="w-full h-48 object-cover"
                />
                <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-gray-700">
                  {destination.category}
                </div>
                <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="text-sm font-medium text-gray-700">{destination.rating}</span>
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-poppins font-semibold mb-2">{destination.name}</h3>
                <p className="text-gray-600 mb-4">{destination.description}</p>
                <Link
                  href={`/destinations/${destination.name.toLowerCase()}`}
                  className="inline-flex items-center text-teal-600 hover:text-teal-700 font-medium transition-colors duration-200"
                >
                  Learn More
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-screen overflow-hidden">
        {/* Background Slides */}
        <div className="absolute inset-0">
          {heroSlides.map((slide, index) => (
            <div
              key={slide.id}
              className={`absolute inset-0 transition-opacity duration-1000 ${
                index === currentSlide ? "opacity-100" : "opacity-0"
              }`}
            >
              <img src={slide.image || "/placeholder.svg"} alt={slide.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/40" />
            </div>
          ))}
        </div>

        {/* Navigation Arrows */}
        <button
          onClick={prevSlide}
          className="absolute left-6 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-all duration-200 z-50"
          type="button"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button
          onClick={nextSlide}
          className="absolute right-6 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-all duration-200 z-50"
          type="button"
        >
          <ChevronRight className="w-6 h-6" />
        </button>

        {/* Slide Indicators */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-2 z-10">
          {heroSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-3 h-3 rounded-full transition-all duration-200 ${
                index === currentSlide ? "bg-white" : "bg-white/50"
              }`}
            />
          ))}
        </div>

        {/* Hero Content */}
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="text-center text-white max-w-4xl px-4">
            <h1 className="text-5xl md:text-7xl font-poppins font-bold mb-6 animate-fade-in">
              {heroSlides[currentSlide].title}
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-gray-200 animate-slide-up animation-delay-200">
              {heroSlides[currentSlide].subtitle}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up animation-delay-400">
              <Link href="/destinations" className="btn-primary">
                Explore Now
              </Link>
              <Link href="/planning" className="btn-secondary">
                Plan Your Trip
              </Link>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 w-full max-w-4xl px-4 z-10">
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-2xl animate-slide-up animation-delay-600">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Destination"
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Experience"
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <button className="btn-primary w-full">Search</button>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Destinations */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-poppins font-bold mb-6 gradient-text">Featured Destinations</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover the most breathtaking places Sri Lanka has to offer, from ancient wonders to pristine beaches
            </p>
          </div>

          {renderFeaturedDestinations()}

          <div className="text-center mt-12">
            <Link href="/destinations" className="btn-primary">
              View All Destinations
            </Link>
          </div>
        </div>
      </section>

      {/* Seasonal Picks */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-poppins font-bold mb-6 gradient-text">Seasonal Picks</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience Sri Lanka at its best with our curated seasonal recommendations
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {seasonalPicks.map((pick, index) => (
              <div
                key={pick.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-slide-up"
                style={{ animationDelay: `${index * 200}ms` }}
              >
                <img src={pick.image || "/placeholder.svg"} alt={pick.title} className="w-full h-48 object-cover" />
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xl font-poppins font-semibold">{pick.title}</h3>
                    <span className="text-sm text-teal-600 bg-teal-50 px-3 py-1 rounded-full">{pick.season}</span>
                  </div>
                  <p className="text-gray-600">{pick.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Journal Previews */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-poppins font-bold mb-6 gradient-text">Travel Journal</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get inspired by real stories and experiences from fellow travelers
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {journalPreviews.map((article, index) => (
              <article
                key={article.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-slide-up"
                style={{ animationDelay: `${index * 200}ms` }}
              >
                <img
                  src={article.image || "/placeholder.svg"}
                  alt={article.title}
                  className="w-full h-48 object-cover"
                />
                <div className="p-6">
                  <h3 className="text-xl font-poppins font-semibold mb-3">{article.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-3">{article.excerpt}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>By {article.author}</span>
                    <span>{article.date}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link href="/journal" className="btn-primary">
              Read More Stories
            </Link>
          </div>
        </div>
      </section>

      {/* Instagram Feed Preview */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-poppins font-bold mb-6 gradient-text">#ExploreSriLanka</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Share your Sri Lankan adventures and get featured on our feed
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {Array.from({ length: 12 }, (_, i) => (
              <div
                key={i}
                className="aspect-square bg-gradient-to-br from-teal-100 to-cyan-100 rounded-lg overflow-hidden card-hover animate-fade-in"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <img
                  src={`/placeholder.svg?height=200&width=200&text=Photo${i + 1}`}
                  alt={`Instagram photo ${i + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <a
              href="https://instagram.com/exploresrilanka"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              Follow @ExploreSriLanka
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
