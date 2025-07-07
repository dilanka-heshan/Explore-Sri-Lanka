"use client"

import { Users, Award, Globe, Heart } from "lucide-react"

const stats = [
  { label: "Happy Travelers", value: "50,000+", icon: Users },
  { label: "Years of Experience", value: "15+", icon: Award },
  { label: "Destinations Covered", value: "200+", icon: Globe },
  { label: "Customer Satisfaction", value: "98%", icon: Heart },
]

const team = [
  {
    name: "Samantha Perera",
    role: "Founder & CEO",
    image: "/placeholder.svg?height=300&width=300",
    bio: "Born and raised in Colombo, Samantha has dedicated her life to showcasing the beauty of Sri Lanka to the world.",
  },
  {
    name: "Rajesh Kumar",
    role: "Head of Operations",
    image: "/placeholder.svg?height=300&width=300",
    bio: "With 12 years in tourism, Rajesh ensures every traveler has an unforgettable experience.",
  },
  {
    name: "Nisha Fernando",
    role: "Cultural Expert",
    image: "/placeholder.svg?height=300&width=300",
    bio: "A historian and cultural enthusiast, Nisha brings Sri Lankan heritage to life for our visitors.",
  },
  {
    name: "David Thompson",
    role: "Adventure Guide",
    image: "/placeholder.svg?height=300&width=300",
    bio: "An experienced mountaineer and wildlife expert, David leads our most thrilling expeditions.",
  },
]

const values = [
  {
    title: "Authentic Experiences",
    description: "We believe in showing you the real Sri Lanka, beyond the tourist facade.",
    icon: Heart,
  },
  {
    title: "Sustainable Tourism",
    description: "We are committed to preserving Sri Lanka's natural beauty for future generations.",
    icon: Globe,
  },
  {
    title: "Local Communities",
    description: "We work closely with local communities to ensure tourism benefits everyone.",
    icon: Users,
  },
  {
    title: "Excellence",
    description: "We strive for excellence in every aspect of your Sri Lankan adventure.",
    icon: Award,
  },
]

export default function AboutPage() {
  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="relative py-24 bg-gradient-to-r from-teal-600 to-cyan-600 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20" />
        <div className="container-custom relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-poppins font-bold mb-6 animate-fade-in">Our Story</h1>
            <p className="text-xl md:text-2xl text-teal-100 animate-slide-up animation-delay-200">
              Passionate about sharing the magic of Sri Lanka with the world
            </p>
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="animate-slide-in-left">
              <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Born from a Love for Sri Lanka</h2>
              <div className="space-y-6 text-lg text-gray-600 leading-relaxed">
                <p>
                  Explore Sri Lanka was founded in 2009 with a simple mission: to share the incredible beauty, rich
                  culture, and warm hospitality of our island nation with travelers from around the world.
                </p>
                <p>
                  What started as a small family business has grown into Sri Lanka's most trusted travel platform,
                  helping over 50,000 travelers discover the pearl of the Indian Ocean. We believe that travel should be
                  transformative, authentic, and sustainable.
                </p>
                <p>
                  Our team of local experts, cultural enthusiasts, and adventure guides work tirelessly to create
                  experiences that go beyond the ordinary. We don't just show you Sri Lanka – we help you feel it, taste
                  it, and carry it in your heart forever.
                </p>
              </div>
            </div>
            <div className="animate-slide-in-right">
              <img
                src="/placeholder.svg?height=500&width=600"
                alt="Sri Lankan landscape"
                className="w-full h-96 object-cover rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Our Impact</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Numbers that reflect our commitment to excellence and our travelers' satisfaction
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon
              return (
                <div
                  key={stat.label}
                  className="text-center animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <div className="text-3xl md:text-4xl font-poppins font-bold text-gray-900 mb-2">{stat.value}</div>
                  <div className="text-gray-600 font-medium">{stat.label}</div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Meet Our Team</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The passionate individuals who make your Sri Lankan adventure unforgettable
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <div
                key={member.name}
                className="bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <img src={member.image || "/placeholder.svg"} alt={member.name} className="w-full h-64 object-cover" />
                <div className="p-6">
                  <h3 className="text-xl font-poppins font-semibold mb-1">{member.name}</h3>
                  <p className="text-teal-600 font-medium mb-3">{member.role}</p>
                  <p className="text-gray-600 text-sm leading-relaxed">{member.bio}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Our Values</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">The principles that guide everything we do</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {values.map((value, index) => {
              const Icon = value.icon
              return (
                <div
                  key={value.title}
                  className="bg-white p-8 rounded-2xl shadow-lg card-hover animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="w-12 h-12 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-lg flex items-center justify-center mb-6">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-poppins font-semibold mb-4">{value.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{value.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section-padding bg-gradient-to-r from-teal-600 to-cyan-600 text-white">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-poppins font-bold mb-8 animate-fade-in">Our Mission</h2>
            <p className="text-xl leading-relaxed animate-slide-up animation-delay-200">
              To be the bridge between Sri Lanka's incredible heritage and curious travelers worldwide, creating
              meaningful connections that benefit both visitors and local communities while preserving the natural and
              cultural treasures of our beautiful island for future generations.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
