import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'
import useAuthStore from '../stores/authStore'
import { useNavigate } from 'react-router-dom'
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

export default function AdminDashboard() {
    const [activeTab, setActiveTab] = useState('overview')
    const [loading, setLoading] = useState(true)
    const [dashboardData, setDashboardData] = useState(null)
    const [users, setUsers] = useState([])
    const [feedback, setFeedback] = useState([])
    const [aiFeedback, setAiFeedback] = useState([])
    const [aiFeedbackAnalytics, setAiFeedbackAnalytics] = useState(null)
    const navigate = useNavigate()
    const user = useAuthStore(state => state.user)

    // Check if user is admin
    useEffect(() => {
        if (!user?.is_admin) {
            toast.error('Admin access required')
            navigate('/app')
        }
    }, [user, navigate])

    // Fetch dashboard data
    useEffect(() => {
        fetchDashboardData()
        fetchAIFeedback() // Always fetch for overview charts
        if (activeTab === 'users') fetchUsers()
        if (activeTab === 'feedback') fetchFeedback()
    }, [activeTab])

    const fetchDashboardData = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/dashboard`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })
            const data = await response.json()
            if (data.success) {
                setDashboardData(data)
            }
            setLoading(false)
        } catch (error) {
            // Error logged server-side only
            toast.error('Failed to load dashboard')
            setLoading(false)
        }
    }

    const fetchUsers = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/users`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })
            const data = await response.json()
            if (data.success) {
                setUsers(data.users)
            }
        } catch (error) {
            // Error logged server-side only
        }
    }

    const fetchFeedback = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/feedback`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })
            const data = await response.json()
            if (data.success) {
                setFeedback(data.feedback)
            }
        } catch (error) {
            // Error logged server-side only
        }
    }

    const fetchAIFeedback = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/ai-feedback`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })
            const data = await response.json()
            if (data.success) {
                setAiFeedback(data.feedback)
                setAiFeedbackAnalytics(data.analytics)
            }
        } catch (error) {
            // Error logged server-side only
        }
    }

    const tabs = [
        { id: 'overview', label: '📊 Overview', icon: '📊' },
        { id: 'users', label: '👥 Users', icon: '👥' },
        { id: 'ai-responses', label: '🤖 AI Responses', icon: '🤖' },
        { id: 'feedback', label: '💬 Site Feedback', icon: '💬' }
    ]

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0a0f1e] flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                    <p className="text-gray-400">Loading admin dashboard...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-[#0a0f1e] text-white">
            {/* Header */}
            <header className="bg-[#1e293b] border-b border-white/10 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/app')}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                            </svg>
                        </button>
                        <div>
                            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
                            <p className="text-sm text-gray-400">DokGuru Voice Analytics</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="px-4 py-2 bg-purple-500/20 border border-purple-500/30 rounded-lg">
                            <span className="text-sm font-semibold text-purple-400">Admin</span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Tabs */}
            <div className="bg-[#1e293b] border-b border-white/10 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex gap-2">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`px-6 py-3 font-medium transition-all relative ${
                                    activeTab === tab.id
                                        ? 'text-white'
                                        : 'text-gray-400 hover:text-white'
                                }`}
                            >
                                {tab.label}
                                {activeTab === tab.id && (
                                    <motion.div
                                        layoutId="activeTab"
                                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500"
                                    />
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-8">
                {activeTab === 'overview' && (
                    <OverviewTab data={dashboardData} aiAnalytics={aiFeedbackAnalytics} />
                )}
                {activeTab === 'users' && (
                    <UsersTab users={users} />
                )}
                {activeTab === 'ai-responses' && (
                    <AIResponsesTab feedback={aiFeedback} analytics={aiFeedbackAnalytics} />
                )}
                {activeTab === 'feedback' && (
                    <FeedbackTab feedback={feedback} />
                )}
            </div>
        </div>
    )
}

// Overview Tab Component with 3D Charts
function OverviewTab({ data, aiAnalytics }) {
    const system = data?.system || {}
    const feedback = data?.feedback || {}

    const stats = [
        { label: 'Total Users', value: system.total_users || 0, icon: '👥', color: 'from-blue-500 to-cyan-500' },
        { label: 'Total Documents', value: system.total_documents || 0, icon: '📄', color: 'from-purple-500 to-pink-500' },
        { label: 'Total Feedback', value: system.total_feedback || 0, icon: '💬', color: 'from-green-500 to-emerald-500' },
        { label: 'Avg Rating', value: system.average_rating || 0, icon: '⭐', color: 'from-yellow-500 to-orange-500' },
        { label: 'New Users (7d)', value: system.recent_users_week || 0, icon: '📈', color: 'from-indigo-500 to-purple-500' },
        { label: 'NPS Score', value: feedback.nps_score || 0, icon: '📊', color: 'from-pink-500 to-rose-500' }
    ]

    // Prepare chart data
    const feedbackTypeData = Object.entries(feedback.by_type || {}).map(([type, count]) => ({
        name: type.replace('_', ' ').split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' '),
        value: count
    }))

    const feedbackRatingData = Object.entries(feedback.by_rating || {})
        .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
        .map(([rating, count]) => ({
            name: `${rating} Star${rating > 1 ? 's' : ''}`,
            count: count,
            rating: parseInt(rating)
        }))

    const aiSatisfactionData = aiAnalytics ? [
        { name: 'Likes', value: aiAnalytics.likes || 0, color: '#10b981' },
        { name: 'Dislikes', value: aiAnalytics.dislikes || 0, color: '#ef4444' }
    ] : []

    const COLORS = ['#8b5cf6', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']

    // Custom tooltip
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-gray-900 border border-purple-500/50 rounded-lg p-3 shadow-xl">
                    <p className="text-white font-semibold">{payload[0].name}</p>
                    <p className="text-purple-400 text-sm">{payload[0].value}</p>
                </div>
            )
        }
        return null
    }

    return (
        <div className="space-y-6 md:space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                {stats.map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl md:rounded-2xl p-4 md:p-6 hover:border-white/20 transition-all"
                    >
                        <div className="flex items-center justify-between mb-3 md:mb-4">
                            <div className={`w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br ${stat.color} rounded-lg md:rounded-xl flex items-center justify-center text-xl md:text-2xl`}>
                                {stat.icon}
                            </div>
                            <div className={`text-2xl md:text-3xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                                {stat.value}
                            </div>
                        </div>
                        <p className="text-gray-400 text-xs md:text-sm font-medium">{stat.label}</p>
                    </motion.div>
                ))}
            </div>

            {/* 3D Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
                {/* Feedback by Type - 3D Pie Chart */}
                {feedbackTypeData.length > 0 && (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl md:rounded-2xl p-4 md:p-6">
                        <h3 className="text-base md:text-lg font-bold mb-4">Feedback Distribution by Type</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={feedbackTypeData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {feedbackTypeData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Feedback by Rating - 3D Bar Chart */}
                {feedbackRatingData.length > 0 && (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl md:rounded-2xl p-4 md:p-6">
                        <h3 className="text-base md:text-lg font-bold mb-4">Rating Distribution</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={feedbackRatingData}>
                                <defs>
                                    <linearGradient id="colorRating" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                                        <stop offset="95%" stopColor="#eab308" stopOpacity={0.3}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                                <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="count" fill="url(#colorRating)" radius={[8, 8, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* AI Response Satisfaction - 3D Donut Chart */}
                {aiSatisfactionData.length > 0 && (
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl md:rounded-2xl p-4 md:p-6">
                        <h3 className="text-base md:text-lg font-bold mb-4">AI Response Satisfaction</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={aiSatisfactionData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={90}
                                    fill="#8884d8"
                                    paddingAngle={5}
                                    dataKey="value"
                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                                >
                                    {aiSatisfactionData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                        {aiAnalytics && (
                            <div className="mt-4 text-center">
                                <div className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
                                    {aiAnalytics.satisfaction_rate}%
                                </div>
                                <p className="text-xs md:text-sm text-gray-400">Satisfaction Rate</p>
                            </div>
                        )}
                    </div>
                )}

                {/* System Metrics - 3D Area Chart */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl md:rounded-2xl p-4 md:p-6">
                    <h3 className="text-base md:text-lg font-bold mb-4">System Metrics Overview</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={[
                            { name: 'Users', value: system.total_users || 0 },
                            { name: 'Documents', value: system.total_documents || 0 },
                            { name: 'Feedback', value: system.total_feedback || 0 },
                            { name: 'AI Responses', value: aiAnalytics?.total || 0 }
                        ]}>
                            <defs>
                                <linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                            <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                            <Tooltip content={<CustomTooltip />} />
                            <Area type="monotone" dataKey="value" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorMetric)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    )
}

// Users Tab Component
function UsersTab({ users }) {
    const [searchTerm, setSearchTerm] = useState('')

    const filteredUsers = users.filter(user =>
        user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.role?.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="space-y-6">
            {/* Search */}
            <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                    <input
                        type="text"
                        placeholder="Search users by email or role..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full px-4 py-3 pl-12 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <svg className="w-5 h-5 text-gray-400 absolute left-4 top-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <div className="text-gray-400">
                    {filteredUsers.length} users
                </div>
            </div>

            {/* Users Table */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-white/5 border-b border-white/10">
                            <tr>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Email</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Role</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Institution</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Joined</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Admin</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/10">
                            {filteredUsers.map((user) => (
                                <tr key={user.id} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-sm font-bold">
                                                {user.email?.[0]?.toUpperCase()}
                                            </div>
                                            <span className="text-white">{user.email}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-sm">
                                            {user.role || 'N/A'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-gray-300">{user.institution || 'N/A'}</td>
                                    <td className="px-6 py-4 text-gray-400 text-sm">
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4">
                                        {user.is_admin ? (
                                            <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-lg text-sm font-semibold">
                                                Admin
                                            </span>
                                        ) : (
                                            <span className="text-gray-500 text-sm">User</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

// AI Responses Tab Component
function AIResponsesTab({ feedback, analytics }) {
    const [filterRating, setFilterRating] = useState('all') // 'all', 'likes', 'dislikes'

    const filteredFeedback = filterRating === 'all'
        ? feedback
        : feedback.filter(f => {
            if (filterRating === 'likes') return f.rating === 1
            if (filterRating === 'dislikes') return f.rating === -1
            return true
        })

    return (
        <div className="space-y-6">
            {/* Analytics Summary */}
            {analytics && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-xl">
                                💬
                            </div>
                            <div className="text-2xl font-bold text-white">{analytics.total || 0}</div>
                        </div>
                        <p className="text-gray-400 text-sm">Total Responses</p>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center text-xl">
                                👍
                            </div>
                            <div className="text-2xl font-bold text-green-400">{analytics.likes || 0}</div>
                        </div>
                        <p className="text-gray-400 text-sm">Likes</p>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-rose-500 rounded-lg flex items-center justify-center text-xl">
                                👎
                            </div>
                            <div className="text-2xl font-bold text-red-400">{analytics.dislikes || 0}</div>
                        </div>
                        <p className="text-gray-400 text-sm">Dislikes</p>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center text-xl">
                                📈
                            </div>
                            <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                                {analytics.satisfaction_rate || 0}%
                            </div>
                        </div>
                        <p className="text-gray-400 text-sm">Satisfaction</p>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="flex gap-3 overflow-x-auto pb-2">
                {['all', 'likes', 'dislikes'].map(rating => (
                    <button
                        key={rating}
                        onClick={() => setFilterRating(rating)}
                        className={`px-4 py-2 rounded-xl font-medium whitespace-nowrap transition-all ${
                            filterRating === rating
                                ? 'bg-purple-500 text-white'
                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                    >
                        {rating === 'all' ? 'All Responses' :
                         rating === 'likes' ? `👍 Liked (${analytics?.likes || 0})` :
                         `👎 Disliked (${analytics?.dislikes || 0})`}
                    </button>
                ))}
            </div>

            {/* AI Responses List */}
            <div className="space-y-4">
                {filteredFeedback.map((item) => (
                    <motion.div
                        key={item.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all"
                    >
                        {/* Rating Badge */}
                        <div className="flex items-start justify-between mb-4">
                            <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                                item.rating === 1
                                    ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                                    : 'bg-red-500/20 text-red-400 border border-red-500/50'
                            }`}>
                                {item.rating === 1 ? '👍 Helpful' : '👎 Not Helpful'}
                            </span>
                            <span className="text-gray-400 text-sm">
                                {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString()}
                            </span>
                        </div>

                        {/* Question */}
                        <div className="mb-4">
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-6 h-6 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-full flex items-center justify-center text-xs font-bold text-white">
                                    Q
                                </div>
                                <h4 className="text-cyan-400 font-semibold">User Question</h4>
                            </div>
                            <p className="text-gray-200 pl-8 bg-cyan-500/5 border-l-2 border-cyan-500 py-2 px-4 rounded-r-lg">
                                {item.query || 'No query provided'}
                            </p>
                        </div>

                        {/* Response */}
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-xs font-bold text-white">
                                    AI
                                </div>
                                <h4 className="text-purple-400 font-semibold">AI Response</h4>
                            </div>
                            <div className="text-gray-300 pl-8 bg-purple-500/5 border-l-2 border-purple-500 py-2 px-4 rounded-r-lg max-h-96 overflow-y-auto">
                                <p className="whitespace-pre-wrap">{item.response}</p>
                            </div>
                        </div>

                        {/* Comment if exists */}
                        {item.comment && (
                            <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                                <p className="text-sm text-yellow-400">
                                    <span className="font-semibold">Comment:</span> {item.comment}
                                </p>
                            </div>
                        )}

                        {/* User ID */}
                        <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
                            User ID: {item.user_id} • Message ID: {item.message_id}
                        </div>
                    </motion.div>
                ))}

                {filteredFeedback.length === 0 && (
                    <div className="text-center py-12 text-gray-400">
                        <div className="text-6xl mb-4">🤖</div>
                        <p className="text-lg">No AI responses found for this filter</p>
                    </div>
                )}
            </div>
        </div>
    )
}

// Feedback Tab Component
function FeedbackTab({ feedback }) {
    const [filterType, setFilterType] = useState('all')

    const filteredFeedback = filterType === 'all'
        ? feedback
        : feedback.filter(f => f.feedback_type === filterType)

    const types = ['all', 'bug', 'feature_request', 'improvement', 'praise', 'other']

    return (
        <div className="space-y-6">
            {/* Filters */}
            <div className="flex gap-3 overflow-x-auto pb-2">
                {types.map(type => (
                    <button
                        key={type}
                        onClick={() => setFilterType(type)}
                        className={`px-4 py-2 rounded-xl font-medium whitespace-nowrap transition-all ${
                            filterType === type
                                ? 'bg-purple-500 text-white'
                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                    >
                        {type === 'all' ? 'All' : type.replace('_', ' ').split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
                    </button>
                ))}
            </div>

            {/* Feedback List */}
            <div className="space-y-4">
                {filteredFeedback.map((item) => (
                    <motion.div
                        key={item.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="flex items-center gap-1">
                                    {[...Array(item.overall_rating)].map((_, i) => (
                                        <span key={i} className="text-yellow-400">⭐</span>
                                    ))}
                                </div>
                                <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                                    item.feedback_type === 'bug' ? 'bg-red-500/20 text-red-400' :
                                    item.feedback_type === 'feature_request' ? 'bg-purple-500/20 text-purple-400' :
                                    item.feedback_type === 'improvement' ? 'bg-blue-500/20 text-blue-400' :
                                    item.feedback_type === 'praise' ? 'bg-green-500/20 text-green-400' :
                                    'bg-gray-500/20 text-gray-400'
                                }`}>
                                    {item.feedback_type.replace('_', ' ')}
                                </span>
                            </div>
                            <span className="text-gray-400 text-sm">
                                {new Date(item.created_at).toLocaleDateString()}
                            </span>
                        </div>

                        {item.feedback_title && (
                            <h4 className="text-white font-semibold mb-2">{item.feedback_title}</h4>
                        )}

                        <p className="text-gray-300 mb-4">{item.feedback_message}</p>

                        {item.likes && (
                            <div className="mb-3">
                                <p className="text-sm text-gray-400 mb-1">Likes:</p>
                                <p className="text-green-400 text-sm">{item.likes}</p>
                            </div>
                        )}

                        {item.improvements && (
                            <div className="mb-3">
                                <p className="text-sm text-gray-400 mb-1">Improvements:</p>
                                <p className="text-orange-400 text-sm">{item.improvements}</p>
                            </div>
                        )}

                        {item.nps_score !== null && (
                            <div className="flex items-center gap-2 text-sm">
                                <span className="text-gray-400">NPS:</span>
                                <span className={`font-semibold ${
                                    item.nps_score >= 9 ? 'text-green-400' :
                                    item.nps_score >= 7 ? 'text-yellow-400' :
                                    'text-red-400'
                                }`}>
                                    {item.nps_score}/10
                                </span>
                            </div>
                        )}
                    </motion.div>
                ))}

                {filteredFeedback.length === 0 && (
                    <div className="text-center py-12 text-gray-400">
                        No feedback found for this filter
                    </div>
                )}
            </div>
        </div>
    )
}
