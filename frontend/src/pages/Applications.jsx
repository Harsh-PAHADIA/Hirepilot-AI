import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { Search, Filter, ArrowUpDown, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

export function Applications() {
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'priority_score', direction: 'desc' })
  const [applications, setApplications] = useState([])

  const fetchApplications = async () => {
    try {
      const response = await axios.get('http://localhost:8000/applications')
      setApplications(response.data)
    } catch (error) {
      console.error("Error fetching applications:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchApplications()
  }, [])

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    })
  }

  const handleStatusChange = async (appId, newStatus) => {
    // Optimistic update
    setApplications(apps => apps.map(app => 
      app.id === appId ? { ...app, status: newStatus } : app
    ))
    
    try {
      await axios.put(`http://localhost:8000/applications/${appId}/status`, { status: newStatus })
    } catch (error) {
      console.error("Error updating status:", error)
      // Revert on error by refetching
      fetchApplications()
    }
  }

  const getStatusBadgeVariant = (status) => {
    if (status === 'Offer' || status === 'Selected') return 'success'
    if (status === 'Interview' || status === 'Final Round') return 'warning'
    if (status === 'Rejected') return 'destructive'
    if (status === 'Applied' || status === 'Online Assessment') return 'default'
    return 'secondary' // Saved
  }

  const getPriorityBadgeVariant = (priority_level) => {
    if (priority_level === 'High') return 'destructive'
    if (priority_level === 'Medium') return 'warning'
    return 'secondary' // Low
  }

  const filteredData = applications
    .filter(app => 
      app.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.role.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? -1 : 1
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? 1 : -1
      }
      return 0
    })

  const PIPELINE_STATUSES = [
    'Saved', 'Applied', 'Online Assessment', 'Interview', 'Final Round', 'Offer', 'Rejected'
  ]

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <motion.div 
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Applications</h2>
        <p className="text-muted-foreground mt-2">Manage and track your active job applications.</p>
      </div>

      <Card>
        <CardHeader className="pb-4">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <CardTitle>All Applications</CardTitle>
            <div className="flex items-center gap-2 w-full md:w-auto">
              <div className="relative w-full md:w-64">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search company or role..."
                  className="pl-9"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Company</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead className="text-right">
                  <Button variant="ghost" className="h-8 hover:bg-transparent px-0 font-medium" onClick={() => handleSort('priority_score')}>
                    Match Score
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.map((app) => (
                <TableRow key={app.id} className="group transition-colors duration-200">
                  <TableCell className="font-medium">{app.company}</TableCell>
                  <TableCell>{app.role}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Badge variant={getStatusBadgeVariant(app.status)} className="w-24 justify-center">
                        {app.status}
                      </Badge>
                      <select 
                        className="bg-transparent text-xs text-muted-foreground border border-border rounded px-1 py-0.5 outline-none focus:ring-1 focus:ring-primary opacity-0 group-hover:opacity-100 transition-opacity"
                        value={app.status}
                        onChange={(e) => handleStatusChange(app.id, e.target.value)}
                      >
                        {PIPELINE_STATUSES.map(s => (
                          <option key={s} value={s} className="bg-card text-foreground">{s}</option>
                        ))}
                      </select>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getPriorityBadgeVariant(app.priority_level)} className="bg-opacity-20 bg-transparent border-current">
                      {app.priority_level}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <span className="font-semibold">{app.priority_score}%</span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {filteredData.length === 0 && (
            <div className="py-12 text-center text-muted-foreground">
              No applications found matching your search.
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
