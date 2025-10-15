/**
 * E2E tests for Builder V2 flow
 */

describe('Builder V2 - Squad Optimization Flow', () => {
  beforeEach(() => {
    // Login first
    cy.visit('/login');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('testpassword');
    cy.get('button[type="submit"]').click();

    // Wait for redirect to dashboard
    cy.url().should('include', '/dashboard');

    // Navigate to Builder V2
    cy.visit('/builder');
  });

  it('should complete full optimization flow for WvW Zerg', () => {
    // Step 1: Squad Size
    cy.contains(/build your squad/i).should('be.visible');
    cy.contains(/select squad size/i).should('be.visible');

    cy.get('input[type="number"]').clear().type('30');
    cy.contains('button', /next/i).click();

    // Step 2: Game Mode Selection
    cy.contains(/select game mode/i).should('be.visible');

    // Select WvW
    cy.contains('button', /world vs world/i).click();

    // Select Zerg mode
    cy.contains('button', /zerg/i).click();

    // Go to next step or optimize
    cy.contains('button', /optimize|next/i).click();

    // Step 3: Optimization Results
    cy.contains(/optimizing/i, { timeout: 10000 }).should('be.visible');

    // Wait for optimization to complete
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Verify results are displayed
    cy.contains(/composition/i).should('be.visible');
    cy.contains(/members/i).should('be.visible');

    // Should show score percentage
    cy.contains(/\d+%/).should('be.visible');
  });

  it('should complete optimization flow for PvE Fractals', () => {
    // Step 1: Squad Size
    cy.get('input[type="number"]').clear().type('5');
    cy.contains('button', /next/i).click();

    // Step 2: Select PvE
    cy.contains('button', /pve|environment/i).click();

    // Select Fractals
    cy.contains('button', /fractal/i).click();

    // Optimize
    cy.contains('button', /optimize/i).click();

    // Wait for results
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Verify 5 members
    cy.get('[data-testid="member-card"]').should('have.length', 5);
  });

  it('should allow adding fixed professions', () => {
    // Navigate to step 1
    cy.get('input[type="number"]').clear().type('10');
    cy.contains('button', /next/i).click();

    // Select game mode
    cy.contains('button', /world vs world/i).click();
    cy.contains('button', /roaming/i).click();

    // Look for fixed professions option
    const fixedProfButton = cy.contains('button', /add fixed profession|optional/i);
    
    if (fixedProfButton) {
      fixedProfButton.click();

      // Select Guardian
      cy.contains(/guardian/i).click();

      // Optimize with constraints
      cy.contains('button', /optimize/i).click();

      // Verify Guardian appears in results
      cy.contains(/guardian/i, { timeout: 15000 }).should('be.visible');
    }
  });

  it('should display boon coverage metrics', () => {
    // Complete basic flow
    cy.get('input[type="number"]').clear().type('15');
    cy.contains('button', /next/i).click();

    cy.contains('button', /world vs world/i).click();
    cy.contains('button', /guild.*raid/i).click();

    cy.contains('button', /optimize/i).click();

    // Wait for results
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Check boon coverage
    cy.contains(/quickness/i).should('be.visible');
    cy.contains(/alacrity/i).should('be.visible');
    cy.contains(/stability/i).should('be.visible');
  });

  it('should display role distribution', () => {
    // Complete basic flow
    cy.get('input[type="number"]').clear().type('20');
    cy.contains('button', /next/i).click();

    cy.contains('button', /world vs world/i).click();
    cy.contains('button', /zerg/i).click();

    cy.contains('button', /optimize/i).click();

    // Wait for results
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Check role distribution
    cy.contains(/healer/i).should('be.visible');
    cy.contains(/support|boon/i).should('be.visible');
    cy.contains(/dps/i).should('be.visible');
  });

  it('should allow going back to edit parameters', () => {
    // Complete first step
    cy.get('input[type="number"]').clear().type('10');
    cy.contains('button', /next/i).click();

    // Go back
    cy.contains('button', /back/i).click();

    // Should be back at step 1
    cy.contains(/select squad size/i).should('be.visible');

    // Verify input still has value
    cy.get('input[type="number"]').should('have.value', '10');
  });

  it('should validate squad size input', () => {
    // Try invalid squad size
    cy.get('input[type="number"]').clear().type('0');

    // Next button should be disabled or show error
    cy.contains('button', /next/i).should('be.disabled')
      .or(() => {
        cy.contains(/invalid|minimum|required/i).should('be.visible');
      });

    // Try valid squad size
    cy.get('input[type="number"]').clear().type('5');
    cy.contains('button', /next/i).should('not.be.disabled');
  });

  it('should show loading state during optimization', () => {
    // Complete flow quickly
    cy.get('input[type="number"]').clear().type('10');
    cy.contains('button', /next/i).click();

    cy.contains('button', /world vs world/i).click();
    cy.contains('button', /roaming/i).click();

    cy.contains('button', /optimize/i).click();

    // Should show loading indicator
    cy.contains(/optimizing|loading/i).should('be.visible');

    // Loading should eventually disappear
    cy.contains(/optimizing|loading/i, { timeout: 15000 }).should('not.exist');
  });

  it('should handle optimization errors gracefully', () => {
    // Intercept API call and force error
    cy.intercept('POST', '**/api/v1/builder/optimize', {
      statusCode: 500,
      body: { detail: 'Optimization failed' },
    }).as('optimizeError');

    // Complete flow
    cy.get('input[type="number"]').clear().type('10');
    cy.contains('button', /next/i).click();

    cy.contains('button', /pve/i).click();
    cy.contains('button', /fractale/i).click();

    cy.contains('button', /optimize/i).click();

    // Wait for error
    cy.wait('@optimizeError');

    // Should show error message
    cy.contains(/error|failed/i).should('be.visible');
  });

  it('should allow saving optimized composition', () => {
    // Complete optimization
    cy.get('input[type="number"]').clear().type('5');
    cy.contains('button', /next/i).click();

    cy.contains('button', /pve/i).click();
    cy.contains('button', /raid/i).click();

    cy.contains('button', /optimize/i).click();

    // Wait for results
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Look for save button
    const saveButton = cy.contains('button', /save|create composition/i);
    
    if (saveButton) {
      saveButton.click();

      // Should show success message
      cy.contains(/saved|created/i, { timeout: 5000 }).should('be.visible');
    }
  });

  it('should display profession icons', () => {
    // Complete optimization
    cy.get('input[type="number"]').clear().type('10');
    cy.contains('button', /next/i).click();

    cy.contains('button', /world vs world/i).click();
    cy.contains('button', /roaming/i).click();

    cy.contains('button', /optimize/i).click();

    // Wait for results
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Should show profession names/icons
    cy.contains(/guardian|revenant|warrior|necromancer|engineer|ranger|thief|elementalist|mesmer/i)
      .should('be.visible');
  });

  it('should show optimization time', () => {
    // Complete optimization
    cy.get('input[type="number"]').clear().type('25');
    cy.contains('button', /next/i).click();

    cy.contains('button', /world vs world/i).click();
    cy.contains('button', /zerg/i).click();

    cy.contains('button', /optimize/i).click();

    // Wait for results
    cy.contains(/global score/i, { timeout: 15000 }).should('be.visible');

    // Should show time taken (if displayed)
    cy.contains(/seconds|ms|time/i).should('exist');
  });
});

describe('Builder V2 - Navigation', () => {
  beforeEach(() => {
    cy.visit('/login');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('testpassword');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });

  it('should be accessible from dashboard', () => {
    // Look for builder link
    cy.contains('a', /builder|create|optimize/i).click();

    cy.url().should('include', '/builder');
    cy.contains(/build your squad/i).should('be.visible');
  });

  it('should show progress indicator', () => {
    cy.visit('/builder');

    // Should show step indicator (1/3, 2/3, etc.)
    cy.contains(/step.*1|1.*of.*3|1\/3/i).should('be.visible');

    // Go to next step
    cy.get('input[type="number"]').clear().type('10');
    cy.contains('button', /next/i).click();

    // Should show step 2
    cy.contains(/step.*2|2.*of.*3|2\/3/i).should('be.visible');
  });
});
