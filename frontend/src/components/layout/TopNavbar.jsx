import React, { useState } from 'react'
import { Bell, Search, UserCircle } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { AnimatePresence, motion } from 'framer-motion'

export function TopNavbar() {
  const [toastMessage, setToastMessage] = useState(null)

  const showToast = (msg) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 3000)
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6 relative">
      <div className="flex w-full max-w-md items-center gap-2">
        <Search className="h-4 w-4 text-muted-foreground absolute ml-3" />
        <Input 
          type="search" 
          placeholder="Search (Coming Soon)" 
          className="pl-10 w-full bg-card cursor-not-allowed opacity-70"
          disabled
          onClick={() => showToast("Search functionality will be available in a future update.")}
        />
      </div>
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="relative" onClick={() => showToast("Notifications coming soon.")}>
          <Bell className="h-5 w-5 text-muted-foreground" />
        </Button>
        <div className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
          <UserCircle className="h-8 w-8 text-muted-foreground" />
          <div className="hidden md:flex flex-col items-start">
            <span className="text-sm font-medium leading-none">Alex Mercer</span>
            <span className="text-xs text-muted-foreground mt-1">Product Manager</span>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {toastMessage && (
          <motion.div 
            initial={{ opacity: 0, y: -20, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: -20, x: '-50%' }}
            className="absolute top-14 left-1/2 -translate-x-1/2 bg-card border border-border shadow-lg px-4 py-2 rounded-md z-50 text-sm font-medium"
          >
            {toastMessage}
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
