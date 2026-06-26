import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import API_URL from "../lib/api"
import { 
  Users, Briefcase, TrendingUp, Calendar, 
  Activity, Loader2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'

export function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState({
    kpi: {
      total_applications: 0,
      high_priority_jobs: 0,
      average_match_score: 0,
      upcoming_interviews: 0
    },
    status_distribution: {},
    match_trend: []
  })
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, tasksRes] = await Promise.all([
          axios.get(`${API_URL}/analytics`),
          axios.get(`${API_URL}/tasks`)
        ])
        
        setData(analyticsRes.data)
        setTasks(tasksRes.data.today || [])
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const kpiData = [
    { title: 'Total Applications', value: data.kpi.total_applications, icon: Users, color: 'text-primary' },
    { title: 'High Priority Jobs', value: data.kpi.high_priority_jobs, icon: Briefcase, color: 'text-warning' },
    { title: 'Average Match', value: `${data.kpi.average_match_score}%`, icon: TrendingUp, color: 'text-success' },
    { title: 'Upcoming Interviews', value: data.kpi.upcoming_interviews, icon: Calendar, color: 'text-primary' },
  ]

  const statusColors = {
    'Saved': '#64748B',
    'Applied': '#3B82F6',
    'Online Assessment': '#8B5CF6',
    'Interview': '#F59E0B',
    'Final Round': '#F97316',
    'Offer': '#22C55E',
    'Rejected': '#EF4444'
  }

  const statusData = Object.keys(data.status_distribution).map(key => ({
    name: key,
    value: data.status_distribution[key],
    color: statusColors[key] || '#94A3B8'
  }))

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  }

  return (
    <motion.div 
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground mt-2">Welcome back. Here's an overview of your job search progress.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {kpiData.map((kpi, index) => {
          const Icon = kpi.icon
          return (
            <motion.div key={index} variants={itemVariants}>
              <Card className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {kpi.title}
                  </CardTitle>
                  <Icon className={`h-4 w-4 ${kpi.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpi.value}</div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <motion.div className="col-span-4" variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Match Score Trend</CardTitle>
              <CardDescription>Average match score progression over recent analyses.</CardDescription>
            </CardHeader>
            <CardContent className="pl-0 h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.match_trend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#4F46E5" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1E293B" />
                  <XAxis dataKey="month" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: '#151B2E', borderColor: '#1E293B', color: '#FFF' }}
                    itemStyle={{ color: '#4F46E5' }}
                  />
                  <Area type="monotone" dataKey="score" stroke="#4F46E5" strokeWidth={2} fillOpacity={1} fill="url(#colorScore)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div className="col-span-3" variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Application Pipeline</CardTitle>
              <CardDescription>Current distribution of your applications.</CardDescription>
            </CardHeader>
            <CardContent className="h-[300px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                {statusData.length > 0 ? (
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#151B2E', borderColor: '#1E293B', color: '#FFF', borderRadius: '8px' }}
                      itemStyle={{ color: '#FFF' }}
                    />
                  </PieChart>
                ) : (
                  <div className="text-muted-foreground flex items-center justify-center h-full">No active applications</div>
                )}
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Action Center Tasks (Today)</CardTitle>
            <CardDescription>Generated from your application gap analyses.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {tasks.map((task, index) => {
                return (
                  <div key={index} className="flex items-center gap-4">
                    <div className={`p-2 rounded-full bg-primary/10 text-primary`}>
                      <Activity className="h-4 w-4" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">{task.title}</p>
                      {task.application_company && (
                        <p className="text-xs text-muted-foreground">{task.application_company}</p>
                      )}
                    </div>
                  </div>
                )
              })}
              {tasks.length === 0 && (
                <div className="text-muted-foreground text-sm">No pending tasks for today. Check your Action Center or analyze a new job description!</div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
