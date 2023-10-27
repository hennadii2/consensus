// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add(`initializeAuth`, () => {
  cy.log(`Initializing auth state.`);

  cy.visit(`/search/`);

  cy.window().should((window) => {
    expect(window).to.not.have.property(`Clerk`, undefined);
    expect(window.Clerk.isReady()).to.eq(true);
  });
});

Cypress.Commands.overwrite("visit", (originalFn, options) => {
  return originalFn(options, { failOnStatusCode: false });
});

Cypress.Commands.add("getByTestId", (selector: string, ...args): any => {
  return cy.get(`[data-testid=${selector}]`, ...args);
});

Cypress.Commands.add("signin", function () {
  cy.get("body").then(($body) => {
    cy.wait(10000);
    if ($body.find(".cl-userButtonTrigger").length === 1) {
      cy.get(".cl-userButtonTrigger").should("be.visible");
    } else {
      // sign in
      cy.visit("/sign-in");
      cy.wait(10000);

      const email = "test@mailinator.com";
      const password = "consensus22";
      cy.get("#identifier-field").type(email + "{enter}");

      cy.wait(5000);

      cy.get("#password-field").type(password + "{enter}");

      cy.wait(3000);

      cy.get(".cl-userButtonTrigger").should("be.visible");
    }
  });
});

Cypress.Commands.add("signout", function () {
  cy.wait(10000);
  cy.get("body").then(($body) => {
    if ($body.find(".cl-userButtonTrigger").length === 1) {
      // sign out
      cy.get(".cl-userButtonTrigger").click();
      cy.get("button").contains("Sign out").click();

      cy.wait(5000);
      cy.url().should("include", "sign-in");
      cy.get("button")
        .contains(new RegExp("Continue", "g"))
        .should("be.visible");
    } else {
      cy.get("button")
        .contains(new RegExp("Continue", "g"))
        .should("be.visible");
    }
  });
});

export {};
