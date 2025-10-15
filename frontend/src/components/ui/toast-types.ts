import * as React from "react";
import { type VariantProps } from "class-variance-authority";
import { Toast, ToastAction, toastVariants } from "@/components/ui/toast";

export type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>;
export type ToastActionElement = React.ReactElement<typeof ToastAction>;

export type ToastVariant = VariantProps<typeof toastVariants>["variant"];
