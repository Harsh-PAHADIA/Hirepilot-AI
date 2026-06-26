import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import API_URL from "../lib/api"
import { GripVertical, Clock, CheckCircle2, Calendar, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const initialColumns = {
  today: {
    id: 'today',
    title: 'Today',
    icon: Clock,
    color: 'text-warning',
    tasks: []
  },
  thisWeek: {
    id: 'thisWeek',
    title: 'This Week',
    icon: Calendar,
    color: 'text-primary',
    tasks: []
  },
  completed: {
    id: 'completed',
    title: 'Completed',
    icon: CheckCircle2,
    color: 'text-success',
    tasks: []
  }
}

export function ActionCenter() {
  const [loading, setLoading] = useState(true)
  const [columns, setColumns] = useState(initialColumns)
  const [draggedTask, setDraggedTask] = useState(null)
  const [sourceColumnId, setSourceColumnId] = useState(null)

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/tasks`)
        const data = response.data
        
        setColumns(prev => ({
          today: { ...prev.today, tasks: data.today || [] },
          thisWeek: { ...prev.thisWeek, tasks: data.thisWeek || [] },
          completed: { ...prev.completed, tasks: data.completed || [] }
        }))
      } catch (error) {
        console.error("Error fetching tasks:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchTasks()
  }, [])

  const handleDragStart = (e, task, columnId) => {
    setDraggedTask(task)
    setSourceColumnId(columnId)
    // For Firefox compatibility
    e.dataTransfer.setData('text/plain', task.id)
    e.dataTransfer.effectAllowed = 'move'
    
    // Add visual feedback
    setTimeout(() => {
      e.target.style.opacity = '0.5'
    }, 0)
  }

  const handleDragEnd = (e) => {
    e.target.style.opacity = '1'
    setDraggedTask(null)
    setSourceColumnId(null)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = async (e, targetColumnId) => {
    e.preventDefault()
    if (!draggedTask || sourceColumnId === targetColumnId) return

    // Optimistic update
    setColumns(prev => {
      const sourceCol = prev[sourceColumnId]
      const targetCol = prev[targetColumnId]

      const sourceTasks = sourceCol.tasks.filter(t => t.id !== draggedTask.id)
      const targetTasks = [...targetCol.tasks, draggedTask]

      return {
        ...prev,
        [sourceColumnId]: { ...sourceCol, tasks: sourceTasks },
        [targetColumnId]: { ...targetCol, tasks: targetTasks }
      }
    })
    
    try {
      await axios.put(`${API_URL}/tasks/${draggedTask.db_id}/status`, { column_status: targetColumnId })
    } catch (error) {
      console.error("Error updating task status:", error)
      // On error, reload page or revert state (simplest is alert for hackathon)
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  }

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <motion.div 
      className="space-y-6 h-full flex flex-col"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Action Center</h2>
        <p className="text-muted-foreground mt-2">Manage your job search tasks with this Kanban board.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1 min-h-0">
        {Object.values(columns).map((column) => {
          const Icon = column.icon
          return (
            <motion.div key={column.id} variants={itemVariants} className="h-full flex flex-col">
              <div className="flex items-center gap-2 mb-4">
                <Icon className={`h-5 w-5 ${column.color}`} />
                <h3 className="font-semibold">{column.title}</h3>
                <Badge variant="secondary" className="ml-auto">{column.tasks.length}</Badge>
              </div>
              
              <div 
                className="flex-1 bg-card/50 rounded-lg p-4 border border-border/50 overflow-y-auto space-y-3"
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, column.id)}
              >
                {column.tasks.map((task) => (
                  <div
                    key={task.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, task, column.id)}
                    onDragEnd={handleDragEnd}
                    className="bg-card p-3 rounded-md border border-border shadow-sm cursor-grab active:cursor-grabbing hover:border-primary/50 transition-colors"
                  >
                    <div className="flex items-start gap-2">
                      <GripVertical className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5 opacity-50" />
                      <div className="flex-1 space-y-2">
                        <p className="text-sm font-medium leading-tight">{task.title}</p>
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                            {task.tag}
                          </Badge>
                          <span className="text-[10px] text-muted-foreground">{task.time}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {column.tasks.length === 0 && (
                  <div className="h-24 flex items-center justify-center text-sm text-muted-foreground border-2 border-dashed border-border rounded-md px-4 text-center">
                    {column.id === 'completed' ? "Completed tasks will appear here" : "Drop tasks here"}
                  </div>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}
