/// <reference types="cypress" />

describe('Dashboard Flow - Complete User Journey', () => {
  const testUser = {
    email: 'frontend@user.com',
    password: 'Frontend123!',
  }

  beforeEach(() => {
    // Clear storage before each test
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  describe('Authentication Flow', () => {
    it('should display login page', () => {
      cy.visit('/login')
      cy.contains('Login').should('be.visible')
      cy.get('input[name="email"]').should('be.visible')
      cy.get('input[name="password"]').should('be.visible')
    })

    it('should login successfully via UI', () => {
      cy.loginUI(testUser.email, testUser.password)
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard')
      
      // Should store JWT token
      cy.window().then((win) => {
        const token = win.localStorage.getItem('access_token')
        expect(token).to.exist
        expect(token).to.be.a('string')
        expect(token.length).to.be.greaterThan(0)
      })
    })

    it('should show error on invalid credentials', () => {
      cy.visit('/login')
      cy.get('input[name="email"]').type('wrong@email.com')
      cy.get('input[name="password"]').type('wrongpassword')
      cy.get('button[type="submit"]').click()
      
      // Should show error message
      cy.contains(/incorrect|invalid|error/i).should('be.visible')
      
      // Should stay on login page
      cy.url().should('include', '/login')
    })

    it('should logout successfully', () => {
      cy.loginUI(testUser.email, testUser.password)
      cy.url().should('include', '/dashboard')
      
      // Click logout button (adjust selector based on your UI)
      cy.get('[data-testid="logout-button"]').click()
      
      // Should redirect to login
      cy.url().should('include', '/login')
      
      // Token should be removed
      cy.window().then((win) => {
        const token = win.localStorage.getItem('access_token')
        expect(token).to.be.null
      })
    })
  })

  describe('Dashboard Access & Display', () => {
    beforeEach(() => {
      // Login before each dashboard test
      cy.login(testUser.email, testUser.password)
      cy.visit('/dashboard')
    })

    it('should display dashboard with stats', () => {
      // Check for stat cards
      cy.contains(/compositions/i).should('be.visible')
      cy.contains(/builds/i).should('be.visible')
      cy.contains(/teams/i).should('be.visible')
      
      // Stats should be numbers
      cy.get('[data-testid="stat-card"]').should('have.length.at.least', 3)
    })

    it('should display activity chart', () => {
      cy.get('[data-testid="activity-chart"]').should('be.visible')
      
      // Chart should have data or empty state
      cy.get('[data-testid="activity-chart"]').within(() => {
        cy.get('svg, canvas, .empty-state').should('exist')
      })
    })

    it('should display activity feed', () => {
      cy.get('[data-testid="activity-feed"]').should('be.visible')
      
      // Should show recent activities or empty state
      cy.get('[data-testid="activity-feed"]').within(() => {
        cy.get('[data-testid="activity-item"], .empty-state').should('exist')
      })
    })

    it('should display quick actions', () => {
      cy.get('[data-testid="quick-actions"]').should('be.visible')
      
      // Should have action buttons
      cy.get('[data-testid="quick-action-button"]').should('have.length.at.least', 3)
    })

    it('should have working sidebar navigation', () => {
      // Check sidebar is visible
      cy.get('[data-testid="sidebar"]').should('be.visible')
      
      // Check navigation links
      cy.get('[data-testid="nav-dashboard"]').should('be.visible')
      cy.get('[data-testid="nav-compositions"]').should('be.visible')
      cy.get('[data-testid="nav-builds"]').should('be.visible')
      cy.get('[data-testid="nav-teams"]').should('be.visible')
    })
  })

  describe('Protected Routes', () => {
    it('should redirect to login when accessing dashboard without auth', () => {
      cy.visit('/dashboard')
      
      // Should redirect to login
      cy.url().should('include', '/login')
    })

    it('should redirect to login when accessing protected routes without auth', () => {
      const protectedRoutes = [
        '/dashboard',
        '/compositions',
        '/builds',
        '/teams',
        '/profile',
      ]

      protectedRoutes.forEach((route) => {
        cy.visit(route)
        cy.url().should('include', '/login')
      })
    })

    it('should allow access to protected routes when authenticated', () => {
      cy.login(testUser.email, testUser.password)
      
      cy.visit('/dashboard')
      cy.url().should('include', '/dashboard')
      cy.url().should('not.include', '/login')
    })
  })

  describe('JWT Token Management', () => {
    it('should store JWT token in localStorage', () => {
      cy.login(testUser.email, testUser.password)
      
      cy.window().then((win) => {
        const accessToken = win.localStorage.getItem('access_token')
        const refreshToken = win.localStorage.getItem('refresh_token')
        
        expect(accessToken).to.exist
        expect(refreshToken).to.exist
        
        // Tokens should be valid JWT format (3 parts separated by dots)
        expect(accessToken?.split('.')).to.have.length(3)
        expect(refreshToken?.split('.')).to.have.length(3)
      })
    })

    it('should include JWT token in API requests', () => {
      cy.login(testUser.email, testUser.password)
      cy.visit('/dashboard')
      
      // Intercept API calls
      cy.intercept('GET', '**/api/v1/**').as('apiRequest')
      
      // Trigger an API call (e.g., by refreshing)
      cy.reload()
      
      // Wait for API call and check Authorization header
      cy.wait('@apiRequest').then((interception) => {
        expect(interception.request.headers).to.have.property('authorization')
        expect(interception.request.headers.authorization).to.match(/^Bearer .+/)
      })
    })
  })

  describe('Responsive Design', () => {
    beforeEach(() => {
      cy.login(testUser.email, testUser.password)
      cy.visit('/dashboard')
    })

    it('should display correctly on desktop', () => {
      cy.viewport(1920, 1080)
      cy.get('[data-testid="sidebar"]').should('be.visible')
      cy.get('[data-testid="main-content"]').should('be.visible')
    })

    it('should display correctly on tablet', () => {
      cy.viewport('ipad-2')
      cy.get('[data-testid="main-content"]').should('be.visible')
    })

    it('should display correctly on mobile', () => {
      cy.viewport('iphone-x')
      cy.get('[data-testid="main-content"]').should('be.visible')
      
      // Sidebar might be hidden or collapsible on mobile
      cy.get('[data-testid="mobile-menu-button"]').should('be.visible')
    })
  })

  describe('User Experience', () => {
    beforeEach(() => {
      cy.login(testUser.email, testUser.password)
      cy.visit('/dashboard')
    })

    it('should show loading states', () => {
      // Reload to see loading states
      cy.reload()
      
      // Should show skeleton or spinner
      cy.get('[data-testid="loading"], .skeleton, .spinner').should('exist')
    })

    it('should handle API errors gracefully', () => {
      // Simulate API error
      cy.intercept('GET', '**/api/v1/dashboard/stats', {
        statusCode: 500,
        body: { detail: 'Internal Server Error' },
      }).as('statsError')
      
      cy.reload()
      cy.wait('@statsError')
      
      // Should show error message
      cy.contains(/error|failed|unavailable/i).should('be.visible')
    })

    it('should display user info in header', () => {
      cy.get('[data-testid="user-menu"]').should('be.visible')
      cy.get('[data-testid="user-menu"]').should('contain', testUser.email.split('@')[0])
    })
  })

  describe('Performance', () => {
    it('should load dashboard within acceptable time', () => {
      cy.login(testUser.email, testUser.password)
      
      const startTime = Date.now()
      cy.visit('/dashboard')
      
      cy.get('[data-testid="dashboard-loaded"]').should('be.visible').then(() => {
        const loadTime = Date.now() - startTime
        expect(loadTime).to.be.lessThan(3000) // Should load in less than 3 seconds
      })
    })
  })
})
