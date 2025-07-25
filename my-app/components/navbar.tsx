"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, X, ChevronDown } from "lucide-react"
import { useDestinationTypes } from "@/lib/hooks/useDestinationTypes"
import { NavigationItem } from "@/lib/types/ui"

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const pathname = usePathname()
  const { destinationTypes, loading } = useDestinationTypes()

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

          {/* CTA Button */}
          <div className="hidden lg:block">
            <Link href="/planning" className="btn-primary">
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
              <div className="px-4 pt-4">
                <Link href="/planning" className="btn-primary w-full text-center block">
                  Plan Your Trip
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
