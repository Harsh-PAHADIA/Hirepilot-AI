import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import API_URL from "../lib/api"
import { FileText, Briefcase, Zap, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

export function PlacementAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [resumeText, setResumeText] = useState("Senior Frontend Developer with 5 years of experience building scalable web applications using React, TypeScript, and Node.js. Strong focus on UI/UX and performance optimization...")
  const [jdText, setJdText] = useState("Looking for a Lead UX Engineer. Required skills: React, Next.js, Framer Motion, Tailwind CSS, System Design, GraphQL. 6+ years experience preferred...")
  const [analysisResult, setAnalysisResult] = useState(null)

  const [errorMsg, setErrorMsg] = useState(null)

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setShowResults(false)
    setErrorMsg(null)
    
    try {
      const response = await axios.post(`${API_URL}/analyze`, {
        resume: resumeText,
        jd: jdText
      }, { timeout: 180000 })
      
      setAnalysisResult(response.data)
      setShowResults(true)
    } catch (error) {
      console.error("Error analyzing:", error)
      setErrorMsg("Failed to analyze profile. The server might be busy or unavailable. Please try again.")
    } finally {
      setIsAnalyzing(false)
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

  return (
    <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Placement Analysis</h2>
        <p className="text-muted-foreground mt-2">Compare your resume against a job description to get instant feedback and a match score.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.div variants={itemVariants}>
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Resume Content
              </CardTitle>
              <CardDescription>Paste your resume text or upload a document.</CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <textarea 
                className="w-full h-64 md:h-full min-h-[250px] rounded-md border border-input bg-background/50 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
                placeholder="Paste your resume here..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
              ></textarea>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-primary" />
                Job Description
              </CardTitle>
              <CardDescription>Paste the target job description.</CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <textarea 
                className="w-full h-64 md:h-full min-h-[250px] rounded-md border border-input bg-background/50 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
                placeholder="Paste job description here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
              ></textarea>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <motion.div variants={itemVariants} className="flex flex-col items-center py-4 space-y-3">
        <Button 
          size="lg" 
          onClick={handleAnalyze} 
          disabled={isAnalyzing}
          className="w-full md:w-auto px-8 relative overflow-hidden"
        >
          {isAnalyzing ? (
            <span className="flex items-center gap-2">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <Zap className="h-5 w-5" />
              </motion.div>
              Analyzing Profile...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              {errorMsg ? "Retry Analysis" : "Analyze Match"}
            </span>
          )}
        </Button>
        {errorMsg && (
          <div className="text-sm text-destructive flex items-center gap-2 bg-destructive/10 px-4 py-2 rounded-md border border-destructive/20">
            <AlertTriangle className="h-4 w-4" />
            {errorMsg}
          </div>
        )}
      </motion.div>

      <AnimatePresence>
        {showResults && analysisResult && (
          <motion.div 
            className="grid gap-6 md:grid-cols-3"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -40 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="md:col-span-1 border-primary/50 shadow-[0_0_15px_rgba(79,70,229,0.15)] relative overflow-hidden">
              {analysisResult.score?.score != null && (
                <div className="absolute top-0 right-0 p-4">
                  <Badge variant={analysisResult.score.score >= 80 ? "success" : analysisResult.score.score >= 60 ? "warning" : "destructive"}>
                    {analysisResult.score.score >= 80 ? "High Priority" : analysisResult.score.score >= 60 ? "Medium Priority" : "Low Priority"}
                  </Badge>
                </div>
              )}
              <CardHeader>
                <CardTitle>Match Score</CardTitle>
                <CardDescription>Overall compatibility</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center py-6">
                {analysisResult.score?.ai_error ? (
                  <p className="text-sm text-destructive text-center flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    {analysisResult.score.ai_error}
                  </p>
                ) : (
                  <>
                    <div className="relative flex items-center justify-center w-32 h-32 mb-4">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="64" cy="64" r="56" fill="transparent" stroke="currentColor" strokeWidth="12" className="text-secondary" />
                        <motion.circle
                          cx="64" cy="64" r="56" fill="transparent" stroke="currentColor" strokeWidth="12"
                          className="text-primary"
                          strokeDasharray={2 * Math.PI * 56}
                          initial={{ strokeDashoffset: 2 * Math.PI * 56 }}
                          animate={{ strokeDashoffset: 2 * Math.PI * 56 * (1 - ((analysisResult.score?.score ?? 0) / 100)) }}
                          transition={{ duration: 1.5, ease: "easeOut" }}
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center">
                        <span className="text-3xl font-bold">{analysisResult.score?.score ?? '—'}%</span>
                      </div>
                    </div>
                    {analysisResult.score?.reason && (
                      <p className="text-center text-sm text-muted-foreground mt-2">{analysisResult.score.reason}</p>
                    )}
                  </>
                )}
              </CardContent>
            </Card>

            <div className="md:col-span-2 space-y-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-warning" />
                    Missing Skills & Keywords
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {analysisResult.gap_analysis?.ai_error ? (
                    <p className="text-sm text-destructive flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 shrink-0" />
                      {analysisResult.gap_analysis.ai_error}
                    </p>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {(analysisResult.gap_analysis?.missing_skills?.length > 0
                        ? analysisResult.gap_analysis.missing_skills
                        : analysisResult.score?.missing_skills
                      )?.map((skill, i) => (
                        <Badge key={i} variant="outline" className="border-warning/50 text-warning bg-warning/10">{skill}</Badge>
                      ))}
                      {!analysisResult.gap_analysis?.missing_skills?.length && !analysisResult.score?.missing_skills?.length && (
                        <span className="text-sm text-muted-foreground">No critical missing skills detected.</span>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-success" />
                    Actionable Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {analysisResult.plan?.ai_error ? (
                    <p className="text-sm text-destructive flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 shrink-0" />
                      {analysisResult.plan.ai_error}
                    </p>
                  ) : !analysisResult.plan?.today?.length && !analysisResult.plan?.this_week?.length ? (
                    <p className="text-sm text-muted-foreground">No recommendations generated.</p>
                  ) : (
                    <ul className="space-y-3">
                      {analysisResult.plan?.today?.map((action, i) => (
                        <li key={`today-${i}`} className="flex items-start gap-2 text-sm">
                          <ArrowRight className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                          <span>{action}</span>
                        </li>
                      ))}
                      {analysisResult.plan?.this_week?.map((action, i) => (
                        <li key={`week-${i}`} className="flex items-start gap-2 text-sm">
                          <ArrowRight className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
