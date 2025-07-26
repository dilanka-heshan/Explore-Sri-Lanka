import type React from "react"
import type { Metadata } from "next"
import { Inter, Poppins } from "next/font/google"
import "./globals.css"
import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import ChatBot from "@/components/chatbot"
import { AuthProvider } from "@/contexts/AuthContext"
import { Toaster } from "react-hot-toast"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-poppins",
})

export const metadata: Metadata = {
  title: "Explore Sri Lanka - Discover Paradise",
  description:
    "Discover the beauty of Sri Lanka with our comprehensive travel guide. Plan your perfect trip to the pearl of the Indian Ocean.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <body className="font-inter bg-white text-gray-900 overflow-x-hidden">
        <AuthProvider>
          <Navbar />
          <main className="min-h-screen">{children}</main>
          <Footer />
          <ChatBot />
          <Toaster position="top-right" />
        </AuthProvider>
      </body>
    </html>
  )
}
