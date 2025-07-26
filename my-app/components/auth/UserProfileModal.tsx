"use client"

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { User, Mail, Phone, MapPin, Globe, Edit3, Save, X, Camera, Heart, Plane, Star } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface UserProfileModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function UserProfileModal({ isOpen, onClose }: UserProfileModalProps) {
  const { user, updateProfile, updatePassword, logout } = useAuth()
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'security' | 'favorites'>('profile')
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)

  // Profile form state
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    location: user?.location || '',
    nationality: user?.nationality || '',
    bio: user?.bio || ''
  })

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })

  const handleProfileUpdate = async () => {
    setLoading(true)
    try {
      await updateProfile(profileData)
      toast.success('Profile updated successfully!')
      setIsEditing(false)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordUpdate = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match')
      return
    }

    setLoading(true)
    try {
      await updatePassword(
        passwordData.current_password,
        passwordData.new_password,
        passwordData.confirm_password
      )
      toast.success('Password updated successfully!')
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to update password')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    onClose()
    toast.success('Logged out successfully')
  }

  if (!user) return null

  const countries = [
    'Sri Lanka', 'India', 'United States', 'United Kingdom', 'Australia', 'Canada',
    'Germany', 'France', 'Japan', 'South Korea', 'Singapore', 'Malaysia', 'Thailand',
    'Other'
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">My Profile</DialogTitle>
        </DialogHeader>

        {/* User Header */}
        <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg mb-6">
          <div className="relative">
            <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.full_name} className="w-16 h-16 rounded-full object-cover" />
              ) : (
                user.full_name.charAt(0).toUpperCase()
              )}
            </div>
            <button className="absolute -bottom-1 -right-1 bg-white rounded-full p-1 shadow-md">
              <Camera className="w-3 h-3 text-gray-600" />
            </button>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold">{user.full_name}</h3>
            <p className="text-gray-600">{user.email}</p>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
              <span className="flex items-center space-x-1">
                <Star className="w-4 h-4" />
                <span>{user.total_reviews || 0} reviews</span>
              </span>
              <span className="flex items-center space-x-1">
                <Plane className="w-4 h-4" />
                <span>{user.total_bookings || 0} trips</span>
              </span>
              <span className="flex items-center space-x-1">
                <Heart className="w-4 h-4" />
                <span>{user.favorite_destinations?.length || 0} favorites</span>
              </span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6">
          {[
            { id: 'profile', label: 'Profile', icon: User },
            { id: 'preferences', label: 'Travel', icon: Plane },
            { id: 'security', label: 'Security', icon: Edit3 },
            { id: 'favorites', label: 'Favorites', icon: Heart }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === id
                  ? 'bg-white text-teal-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold">Personal Information</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                {isEditing ? (
                  <>
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </>
                ) : (
                  <>
                    <Edit3 className="w-4 h-4 mr-2" />
                    Edit
                  </>
                )}
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Full Name</Label>
                {isEditing ? (
                  <Input
                    value={profileData.full_name}
                    onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                  />
                ) : (
                  <div className="p-3 bg-gray-50 rounded-lg">{user.full_name}</div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Email</Label>
                <div className="p-3 bg-gray-50 rounded-lg flex items-center justify-between">
                  <span>{user.email}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    user.email_verified 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {user.email_verified ? 'Verified' : 'Unverified'}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Phone</Label>
                {isEditing ? (
                  <Input
                    value={profileData.phone}
                    onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                    placeholder="Phone number"
                  />
                ) : (
                  <div className="p-3 bg-gray-50 rounded-lg">{user.phone || 'Not provided'}</div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Nationality</Label>
                {isEditing ? (
                  <select
                    value={profileData.nationality}
                    onChange={(e) => setProfileData({ ...profileData, nationality: e.target.value })}
                    className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Select country</option>
                    {countries.map((country) => (
                      <option key={country} value={country}>
                        {country}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="p-3 bg-gray-50 rounded-lg">{user.nationality || 'Not provided'}</div>
                )}
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label>Location</Label>
                {isEditing ? (
                  <Input
                    value={profileData.location}
                    onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
                    placeholder="City, State/Province"
                  />
                ) : (
                  <div className="p-3 bg-gray-50 rounded-lg">{user.location || 'Not provided'}</div>
                )}
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label>Bio</Label>
                {isEditing ? (
                  <textarea
                    value={profileData.bio}
                    onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                    className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                    rows={3}
                    placeholder="Tell us about yourself..."
                  />
                ) : (
                  <div className="p-3 bg-gray-50 rounded-lg min-h-[80px]">
                    {user.bio || 'No bio provided'}
                  </div>
                )}
              </div>
            </div>

            {isEditing && (
              <div className="flex justify-end space-x-3">
                <Button variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
                <Button onClick={handleProfileUpdate} disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Travel Preferences Tab */}
        {activeTab === 'preferences' && (
          <div className="space-y-6">
            <h4 className="text-lg font-semibold">Travel Preferences</h4>
            <div className="p-4 bg-gray-50 rounded-lg text-center">
              <Plane className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Travel preferences coming soon!</p>
              <p className="text-sm text-gray-500">Set your interests, budget level, and travel style</p>
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            <h4 className="text-lg font-semibold">Security Settings</h4>
            
            {/* Change Password */}
            <div className="space-y-4">
              <h5 className="font-medium">Change Password</h5>
              <div className="grid grid-cols-1 gap-4">
                <div className="space-y-2">
                  <Label>Current Password</Label>
                  <Input
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                    placeholder="Enter current password"
                  />
                </div>
                <div className="space-y-2">
                  <Label>New Password</Label>
                  <Input
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                    placeholder="Enter new password"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Confirm New Password</Label>
                  <Input
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    placeholder="Confirm new password"
                  />
                </div>
              </div>
              <Button onClick={handlePasswordUpdate} disabled={loading}>
                {loading ? 'Updating...' : 'Update Password'}
              </Button>
            </div>

            <hr />

            {/* Account Actions */}
            <div className="space-y-4">
              <h5 className="font-medium">Account Actions</h5>
              <div className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  Download My Data
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={handleLogout}>
                  Sign Out
                </Button>
                <Button variant="destructive" className="w-full justify-start">
                  Delete Account
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Favorites Tab */}
        {activeTab === 'favorites' && (
          <div className="space-y-6">
            <h4 className="text-lg font-semibold">Favorite Destinations</h4>
            <div className="p-4 bg-gray-50 rounded-lg text-center">
              <Heart className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">No favorites yet!</p>
              <p className="text-sm text-gray-500">Save destinations you love to see them here</p>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
