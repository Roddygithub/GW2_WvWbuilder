import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate, useParams } from "react-router-dom"
import { Loader2 } from "lucide-react"

import { CompositionForm } from "@/components/form/CompositionForm"
import { useToast } from "@/components/ui/use-toast"
import {
  getCompositionById,
  createComposition,
  updateComposition,
} from "@/api/compositions"
import { toFormValues } from "@/schemas/composition.schema"

export default function EditCompositionPage() {
  const { id } = useParams<{ id?: string }>()
  const isEditing = !!id
  const { toast } = useToast()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Récupérer la composition existante si en mode édition
  const { data: existingComposition, isLoading } = useQuery({
    queryKey: ["composition", id],
    queryFn: () => getCompositionById(id!), // L'assertion non-null est sûre car la requête est désactivée si id est undefined
    enabled: isEditing,
  })

  const createMutation = useMutation({
    mutationFn: createComposition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compositions"] })
      navigate("/compositions")
    },
  })

  const updateMutation = useMutation({
    mutationFn: async (data: Parameters<typeof updateComposition>[1]) => {
      if (!id) throw new Error("ID de composition manquant")
      return updateComposition(parseInt(id, 10), data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compositions"] })
      queryClient.invalidateQueries({ queryKey: ["composition", id] })
      navigate(`/compositions/${id}`)
    },
  })

  const handleSubmit = async (data: any) => {
    try {
      if (isEditing) {
        await updateMutation.mutateAsync(data)
      } else {
        await createMutation.mutateAsync(data)
      }
      
      toast({
        title: "Succès",
        description: `La composition a été ${isEditing ? 'mise à jour' : 'créée'} avec succès.`,
      })
    } catch (error) {
      console.error("Erreur lors de l'enregistrement :", error)
      throw error // Laisser le formulaire gérer l'erreur
    }
  }

  if (isLoading && isEditing) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="sr-only">Chargement...</span>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">
          {isEditing ? "Modifier la composition" : "Nouvelle composition"}
        </h1>
        <p className="text-muted-foreground">
          {isEditing
            ? "Modifiez les détails de votre composition existante."
            : "Créez une nouvelle composition pour votre escouade WvW."}
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <CompositionForm
          defaultValues={
            isEditing && existingComposition
              ? toFormValues(existingComposition)
              : undefined
          }
          onSubmit={handleSubmit}
          isSubmitting={createMutation.isPending || updateMutation.isPending}
          submitLabel={
            isEditing
              ? updateMutation.isPending
                ? "Enregistrement..."
                : "Mettre à jour"
              : createMutation.isPending
              ? "Création..."
              : "Créer la composition"
          }
        />
      </div>
    </div>
  )
}
