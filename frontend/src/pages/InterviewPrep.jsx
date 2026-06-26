import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import API_URL from "../lib/api"
import { Code2, Database, Users, Building2, ChevronRight, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'

const IconMap = {
  Code2: Code2,
  Database: Database,
  Users: Users,
  Building2: Building2
}

export function InterviewPrep() {
  const [loading, setLoading] = useState(true)
  const [prepCategories, setPrepCategories] = useState([])
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    const fetchPrep = async () => {
      try {
        const response = await axios.get(`${API_URL}/interview-prep`)
        const data = Array.isArray(response.data) ? response.data : []
        setPrepCategories(data.filter(c => c && typeof c === 'object'))
      } catch (error) {
        console.error("Error fetching interview prep:", error)
        setPrepCategories([]) // Fallback to empty state
      } finally {
        setLoading(false)
      }
    }
    fetchPrep()
  }, [])

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

  if (!Array.isArray(prepCategories) || prepCategories.length === 0) {
    return (
      <div className="flex flex-col h-[80vh] items-center justify-center space-y-4">
        <h2 className="text-2xl font-bold tracking-tight">No Interview Prep Available</h2>
        <p className="text-muted-foreground">Run a Resume Analysis to generate personalized questions.</p>
      </div>
    )
  }

  return (
    <motion.div 
      className="space-y-6 max-w-5xl mx-auto"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Interview Prep</h2>
        <p className="text-muted-foreground mt-2">Practice curated questions tailored to your upcoming interviews and skill gaps.</p>
      </div>

      {prepCategories.every(c => !Array.isArray(c.questions) || c.questions.length === 0) ? (
        <div className="flex flex-col py-12 items-center justify-center border-2 border-dashed border-border rounded-lg bg-card/50">
          <p className="text-muted-foreground text-center">No interview questions could be generated from the last analysis.<br/>Please try analyzing a different resume and job description.</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {prepCategories.map((category, catIndex) => {
            const Icon = IconMap[category.icon_name] || Code2
            const questions = Array.isArray(category.questions) ? category.questions : []
            
            if (questions.length === 0) return null;

            return (
              <motion.div key={category.id || catIndex} variants={itemVariants}>
                <Card className="h-full border-border/50 hover:border-border transition-colors">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-md bg-primary/10 text-primary">
                        <Icon className="h-6 w-6" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{category.title || "Category"}</CardTitle>
                        <CardDescription>{category.description || "Practice questions"}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Accordion type="single" collapsible className="w-full">
                      {questions.map((item, index) => (
                        <AccordionItem key={index} value={`item-${index}`} className="border-border/50 border-b last:border-0">
                          <AccordionTrigger className="hover:no-underline hover:text-primary transition-colors text-left py-3">
                            <div className="flex flex-col md:flex-row md:items-center justify-between w-full pr-4 gap-2">
                              <span className="text-sm font-medium pr-2">{item.q || item.question || "Practice Question"}</span>
                              <div className="flex items-center gap-2 shrink-0">
                                {item.company && (
                                  <span className="text-xs text-primary/80 bg-primary/10 px-2 py-1 rounded whitespace-nowrap">
                                    {item.company}
                                  </span>
                                )}
                                <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded whitespace-nowrap">
                                  {item.difficulty || "Medium"}
                                </span>
                              </div>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent className="text-muted-foreground pl-4 border-l-2 border-primary/20 ml-2 mt-2">
                            <p className="mb-2">Suggested approach:</p>
                            <ul className="list-disc pl-4 space-y-1">
                              <li>Identify the core problem constraints.</li>
                              <li>Discuss naive solution first to establish baseline.</li>
                              <li>Optimize for time/space complexity.</li>
                              <li>Test with edge cases.</li>
                            </ul>
                            <div 
                              className="mt-4 flex w-fit items-center text-primary/60 text-sm font-medium cursor-pointer bg-primary/5 px-3 py-1.5 rounded-md hover:bg-primary/10 transition-colors"
                              onClick={() => setShowModal(true)}
                            >
                              View full solution <ChevronRight className="h-4 w-4 ml-1" />
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>
      )}

      <AnimatePresence>
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-card border border-border shadow-lg p-6 rounded-lg max-w-md w-full mx-4 relative"
            >
              <h3 className="text-xl font-semibold mb-2">Coming Soon</h3>
              <p className="text-muted-foreground mb-6">Detailed AI solutions are coming soon.</p>
              <div className="flex justify-end">
                <Button onClick={() => setShowModal(false)}>Close</Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
