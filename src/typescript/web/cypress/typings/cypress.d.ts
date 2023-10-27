/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable<Subject> {
    getByTestId(str: string): Chainable<Element>;
  }
}
