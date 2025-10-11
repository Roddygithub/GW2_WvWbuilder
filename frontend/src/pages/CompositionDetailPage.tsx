import React from "react";
import { deleteComposition, getCompositionById } from "@/api/compositions";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle, // Corrected import
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { PROFESSIONS_DATA, ALL_ROLES } from "@/data/professions";
import { cn } from "@/lib/utils";
import type { Role } from "@/types/squad";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"; // Corrected import
import { format } from "date-fns";
import {
  ArrowLeft,
  Download,
  Loader2,
  Pencil,
  Shield,
  Swords,
  Trash2,
  Users,
} from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"; 
import { useToast } from "@/hooks/use-toast";

export default function CompositionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    data: composition,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["composition", id],
    queryFn: () => getCompositionById(id!),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteComposition,
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Composition deleted successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["compositions"] });
      navigate("/compositions");
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    },
  });

  const handleDelete = () => {
    if (composition) {
      deleteMutation.mutate(composition.id);
    }
  };

  const handleExportJson = () => {
    if (!composition) return;
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(composition, null, 2)
    )}`;
    const link = document.createElement("a");
    link.href = jsonString;
    const safeName = composition.name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    link.download = `${safeName}_composition.json`;

    link.click();
    toast({
      title: "Success",
      description: "Composition exported as JSON.",
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-6 w-full" />
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
    );
  }

  if (isError || !composition) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-semibold text-destructive">Composition not found</h2>
        <p className="text-muted-foreground">The requested composition could not be loaded.</p>
        <Button asChild variant="link" className="mt-4">
          <Link to="/compositions">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to compositions
          </Link>
        </Button>
      </div>
    );
  }

  const PlaystyleIcon = {
    offensive: <Swords className="mr-2 h-4 w-4" />,
    defensive: <Shield className="mr-2 h-4 w-4" />,
    balanced: <Users className="mr-2 h-4 w-4" />,
    zerg: <Users className="mr-2 h-4 w-4" />,
    havoc: <Users className="mr-2 h-4 w-4" />,
  }[composition.playstyle] || <Users className="mr-2 h-4 w-4" />;

  const roleCounts = React.useMemo(() => {
    if (!composition?.professions) return [];

    const counts = {} as Record<Role, number>;
    ALL_ROLES.forEach(r => counts[r] = 0);

    for (const prof of composition.professions) {
      PROFESSIONS_DATA[prof]?.roles.forEach((role) => {
        if (counts[role] !== undefined) counts[role]++;
      });
    }

    // Format for Recharts
    return ALL_ROLES.map(role => ({ name: role, count: counts[role] || 0 }));
  }, [composition?.professions]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div>
          <Button asChild variant="ghost" className="-ml-4 mb-2">
            <Link to="/compositions"><ArrowLeft className="mr-2 h-4 w-4" />Back to list</Link>
          </Button>
          <h2 className="text-3xl font-bold tracking-tight">{composition.name}</h2>
          <p className="text-muted-foreground">
            Created on {format(new Date(composition.created_at), "PPP")}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportJson}>
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
          <Link to="/builder" state={{ composition }} className={cn(buttonVariants({ variant: "outline" }))}>
            <Pencil className="mr-2 h-4 w-4" /> Edit
          </Link>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" disabled={deleteMutation.isPending}>
                {deleteMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
                Delete
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete your
                  composition.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete} className={cn(buttonVariants({ variant: "destructive" }))}>
                  Continue
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <Badge variant="outline" className="text-sm"><Users className="mr-2 h-4 w-4" />{composition.squad_size} Players</Badge>
        <Badge variant="outline" className="text-sm capitalize">{PlaystyleIcon}{composition.playstyle}</Badge>
      </div>

      {composition.description && (
        <div className="rounded-lg border bg-muted/50 p-6">
          <h3 className="mb-2 text-lg font-medium">Description</h3>
          <p className="text-muted-foreground">
            {composition.description}
          </p>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border p-6">
          <h3 className="mb-4 text-lg font-medium">Professions</h3>
          <div className="flex flex-wrap gap-2">
            {composition.professions?.map((prof, index) => <Badge key={index}>{prof}</Badge>)}
          </div>
        </div>

        <div className="rounded-lg border p-6">
          <h3 className="mb-4 text-lg font-medium">Role Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={roleCounts} layout="vertical" margin={{ left: 10, right: 30 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                cursor={{ fill: "hsl(var(--muted))" }}
                contentStyle={{ backgroundColor: "hsl(var(--background))", border: "1px solid hsl(var(--border))" }}
              />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}