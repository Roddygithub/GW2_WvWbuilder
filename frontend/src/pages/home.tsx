import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-5xl">
        Optimize Your WvW Squad
      </h1>
      <p className="mb-8 max-w-2xl text-lg text-muted-foreground">
        Create, optimize, and share the perfect WvW squad compositions for Guild
        Wars 2. Maximize your team's potential with data-driven insights and
        recommendations.
      </p>
      <div className="flex gap-4">
        <Button asChild size="lg">
          <Link to="/builder">Get Started</Link>
        </Button>
        <Button variant="outline" size="lg" asChild>
          <Link to="/about">Learn More</Link>
        </Button>
      </div>

      <div className="mt-16 grid w-full max-w-5xl grid-cols-1 gap-8 md:grid-cols-3">
        <div className="rounded-lg border p-6 text-left">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-primary"
            >
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          </div>
          <h3 className="mb-2 text-lg font-semibold">Build Compositions</h3>
          <p className="text-sm text-muted-foreground">
            Create and customize squad compositions for groups of 2 to 20
            players with an intuitive interface.
          </p>
        </div>

        <div className="rounded-lg border p-6 text-left">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-primary"
            >
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
              <line x1="12" y1="22.08" x2="12" y2="12" />
            </svg>
          </div>
          <h3 className="mb-2 text-lg font-semibold">Optimize Roles</h3>
          <p className="text-sm text-muted-foreground">
            Get intelligent suggestions for role distribution based on
            profession synergies and WvW meta.
          </p>
        </div>

        <div className="rounded-lg border p-6 text-left">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-primary"
            >
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <h3 className="mb-2 text-lg font-semibold">Share & Collaborate</h3>
          <p className="text-sm text-muted-foreground">
            Share your compositions with your guild or group and get feedback
            from the community.
          </p>
        </div>
      </div>
    </div>
  );
}
