import { useForm, useFormContext } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate } from "react-router-dom"
import { Loader2 } from "lucide-react"
import * as React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ProfessionSelect } from "./ProfessionSelect"
import {
  compositionFormSchema,
  type CompositionFormValues,
  playstyleOptions,
} from "@/schemas/composition.schema"

// Composants de formulaire personnalisés
interface FormFieldProps {
  name: keyof CompositionFormValues
  children: (props: { field: any }) => React.ReactNode
}

const FormField = ({ 
  name, 
  children 
}: FormFieldProps) => {
  const { register } = useFormContext<CompositionFormValues>()
  return <>{children({ field: { ...register(name) } })}</>
}

const FormItem = ({ children }: { children: React.ReactNode }) => (
  <div className="space-y-2">{children}</div>
)

const FormLabel = ({
  children,
  className = "",
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>) => (
  <label
    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
    {...props}
  >
    {children}
  </label>
)

const FormControl = ({
  children,
  className = "",
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={className} {...props}>
    {children}
  </div>
)

const FormDescription = ({
  children,
  className = "",
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p className={`text-sm text-muted-foreground ${className}`} {...props}>
    {children}
  </p>
)

const FormMessage = ({
  children,
  className = "",
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p className={`text-sm font-medium text-destructive ${className}`} {...props}>
    {children}
  </p>
)


interface CompositionFormProps {
  defaultValues?: Partial<CompositionFormValues>
  onSubmit: (data: CompositionFormValues) => Promise<void>
  isSubmitting?: boolean
  submitLabel?: string
  className?: string
}

export function CompositionForm({
  defaultValues = {},
  onSubmit,
  isSubmitting = false,
  submitLabel = "Enregistrer",
  className,
}: CompositionFormProps) {
  const navigate = useNavigate()

  const form = useForm<CompositionFormValues>({
    resolver: zodResolver(compositionFormSchema),
    defaultValues: {
      name: "",
      description: "",
      playstyle: "balanced",
      squad_size: 10,
      professions: [],
      ...defaultValues,
    },
  })

  const handleSubmit = async (data: CompositionFormValues) => {
    try {
      await onSubmit(data)
      navigate("/compositions")
    } catch (error) {
      console.error(
        error instanceof Error ? error.message : "Une erreur est survenue"
      )
    }
  }

  return (
    <form
      onSubmit={form.handleSubmit(handleSubmit)}
      className={`space-y-6 ${className || ""}`}
    >
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <FormField name="name">
          {({ field }) => (
            <FormItem>
              <FormLabel>Nom de la composition</FormLabel>
              <FormControl>
                <Input placeholder="Ma composition" {...field} />
              </FormControl>
              <FormDescription>
                Donnez un nom clair et descriptif à votre composition.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        </FormField>

        <FormField name="playstyle">
          {({ field }) => (
            <FormItem>
              <FormLabel>Style de jeu</FormLabel>
              <Select
                onValueChange={field.onChange}
                defaultValue={field.value}
                value={field.value}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un style de jeu" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {playstyleOptions.map((style) => (
                    <SelectItem key={style} value={style}>
                      {style}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Choisissez le style de jeu qui correspond le mieux à cette
                composition.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        </FormField>

        <FormField name="squad_size">
          {({ field }) => (
            <FormItem>
              <FormLabel>Taille de l'escouade</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  min={1}
                  max={100}
                  {...field}
                  onChange={(e) => field.onChange(Number(e.target.value))}
                />
              </FormControl>
              <FormDescription>
                Nombre de joueurs dans l'escouade (1-100).
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        </FormField>

        <FormField name="professions">
          {({ field }) => (
            <FormItem>
              <FormLabel>Professions</FormLabel>
              <FormControl>
                <ProfessionSelect
                  value={field.value}
                  onChange={field.onChange}
                />
              </FormControl>
              <FormDescription>
                Sélectionnez les professions pour cette composition.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        </FormField>

        <div className="md:col-span-2">
          <FormField name="description">
            {({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Décrivez les objectifs et la stratégie de cette composition..."
                    className="min-h-[100px]"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Décrivez les objectifs, la stratégie ou toute autre
                  information utile pour cette composition.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          </FormField>
        </div>
      </div>

      <div className="flex justify-end gap-4 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => navigate(-1)}
          disabled={isSubmitting}
        >
          Annuler
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting && (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          )}
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
