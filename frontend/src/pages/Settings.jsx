import React from 'react'
import { motion } from 'framer-motion'
import { User, Bell, Shield, Paintbrush } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function Settings() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  }

  return (
    <motion.div 
      className="space-y-6 max-w-4xl mx-auto"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground mt-2">Manage your account settings and preferences.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <div className="md:col-span-1 space-y-2">
          <Button variant="secondary" className="w-full justify-start">
            <User className="mr-2 h-4 w-4" />
            Profile
          </Button>
          <Button variant="ghost" className="w-full justify-start cursor-not-allowed opacity-70" disabled>
            <Bell className="mr-2 h-4 w-4" />
            Notifications <span className="ml-auto text-[10px] bg-muted px-1.5 py-0.5 rounded">Coming Soon</span>
          </Button>
          <Button variant="ghost" className="w-full justify-start cursor-not-allowed opacity-70" disabled>
            <Paintbrush className="mr-2 h-4 w-4" />
            Appearance <span className="ml-auto text-[10px] bg-muted px-1.5 py-0.5 rounded">Coming Soon</span>
          </Button>
          <Button variant="ghost" className="w-full justify-start cursor-not-allowed opacity-70" disabled>
            <Shield className="mr-2 h-4 w-4" />
            Security <span className="ml-auto text-[10px] bg-muted px-1.5 py-0.5 rounded">Coming Soon</span>
          </Button>
        </div>
        
        <div className="md:col-span-3 space-y-6">
          <motion.div variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your personal details and public profile.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Full Name
                  </label>
                  <Input defaultValue="Alex Mercer" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Email Address
                  </label>
                  <Input defaultValue="alex@example.com" type="email" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Professional Title
                  </label>
                  <Input defaultValue="Product Manager" />
                </div>
                <Button onClick={() => alert("Profile updated successfully.")}>Save Changes</Button>
              </CardContent>
            </Card>
          </motion.div>
          
          <motion.div variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle>Account Preferences</CardTitle>
                <CardDescription>Manage your default application tracking settings.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between rounded-lg border p-4 opacity-70">
                  <div className="space-y-0.5">
                    <label className="text-base font-medium flex items-center gap-2">Weekly Reports <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground">Coming Soon</span></label>
                    <p className="text-sm text-muted-foreground">Receive a weekly summary of your job search progress.</p>
                  </div>
                  <div className="h-6 w-11 rounded-full bg-muted relative cursor-not-allowed">
                    <div className="absolute left-1 top-1 h-4 w-4 rounded-full bg-muted-foreground transition-transform"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
