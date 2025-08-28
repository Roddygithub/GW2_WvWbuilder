import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center space-x-6">
          <Link to="/" className="flex items-center space-x-2">
            <span className="inline-block font-bold text-xl">GW2 WvW Builder</span>
          </Link>
        </div>
        <div className="flex items-center space-x-2">
          <ThemeToggle />
          <Button variant="outline" size="sm" asChild>
            <a 
              href="https://github.com/yourusername/gw2-wvwbuilder" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </Button>
        </div>
      </div>
    </header>
  )
}
