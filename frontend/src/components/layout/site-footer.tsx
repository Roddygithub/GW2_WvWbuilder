export function SiteFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t py-6">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          © {currentYear} GW2 WvW Builder. All game content and materials are
          trademarks and copyrights of ArenaNet, LLC.
        </p>
        <div className="flex items-center space-x-4">
          <a
            href="https://github.com/yourusername/gw2-wvwbuilder"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            GitHub
          </a>
          <a
            href="https://github.com/yourusername/gw2-wvwbuilder/issues"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Report an issue
          </a>
        </div>
      </div>
    </footer>
  );
}
