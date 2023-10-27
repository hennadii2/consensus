import { FeatureFlag } from "../../../web/src/enums/feature-flag";
import "./commands";

/**
 * Prevent test from failing because of new feature flag
 */
beforeEach(() => {
  Cypress.on("uncaught:exception", (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
  });

  const excludedFeature = [FeatureFlag.PAPER_SEARCH.toString()];

  cy.visit("/feature-flag");
  cy.wait(3000);
  cy.get('input[type="checkbox"]')
    .filter((index, checkbox) => {
      const checkboxName = checkbox.getAttribute("name") || "";
      return !excludedFeature.includes(checkboxName);
    })
    .check({ force: true });
});
