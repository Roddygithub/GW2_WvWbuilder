import { z } from "zod"
import type { Composition } from "@/types/squad"

export const playstyleOptions = [
  "balanced",
  "offensive",
  "defensive",
  "zerg",
  "havoc",
] as const

export const compositionFormSchema = z.object({
  name: z.string().min(1, "Le nom est requis").max(100, "Le nom est trop long"),
  description: z.string().max(500, "La description est trop longue").optional(),
  playstyle: z.enum(playstyleOptions, {
    required_error: "Veuillez sélectionner un style de jeu",
  }),
  squad_size: z.coerce
    .number()
    .int("Doit être un nombre entier")
    .min(1, "La taille minimale est de 1")
    .max(100, "La taille maximale est de 100"),
  professions: z
    .array(z.string())
    .min(1, "Au moins une profession est requise")
    .max(50, "Trop de professions"),
})

export type CompositionFormValues = z.infer<typeof compositionFormSchema>

export const defaultValues: Partial<CompositionFormValues> = {
  name: "",
  description: "",
  playstyle: "balanced",
  squad_size: 10,
  professions: [],
}

export function toFormValues(composition: Composition): CompositionFormValues {
  return {
    name: composition.name,
    description: composition.description || "",
    playstyle: composition.playstyle,
    squad_size: composition.squad_size,
    professions: [...composition.professions],
  }
}

export function toComposition(
  data: CompositionFormValues,
  id?: number
): Omit<Composition, "id" | "created_at" | "updated_at"> & { id?: number } {
  return {
    ...(id && { id }),
    name: data.name,
    description: data.description || null,
    playstyle: data.playstyle,
    squad_size: data.squad_size,
    professions: [...data.professions],
  }
}
