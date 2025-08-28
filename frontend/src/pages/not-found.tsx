import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"

export default function NotFoundPage() {
  return (
    <div className="flex h-[calc(100vh-200px)] flex-col items-center justify-center space-y-4 text-center">
      <h1 className="text-6xl font-bold tracking-tight text-muted-foreground">404</h1>
      <h2 className="text-2xl font-semibold">Page Not Found</h2>
      <p className="max-w-md text-muted-foreground">
        The page you're looking for doesn't exist or has been moved. Let's get you back on track.
      </p>
      <Button asChild className="mt-4">
        <Link to="/">Return Home</Link>
      </Button>
    </div>
  )
}
