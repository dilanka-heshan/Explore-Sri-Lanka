"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, X, ChevronDown, User, LogIn, Heart, Settings, LogOut } from "lucide-react"
import { useDestinationTypes } from "@/lib/hooks/useDestinationTypes"
import { NavigationItem } from "@/lib/types/ui"
import { useAuth } from "@/contexts/AuthContext"
import AuthModal from "@/components/auth/AuthModal"
import UserProfileModal from "@/components/auth/UserProfileModal"

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [showProfileModal, setShowProfileModal] = useState(false)
  const [authModalTab, setAuthModalTab] = useState<'login' | 'register'>('login')
  const pathname = usePathname()
  const { destinationTypes, loading } = useDestinationTypes()
  const { user, logout, isAuthenticated } = useAuth()

  // Create dynamic navigation with destination types from database
  const navigation: NavigationItem[] = [
    { name: "Home", href: "/" },
    {
      name: "Destinations",
      href: "/destinations",
      dropdown: [
        { name: "All Destinations", href: "/destinations" },
        // Show loading state or fallback categories
        ...(loading ? [
          { name: "Cultural", href: "/destinations?category=cultural" },
          { name: "Beach", href: "/destinations?category=beach" },
          { name: "Nature", href: "/destinations?category=nature" },
          { name: "Wildlife", href: "/destinations?category=wildlife" },
          { name: "Adventure", href: "/destinations?category=adventure" },
        ] : destinationTypes.map(type => ({
          name: type,
          href: `/destinations?category=${type.toLowerCase()}`
        })))
      ],
    },
    { name: "Experiences", href: "/experiences" },
    { name: "Planning", href: "/planning" },
    { name: "Journal", href: "/journal" },
    { name: "About", href: "/about" },
    { name: "Contact", href: "/contact" },
  ]

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const handleAuthClick = (tab: 'login' | 'register') => {
    setAuthModalTab(tab)
    setShowAuthModal(true)
  }

  const handleLogout = () => {
    logout()
    setActiveDropdown(null)
  }

  return (
    <nav
      className={`fixed w-full z-50 transition-all duration-300 ${
        isScrolled ? "bg-white/95 backdrop-blur-md shadow-lg" : "bg-transparent"
      }`}
    >
      <div className="container-custom">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">SL</span>
            </div>
            <span className="text-xl font-poppins font-bold gradient-text">Explore Sri Lanka</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-8">
            {navigation.map((item) => (
              <div key={item.name} className="relative">
                {item.dropdown ? (
                  <div
                    className="relative"
                    onMouseEnter={() => setActiveDropdown(item.name)}
                    onMouseLeave={() => setActiveDropdown(null)}
                  >
                    <button className="flex items-center space-x-1 text-gray-900 hover:text-teal-600 transition-colors duration-200 font-medium">
                      <span>{item.name}</span>
                      <ChevronDown className="w-4 h-4" />
                    </button>
                    {activeDropdown === item.name && (
                      <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-2 animate-fade-in">
                        {item.dropdown.map((dropdownItem) => (
                          <Link
                            key={dropdownItem.name}
                            href={dropdownItem.href}
                            className="block px-4 py-2 text-gray-900 hover:text-teal-600 hover:bg-gray-50 transition-colors duration-200"
                          >
                            {dropdownItem.name}
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <Link
                    href={item.href}
                    className={`text-gray-900 hover:text-teal-600 transition-colors duration-200 font-medium ${
                      pathname === item.href ? "text-teal-600" : ""
                    }`}
                  >
                    {item.name}
                  </Link>
                )}
              </div>
            ))}
          </div>

          {/* Auth Section */}
          <div className="hidden lg:flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setActiveDropdown(activeDropdown === 'user' ? null : 'user')}
                  className="flex items-center space-x-2 px-3 py-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors duration-200"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                    {user.avatar_url ? (
                      <img src={user.avatar_url} alt={user.full_name} className="w-8 h-8 rounded-full object-cover" />
                    ) : (
                      user.full_name.charAt(0).toUpperCase()
                    )}
                  </div>
                  <span className="font-medium text-gray-700">{user.full_name.split(' ')[0]}</span>
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                </button>

                {/* User Dropdown */}
                {activeDropdown === 'user' && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-2 z-50">
                    <button
                      onClick={() => {
                        setShowProfileModal(true)
                        setActiveDropdown(null)
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                    >
                      <User className="w-4 h-4" />
                      <span>My Profile</span>
                    </button>
                    <Link
                      href="/favorites"
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                      onClick={() => setActiveDropdown(null)}
                    >
                      <Heart className="w-4 h-4" />
                      <span>Favorites</span>
                    </Link>
                    <Link
                      href="/my-trips"
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                      onClick={() => setActiveDropdown(null)}
                    >
                      <Settings className="w-4 h-4" />
                      <span>My Trips</span>
                    </Link>
                    <hr className="my-2" />
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => handleAuthClick('login')}
                  className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-teal-600 transition-colors duration-200"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Sign In</span>
                </button>
                <button
                  onClick={() => handleAuthClick('register')}
                  className="btn-primary"
                >
                  Sign Up
                </button>
              </div>
            )}

            {/* CTA Button */}
            <Link href="/planning" className="btn-secondary">
              Plan Your Trip
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="lg:hidden p-2 rounded-md text-gray-700 hover:text-teal-600 transition-colors duration-200"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="lg:hidden bg-white border-t border-gray-100 animate-slide-up">
            <div className="py-4 space-y-2">
              {navigation.map((item) => (
                <div key={item.name}>
                  <Link
                    href={item.href}
                    className={`block px-4 py-2 text-gray-700 hover:text-teal-600 transition-colors duration-200 font-medium ${
                      pathname === item.href ? "text-teal-600 bg-gray-50" : ""
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    {item.name}
                  </Link>
                  {item.dropdown && (
                    <div className="ml-4 space-y-1">
                      {item.dropdown.map((dropdownItem) => (
                        <Link
                          key={dropdownItem.name}
                          href={dropdownItem.href}
                          className="block px-4 py-1 text-sm text-gray-600 hover:text-teal-600 transition-colors duration-200"
                          onClick={() => setIsOpen(false)}
                        >
                          {dropdownItem.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* Mobile Auth Section */}
              <div className="px-4 pt-4 border-t border-gray-100 mt-4">
                {isAuthenticated && user ? (
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3 pb-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-semibold">
                        {user.avatar_url ? (
                          <img src={user.avatar_url} alt={user.full_name} className="w-10 h-10 rounded-full object-cover" />
                        ) : (
                          user.full_name.charAt(0).toUpperCase()
                        )}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setShowProfileModal(true)
                        setIsOpen(false)
                      }}
                      className="w-full text-left py-2 text-gray-700 hover:text-teal-600 flex items-center space-x-2"
                    >
                      <User className="w-4 h-4" />
                      <span>My Profile</span>
                    </button>
                    <Link
                      href="/favorites"
                      className="w-full text-left py-2 text-gray-700 hover:text-teal-600 flex items-center space-x-2"
                      onClick={() => setIsOpen(false)}
                    >
                      <Heart className="w-4 h-4" />
                      <span>Favorites</span>
                    </Link>
                    <Link
                      href="/my-trips"
                      className="w-full text-left py-2 text-gray-700 hover:text-teal-600 flex items-center space-x-2"
                      onClick={() => setIsOpen(false)}
                    >
                      <Settings className="w-4 h-4" />
                      <span>My Trips</span>
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout()
                        setIsOpen(false)
                      }}
                      className="w-full text-left py-2 text-red-600 hover:text-red-700 flex items-center space-x-2"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <button
                      onClick={() => {
                        handleAuthClick('login')
                        setIsOpen(false)
                      }}
                      className="w-full text-left py-2 text-gray-700 hover:text-teal-600 flex items-center space-x-2"
                    >
                      <LogIn className="w-4 h-4" />
                      <span>Sign In</span>
                    </button>
                    <button
                      onClick={() => {
                        handleAuthClick('register')
                        setIsOpen(false)
                      }}
                      className="btn-primary w-full text-center"
                    >
                      Sign Up
                    </button>
                  </div>
                )}
                <div className="pt-3">
                  <Link href="/planning" className="btn-secondary w-full text-center block">
                    Plan Your Trip
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Auth Modal */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          defaultTab={authModalTab}
        />

        {/* User Profile Modal */}
        <UserProfileModal
          isOpen={showProfileModal}
          onClose={() => setShowProfileModal(false)}
        />
      </div>
    </nav>
  )
}
