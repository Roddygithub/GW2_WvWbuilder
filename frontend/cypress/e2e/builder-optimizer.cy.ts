/**
 * E2E Test: Builder Optimizer
 * Tests the complete flow of optimizing a WvW composition
 */

describe('Builder Optimizer', () => {
  beforeEach(() => {
    // Login first
    cy.visit('/login');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('testpassword');
    cy.get('button[type="submit"]').click();
    
    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');
    
    // Navigate to builder
    cy.visit('/builder');
    cy.url().should('include', '/builder');
  });

  it('should display the builder optimizer page', () => {
    cy.contains('WvW Composition Optimizer').should('be.visible');
    cy.contains('Squad Configuration').should('be.visible');
    cy.contains('Optimization Goals').should('be.visible');
  });

  it('should allow configuring squad size and game mode', () => {
    // Change squad size
    cy.get('[id="squad-size"]').parent().click();
    cy.contains('20 Players').click();
    
    // Change game mode
    cy.get('[id="game-mode"]').parent().click();
    cy.contains('Roaming').click();
    
    // Verify configuration summary
    cy.contains('20 players').should('be.visible');
    cy.contains('roaming').should('be.visible');
  });

  it('should allow selecting optimization goals', () => {
    // Click on Boon Uptime (should be selected by default)
    cy.contains('Boon Uptime').parent().should('have.class', 'border-purple-500');
    
    // Click on Crowd Control to select it
    cy.contains('Crowd Control').click();
    cy.contains('Crowd Control').parent().should('have.class', 'border-purple-500');
    
    // Verify goals count in summary
    cy.contains('4 selected').should('be.visible');
  });

  it('should allow setting preferred role distribution', () => {
    // Set healer count
    cy.get('input[id="role-healer"]').clear().type('5');
    cy.get('input[id="role-healer"]').should('have.value', '5');
    
    // Set DPS count
    cy.get('input[id="role-dps"]').clear().type('10');
    cy.get('input[id="role-dps"]').should('have.value', '10');
  });

  it('should allow adding and removing fixed roles', () => {
    // Add a fixed role
    cy.contains('Add').click();
    cy.get('input[type="number"]').first().should('be.visible');
    
    // Set count
    cy.get('input[type="number"]').first().clear().type('2');
    
    // Remove the fixed role
    cy.get('button').contains('×').click();
    cy.contains('No fixed roles').should('be.visible');
  });

  it('should optimize composition and display results', () => {
    // Configure a simple optimization
    cy.get('[id="squad-size"]').parent().click();
    cy.contains('15 Players').click();
    
    cy.get('[id="game-mode"]').parent().click();
    cy.contains('Zerg').click();
    
    // Click optimize button
    cy.contains('Optimize Composition').click();
    
    // Wait for optimization to complete (max 10s)
    cy.contains('Optimizing...', { timeout: 1000 }).should('be.visible');
    cy.contains('Optimization Results', { timeout: 10000 }).should('be.visible');
    
    // Verify results are displayed
    cy.contains('Optimization Score').should('be.visible');
    cy.contains('Boon Coverage').should('be.visible');
    cy.contains('Role Distribution').should('be.visible');
    
    // Verify score is displayed (0-100)
    cy.get('[class*="text-4xl"]').should('contain', '/100');
  });

  it('should show error when no optimization goals are selected', () => {
    // Deselect all goals
    cy.contains('Boon Uptime').click();
    cy.contains('Healing').click();
    cy.contains('Damage').click();
    
    // Try to optimize
    cy.contains('Optimize Composition').should('be.disabled');
    cy.contains('Select at least one optimization goal').should('be.visible');
  });

  it('should display mode description when mode is selected', () => {
    // Select Zerg mode
    cy.get('[id="game-mode"]').parent().click();
    cy.contains('Zerg').click();
    
    // Verify description is shown
    cy.contains('Large-scale fights').should('be.visible');
  });

  it('should update configuration summary in real-time', () => {
    // Initial state
    cy.contains('15 players').should('be.visible');
    cy.contains('3 selected').should('be.visible');
    
    // Change squad size
    cy.get('[id="squad-size"]').parent().click();
    cy.contains('25 Players').click();
    cy.contains('25 players').should('be.visible');
    
    // Add a fixed role
    cy.contains('Add').click();
    cy.contains('Fixed Roles:').parent().should('contain', '1');
  });

  it('should handle API errors gracefully', () => {
    // Intercept API call and force error
    cy.intercept('POST', '**/api/v1/builder/optimize', {
      statusCode: 500,
      body: { detail: 'Optimization failed' },
    }).as('optimizeError');
    
    // Try to optimize
    cy.contains('Optimize Composition').click();
    
    // Wait for error
    cy.wait('@optimizeError');
    
    // Verify error toast is shown (sonner toast)
    cy.contains('Optimization failed', { timeout: 5000 }).should('be.visible');
  });

  it('should be responsive on mobile', () => {
    // Test mobile viewport
    cy.viewport('iphone-x');
    
    cy.contains('WvW Composition Optimizer').should('be.visible');
    cy.contains('Squad Configuration').should('be.visible');
    
    // Verify layout adapts
    cy.get('[class*="lg:grid-cols-3"]').should('exist');
  });

  it('should persist form state during optimization', () => {
    // Set custom values
    cy.get('[id="squad-size"]').parent().click();
    cy.contains('20 Players').click();
    
    cy.get('input[id="role-healer"]').clear().type('4');
    
    // Start optimization
    cy.contains('Optimize Composition').click();
    
    // Wait for results
    cy.contains('Optimization Results', { timeout: 10000 }).should('be.visible');
    
    // Verify form values are still there
    cy.get('input[id="role-healer"]').should('have.value', '4');
  });
});

describe('Builder Optimizer - Dark Mode', () => {
  it('should display correctly in dark mode', () => {
    cy.visit('/login');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('testpassword');
    cy.get('button[type="submit"]').click();
    
    cy.visit('/builder');
    
    // Verify dark mode classes
    cy.get('body').should('have.class', 'dark');
    cy.get('[class*="bg-slate-950"]').should('exist');
    cy.get('[class*="text-purple-400"]').should('exist');
  });
});

describe('Builder Optimizer - Accessibility', () => {
  beforeEach(() => {
    cy.visit('/login');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('testpassword');
    cy.get('button[type="submit"]').click();
    cy.visit('/builder');
  });

  it('should be keyboard navigable', () => {
    // Tab through form elements
    cy.get('body').tab();
    cy.focused().should('have.attr', 'id', 'squad-size');
    
    cy.focused().tab();
    cy.focused().should('have.attr', 'id', 'game-mode');
  });

  it('should have proper ARIA labels', () => {
    cy.get('label[for="squad-size"]').should('exist');
    cy.get('label[for="game-mode"]').should('exist');
    cy.get('button').contains('Optimize Composition').should('have.attr', 'type', 'button');
  });
});
