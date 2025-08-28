import { Outlet } from 'react-router-dom'
import { MainNav } from './main-nav'
import { SiteHeader } from './site-header'
import { SiteFooter } from './site-footer'

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <div className="flex-1">
        <MainNav />
        <main className="container py-6">
          <Outlet />
        </main>
      </div>
      <SiteFooter />
    </div>
  )
}
