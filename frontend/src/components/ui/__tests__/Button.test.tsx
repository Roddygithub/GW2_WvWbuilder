import * as React from "react"
import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Button } from "../button"
import "@testing-library/jest-dom"

describe("Button", () => {
  it("renders a button with default variant", () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole("button", { name: /click me/i })
    
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass("bg-primary")
    expect(button).toHaveClass("text-primary-foreground")
  })

  it("applies custom className", () => {
    render(<Button className="custom-class">Custom Button</Button>)
    const button = screen.getByRole("button", { name: /custom button/i })
    
    expect(button).toHaveClass("custom-class")
  })

  it("renders as child when asChild is true", () => {
    render(
      <Button asChild>
        <a href="https://example.com">Link</a>
      </Button>
    )
    
    const link = screen.getByRole("link", { name: /link/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute("href", "https://example.com")
  })

  it("applies variant styles", () => {
    const { rerender } = render(<Button variant="outline">Outline</Button>)
    expect(screen.getByRole("button")).toHaveClass("border")
    
    rerender(<Button variant="destructive">Destructive</Button>)
    expect(screen.getByRole("button")).toHaveClass("bg-destructive")
  })

  it("applies size styles", () => {
    render(<Button size="lg">Large Button</Button>)
    expect(screen.getByRole("button")).toHaveClass("h-11")
  })

  it("handles click events", async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole("button", { name: /click me/i })
    await userEvent.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled Button</Button>)
    
    const button = screen.getByRole("button", { name: /disabled button/i })
    expect(button).toBeDisabled()
    expect(button.className).toContain("opacity-50")
    expect(button.className).toContain("pointer-events-none")
  })

  it("forwards ref to the button element", () => {
    const ref = React.createRef<HTMLButtonElement>()
    render(<Button ref={ref}>Button with Ref</Button>)
    
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
    expect(ref.current?.textContent).toBe("Button with Ref")
  })
})
