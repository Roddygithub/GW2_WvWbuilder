# UI Components

This directory contains reusable UI components built with Radix UI and styled with Tailwind CSS.

## Available Components

### Button

A customizable button component with various styles and states.

```tsx
import { Button } from "@/components/ui/button"

// Basic usage
<Button>Click me</Button>

// With variant and size
<Button variant="outline" size="lg">Large Outline Button</Button>

// As a link
<Button asChild>
  <a href="/some-page">Go to page</a>
</Button>
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'default' \| 'destructive' \| 'outline' \| 'secondary' \| 'ghost' \| 'link' | 'default' | The visual style of the button |
| size | 'default' \| 'sm' \| 'lg' \| 'icon' | 'default' | The size of the button |
| asChild | boolean | false | Render as child component |
| className | string | '' | Additional CSS classes |

### Alert Dialog

A modal dialog that interrupts the user with important content and expects a response.

```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

function Example() {
  const [open, setOpen] = React.useState(false)

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger>Open</AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction>Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

## Styling

Components are styled using Tailwind CSS with the following conventions:

- Use the `cn` utility for conditional class names
- Follow the design system defined in `tailwind.config.js`
- Use semantic color tokens (e.g., `bg-primary`, `text-secondary`)

## Accessibility

All components follow WAI-ARIA design patterns and include:

- Keyboard navigation
- Proper ARIA attributes
- Focus management
- Screen reader support

## Development

### Adding a New Component

1. Create a new file in this directory
2. Follow the pattern of existing components
3. Add TypeScript types for all props
4. Document the component with JSDoc
5. Add examples in the component's documentation

### Testing

Components should be tested with:

- Unit tests for functionality
- Visual regression tests
- Screen reader testing
- Keyboard navigation testing

## Best Practices

- Keep components focused and single-responsibility
- Use composition over configuration
- Follow the principle of least privilege for props
- Document all props and their types
- Include accessibility attributes
- Support both mouse and keyboard interaction
