/// <reference types="cypress" />

describe('Authentication Flow - Register & Login', () => {
  const timestamp = Date.now()
  const newUser = {
    username: `testuser_${timestamp}`,
    email: `test_${timestamp}@example.com`,
    password: 'TestPassword123!',
    fullName: 'Test User',
  }

  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  describe('Registration', () => {
    it('should display registration page', () => {
      cy.visit('/register')
      cy.contains(/register|sign up/i).should('be.visible')
      cy.get('input[name="username"]').should('be.visible')
      cy.get('input[name="email"]').should('be.visible')
      cy.get('input[name="password"]').should('be.visible')
    })

    it('should register a new user successfully', () => {
      cy.visit('/register')
      
      cy.get('input[name="username"]').type(newUser.username)
      cy.get('input[name="email"]').type(newUser.email)
      cy.get('input[name="password"]').type(newUser.password)
      cy.get('input[name="confirmPassword"]').type(newUser.password)
      
      if (cy.get('input[name="fullName"]').should('exist')) {
        cy.get('input[name="fullName"]').type(newUser.fullName)
      }
      
      cy.get('button[type="submit"]').click()
      
      // Should show success message or redirect to login
      cy.url().should('match', /\/(login|dashboard)/)
    })

    it('should show validation errors for invalid inputs', () => {
      cy.visit('/register')
      
      // Try to submit empty form
      cy.get('button[type="submit"]').click()
      
      // Should show validation errors
      cy.contains(/required|invalid/i).should('be.visible')
    })

    it('should validate email format', () => {
      cy.visit('/register')
      
      cy.get('input[name="email"]').type('invalid-email')
      cy.get('input[name="email"]').blur()
      
      // Should show email validation error
      cy.contains(/valid email/i).should('be.visible')
    })

    it('should validate password strength', () => {
      cy.visit('/register')
      
      cy.get('input[name="password"]').type('weak')
      cy.get('input[name="password"]').blur()
      
      // Should show password strength error
      cy.contains(/password.*strong|minimum.*characters/i).should('be.visible')
    })

    it('should validate password confirmation match', () => {
      cy.visit('/register')
      
      cy.get('input[name="password"]').type('Password123!')
      cy.get('input[name="confirmPassword"]').type('DifferentPassword123!')
      cy.get('input[name="confirmPassword"]').blur()
      
      // Should show password mismatch error
      cy.contains(/passwords.*match/i).should('be.visible')
    })

    it('should prevent duplicate email registration', () => {
      cy.visit('/register')
      
      // Try to register with existing email
      cy.get('input[name="username"]').type('existinguser')
      cy.get('input[name="email"]').type('frontend@user.com') // Existing user
      cy.get('input[name="password"]').type('Password123!')
      cy.get('input[name="confirmPassword"]').type('Password123!')
      cy.get('button[type="submit"]').click()
      
      // Should show error about existing email
      cy.contains(/already exists|already registered/i).should('be.visible')
    })
  })

  describe('Login', () => {
    it('should login with valid credentials', () => {
      cy.visit('/login')
      
      cy.get('input[name="email"]').type('frontend@user.com')
      cy.get('input[name="password"]').type('Frontend123!')
      cy.get('button[type="submit"]').click()
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard')
    })

    it('should show error with invalid credentials', () => {
      cy.visit('/login')
      
      cy.get('input[name="email"]').type('wrong@email.com')
      cy.get('input[name="password"]').type('wrongpassword')
      cy.get('button[type="submit"]').click()
      
      // Should show error
      cy.contains(/incorrect|invalid/i).should('be.visible')
      cy.url().should('include', '/login')
    })

    it('should show validation for empty fields', () => {
      cy.visit('/login')
      
      cy.get('button[type="submit"]').click()
      
      // Should show validation errors
      cy.contains(/required/i).should('be.visible')
    })

    it('should have "Remember me" option', () => {
      cy.visit('/login')
      
      cy.get('input[type="checkbox"][name="rememberMe"]').should('exist')
    })

    it('should have "Forgot password" link', () => {
      cy.visit('/login')
      
      cy.contains(/forgot.*password/i).should('be.visible')
    })

    it('should toggle password visibility', () => {
      cy.visit('/login')
      
      cy.get('input[name="password"]').should('have.attr', 'type', 'password')
      
      // Click show password button
      cy.get('[data-testid="toggle-password-visibility"]').click()
      
      cy.get('input[name="password"]').should('have.attr', 'type', 'text')
    })
  })

  describe('Session Management', () => {
    it('should persist session after page reload', () => {
      cy.loginUI('frontend@user.com', 'Frontend123!')
      cy.url().should('include', '/dashboard')
      
      // Reload page
      cy.reload()
      
      // Should still be on dashboard (not redirected to login)
      cy.url().should('include', '/dashboard')
    })

    it('should clear session on logout', () => {
      cy.loginUI('frontend@user.com', 'Frontend123!')
      cy.url().should('include', '/dashboard')
      
      // Logout
      cy.get('[data-testid="logout-button"]').click()
      
      // Try to access dashboard
      cy.visit('/dashboard')
      
      // Should redirect to login
      cy.url().should('include', '/login')
    })

    it('should handle expired token gracefully', () => {
      cy.login('frontend@user.com', 'Frontend123!')
      cy.visit('/dashboard')
      
      // Simulate expired token
      cy.window().then((win) => {
        win.localStorage.setItem('access_token', 'expired.token.here')
      })
      
      // Reload to trigger API call with expired token
      cy.reload()
      
      // Should redirect to login or show refresh prompt
      cy.url().should('match', /\/(login|refresh)/)
    })
  })

  describe('Navigation Between Auth Pages', () => {
    it('should navigate from login to register', () => {
      cy.visit('/login')
      
      cy.contains(/sign up|register/i).click()
      
      cy.url().should('include', '/register')
    })

    it('should navigate from register to login', () => {
      cy.visit('/register')
      
      cy.contains(/sign in|login/i).click()
      
      cy.url().should('include', '/login')
    })

    it('should redirect to dashboard if already logged in', () => {
      cy.login('frontend@user.com', 'Frontend123!')
      
      // Try to visit login page
      cy.visit('/login')
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard')
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      cy.visit('/login')
      
      cy.get('label[for="email"]').should('exist')
      cy.get('label[for="password"]').should('exist')
    })

    it('should support keyboard navigation', () => {
      cy.visit('/login')
      
      // Tab through form fields
      cy.get('input[name="email"]').focus().tab()
      cy.focused().should('have.attr', 'name', 'password')
      
      cy.tab()
      cy.focused().should('have.attr', 'type', 'submit')
    })

    it('should have proper ARIA attributes', () => {
      cy.visit('/login')
      
      cy.get('form').should('have.attr', 'aria-label')
      cy.get('button[type="submit"]').should('have.attr', 'aria-label')
    })
  })
})
