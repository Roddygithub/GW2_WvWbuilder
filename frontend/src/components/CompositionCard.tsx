import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@lib/utils";
import type { Composition } from "@/types/squad";
import { formatDistanceToNow } from "date-fns";
import { Link } from "react-router-dom";

interface CompositionCardProps {
  composition: Composition;
}

export function CompositionCard({ composition }: CompositionCardProps) {
  const lastUpdated = formatDistanceToNow(new Date(composition.updated_at), {
    addSuffix: true,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{composition.name}</CardTitle>
        <CardDescription>
          {composition.description || "No description available."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          {composition.squad_size} players • Last updated {lastUpdated}
        </p>
      </CardContent>
      <CardFooter className="flex justify-end">
        <Link
          to={`/compositions/${composition.id}`}
          className={cn(buttonVariants({ variant: "outline" }))}
        >
          View
        </Link>
      </CardFooter>
    </Card>
  );
}
