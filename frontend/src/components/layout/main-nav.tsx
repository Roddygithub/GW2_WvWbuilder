import { NavLink } from "react-router-dom";
import { cn } from '../../lib/utils';

export function MainNav() {
  const navItems = [
    { name: "Home", href: "/" },
    { name: "Builder", href: "/builder" },
    { name: "Compositions", href: "/compositions" },
    { name: "About", href: "/about" },
  ];

  return (
    <nav className="flex items-center space-x-6 text-sm font-medium">
      {navItems.map((item) => (
        <NavLink
          key={item.href}
          to={item.href}
          className={({ isActive }) =>
            cn(
              "transition-colors hover:text-foreground/80",
              isActive ? "text-foreground" : "text-foreground/60",
            )
          }
        >
          {item.name}
        </NavLink>
      ))}
    </nav>
  );
}
