import { useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { changePassword, changeEmail, deleteAccount } from '../../services/api'
import useAuthStore from '../../stores/authStore'
import { useNavigate } from 'react-router-dom'

export default function AccountManagement() {
    const navigate = useNavigate()
    const { user, setUser, setToken, logout } = useAuthStore()

    // Change Password State
    const [showChangePassword, setShowChangePassword] = useState(false)
    const [currentPassword, setCurrentPassword] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [changingPassword, setChangingPassword] = useState(false)

    // Change Email State
    const [showChangeEmail, setShowChangeEmail] = useState(false)
    const [newEmail, setNewEmail] = useState('')
    const [emailPassword, setEmailPassword] = useState('')
    const [changingEmail, setChangingEmail] = useState(false)

    // Delete Account State
    const [showDeleteAccount, setShowDeleteAccount] = useState(false)
    const [deletePassword, setDeletePassword] = useState('')
    const [deleteConfirmation, setDeleteConfirmation] = useState('')
    const [deletingAccount, setDeletingAccount] = useState(false)

    // Change Password Handler
    const handleChangePassword = async (e) => {
        e.preventDefault()

        if (newPassword !== confirmPassword) {
            toast.error('Passwords do not match')
            return
        }

        if (newPassword.length < 6) {
            toast.error('Password must be at least 6 characters')
            return
        }

        setChangingPassword(true)

        try {
            const response = await changePassword(currentPassword, newPassword)
            toast.success(response.message || 'Password changed successfully')

            // Reset form
            setCurrentPassword('')
            setNewPassword('')
            setConfirmPassword('')
            setShowChangePassword(false)
        } catch (error) {
            toast.error(error.message || 'Failed to change password')
        } finally {
            setChangingPassword(false)
        }
    }

    // Change Email Handler
    const handleChangeEmail = async (e) => {
        e.preventDefault()

        if (!newEmail || !newEmail.includes('@')) {
            toast.error('Please enter a valid email')
            return
        }

        setChangingEmail(true)

        try {
            const response = await changeEmail(newEmail, emailPassword)
            toast.success(response.message || 'Email changed successfully')

            // Update user state with new email and token
            setUser({ ...user, email: response.email })
            setToken(response.token)

            // Reset form
            setNewEmail('')
            setEmailPassword('')
            setShowChangeEmail(false)
        } catch (error) {
            toast.error(error.message || 'Failed to change email')
        } finally {
            setChangingEmail(false)
        }
    }

    // Delete Account Handler
    const handleDeleteAccount = async (e) => {
        e.preventDefault()

        if (deleteConfirmation !== 'DELETE') {
            toast.error('Please type DELETE to confirm')
            return
        }

        if (!deletePassword) {
            toast.error('Password is required')
            return
        }

        setDeletingAccount(true)

        try {
            const response = await deleteAccount(deletePassword, deleteConfirmation)
            toast.success(response.message || 'Account deleted successfully')

            // Logout and redirect
            setTimeout(() => {
                logout()
                navigate('/')
            }, 2000)
        } catch (error) {
            toast.error(error.message || 'Failed to delete account')
            setDeletingAccount(false)
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">Account Management</h2>
                    <p className="text-sm text-gray-400">Manage your account security and settings</p>
                </div>
            </div>

            {/* Change Password Section */}
            <motion.div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <button
                    onClick={() => setShowChangePassword(!showChangePassword)}
                    className="w-full flex items-center justify-between text-left"
                >
                    <div>
                        <h3 className="text-lg font-semibold text-white">Change Password</h3>
                        <p className="text-sm text-gray-400">Update your account password</p>
                    </div>
                    <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${showChangePassword ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                {showChangePassword && (
                    <motion.form
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        onSubmit={handleChangePassword}
                        className="mt-6 space-y-4"
                    >
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Current Password</label>
                            <input
                                type="password"
                                value={currentPassword}
                                onChange={(e) => setCurrentPassword(e.target.value)}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">New Password</label>
                            <input
                                type="password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                                minLength={6}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Confirm New Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                                minLength={6}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={changingPassword}
                            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {changingPassword ? 'Changing Password...' : 'Change Password'}
                        </button>
                    </motion.form>
                )}
            </motion.div>

            {/* Change Email Section */}
            <motion.div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <button
                    onClick={() => setShowChangeEmail(!showChangeEmail)}
                    className="w-full flex items-center justify-between text-left"
                >
                    <div>
                        <h3 className="text-lg font-semibold text-white">Change Email</h3>
                        <p className="text-sm text-gray-400">Update your email address</p>
                    </div>
                    <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${showChangeEmail ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                {showChangeEmail && (
                    <motion.form
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        onSubmit={handleChangeEmail}
                        className="mt-6 space-y-4"
                    >
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">New Email</label>
                            <input
                                type="email"
                                value={newEmail}
                                onChange={(e) => setNewEmail(e.target.value)}
                                placeholder={user?.email}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                            <input
                                type="password"
                                value={emailPassword}
                                onChange={(e) => setEmailPassword(e.target.value)}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={changingEmail}
                            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {changingEmail ? 'Changing Email...' : 'Change Email'}
                        </button>
                    </motion.form>
                )}
            </motion.div>

            {/* Delete Account Section - Danger Zone */}
            <motion.div className="bg-red-500/10 backdrop-blur-sm rounded-xl p-6 border border-red-500/30">
                <button
                    onClick={() => setShowDeleteAccount(!showDeleteAccount)}
                    className="w-full flex items-center justify-between text-left"
                >
                    <div>
                        <h3 className="text-lg font-semibold text-red-400">Delete Account</h3>
                        <p className="text-sm text-gray-400">Permanently delete your account and all data</p>
                    </div>
                    <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${showDeleteAccount ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                {showDeleteAccount && (
                    <motion.form
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        onSubmit={handleDeleteAccount}
                        className="mt-6 space-y-4"
                    >
                        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
                            <p className="text-sm text-red-300">
                                ⚠️ <strong>Warning:</strong> This action cannot be undone. All your documents, chat history, and account data will be permanently deleted.
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                            <input
                                type="password"
                                value={deletePassword}
                                onChange={(e) => setDeletePassword(e.target.value)}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Type <span className="text-red-400 font-bold">DELETE</span> to confirm
                            </label>
                            <input
                                type="text"
                                value={deleteConfirmation}
                                onChange={(e) => setDeleteConfirmation(e.target.value)}
                                placeholder="DELETE"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={deletingAccount || deleteConfirmation !== 'DELETE'}
                            className="w-full py-3 bg-gradient-to-r from-red-500 to-red-700 hover:from-red-600 hover:to-red-800 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {deletingAccount ? 'Deleting Account...' : 'Delete My Account'}
                        </button>
                    </motion.form>
                )}
            </motion.div>
        </div>
    )
}
