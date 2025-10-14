import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"

export default function CompositionsPage() {
  // This would come from an API in a real application
  const compositions = [
    {
      id: 1,
      name: "Balanced Zerg",
      size: 50,
      lastUpdated: "2025-08-28",
      author: "Commander X",
      likes: 42,
    },
    {
      id: 2,
      name: "Havoc Squad",
      size: 10,
      lastUpdated: "2025-08-27",
      author: "Scout Y",
      likes: 28,
    },
    {
      id: 3,
      name: "Defensive Keep Defense",
      size: 15,
      lastUpdated: "2025-08-26",
      author: "Defender Z",
      likes: 15,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between space-y-4 sm:flex-row sm:items-center sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Saved Compositions</h2>
          <p className="text-muted-foreground">
            Browse and manage your saved squad compositions
          </p>
        </div>
        <Button>Create New</Button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search compositions..."
          className="w-full pl-10 md:w-[300px]"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {compositions.map((comp) => (
          <div key={comp.id} className="rounded-lg border p-6 transition-colors hover:bg-accent/50">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-medium">{comp.name}</h3>
                <p className="text-sm text-muted-foreground">{comp.size} players • {comp.lastUpdated}</p>
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <span className="sr-only">Like</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-4 w-4"
                >
                  <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
                </svg>
              </Button>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm text-muted-foreground">By {comp.author}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">{comp.likes} likes</span>
                <Button variant="outline" size="sm">View</Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
