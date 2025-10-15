import * as React from "react";
import {
  useForm as useReactHookForm,
  type UseFormReturn,
} from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

type FormProps<T extends z.ZodType> = {
  children: React.ReactNode;
  form: UseFormReturn<z.infer<T>>;
  onSubmit: (values: z.infer<T>) => void;
  className?: string;
};

const Form = <T extends z.ZodType>({
  children,
  form,
  onSubmit,
  className,
}: FormProps<T>) => {
  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className={className}>
      {children}
    </form>
  );
};

const FormField = <T extends z.ZodType>({
  control,
  name,
  render,
}: {
  control: UseFormReturn<z.infer<T>>["control"];
  name: keyof z.infer<T>;
  render: (props: { field: any }) => React.ReactNode;
}) => {
  return (
    <div className="space-y-2">
      {render({
        field: {
          ...control.register(name as any),
        },
      })}
    </div>
  );
};

const FormItem = ({ children }: { children: React.ReactNode }) => {
  return <div className="space-y-1">{children}</div>;
};

const FormLabel = ({
  children,
  className,
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>) => {
  return (
    <label
      className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
      {...props}
    >
      {children}
    </label>
  );
};

const FormControl = ({
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => {
  return <div {...props}>{children}</div>;
};

const FormDescription = ({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) => {
  return (
    <p className={`text-sm text-muted-foreground ${className}`} {...props}>
      {children}
    </p>
  );
};

const FormMessage = ({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) => {
  return (
    <p
      className={`text-sm font-medium text-destructive ${className}`}
      {...props}
    >
      {children}
    </p>
  );
};

export {
  Form,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  FormField,
  useReactHookForm,
  zodResolver,
};
