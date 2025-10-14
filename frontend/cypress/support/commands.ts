/// <reference types="cypress" />

// ***********************************************
// Custom commands for GW2 WvW Builder
// ***********************************************

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to login via API
       * @example cy.login('test@example.com', 'password123')
       */
      login(email: string, password: string): Chainable<void>
      
      /**
       * Custom command to login via UI
       * @example cy.loginUI('test@example.com', 'password123')
       */
      loginUI(email: string, password: string): Chainable<void>
      
      /**
       * Custom command to logout
       * @example cy.logout()
       */
      logout(): Chainable<void>
      
      /**
       * Custom command to check if user is authenticated
       * @example cy.isAuthenticated()
       */
      isAuthenticated(): Chainable<boolean>
    }
  }
}

// Login via API (faster for setup)
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    form: true,
    body: {
      username: email,
      password: password,
    },
  }).then((response) => {
    expect(response.status).to.eq(200)
    const { access_token, refresh_token } = response.body

    // Visit the app and inject tokens before it loads
    cy.visit('/', {
      onBeforeLoad(win) {
        win.localStorage.setItem('access_token', access_token)
        win.localStorage.setItem('refresh_token', refresh_token)
      },
    })
  })
})

// Login via UI (for testing the login flow)
Cypress.Commands.add('loginUI', (email: string, password: string) => {
  cy.visit('/login')
  cy.get('input[name="email"]').type(email)
  cy.get('input[name="password"]').type(password)
  cy.get('button[type="submit"]').click()
  
  // Wait for redirect to dashboard
  cy.url().should('include', '/dashboard')
})

// Logout
Cypress.Commands.add('logout', () => {
  window.localStorage.removeItem('access_token')
  window.localStorage.removeItem('refresh_token')
  cy.visit('/login')
})

// Check if authenticated
Cypress.Commands.add('isAuthenticated', () => {
  const token = window.localStorage.getItem('access_token')
  return cy.wrap(!!token)
})

export {}
