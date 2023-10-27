describe("Homepage", () => {
  describe("redirected to /search", () => {
    it("should open the homepage with topbar, search input, trending tags and product details", () => {
      cy.visit("/search");

      cy.getByTestId("topbar").should("be.visible");
      cy.getByTestId("search-input-form").should("be.visible");
      cy.getByTestId("tag").should("be.visible");
      cy.getByTestId("product-details").should("be.visible");
    });

    it("should navigate to the results page with query text", () => {
      cy.visit("/search");

      const text = "are covid-19 vaccines effective?";
      cy.getByTestId("user-button").should("be.visible");
      cy.getByTestId("search-input").type(text);
      cy.get("#search-button").click();
      cy.url().should("include", "are%20covid-19%20vaccines%20effective%3F");
    });

    it("should navigate to the results page when clicking one of the trending tag", async () => {
      cy.visit("/search");

      cy.getByTestId("user-button").should("be.visible");
      const firstTag = cy.getByTestId("tag").first();
      firstTag.click().then(() => {
        firstTag.invoke("text").then((text) => {
          cy.url().should("include", text);
        });
      });
    });

    it("should navigate to the results page when type search then hit enter", () => {
      cy.visit("/search");
      cy.wait(2000);

      const text = "are covid-19 vaccines effective?";
      cy.getByTestId("search-input").should("be.visible");
      cy.getByTestId("search-input").type(text);
      cy.getByTestId("search-input").type("{enter}");

      cy.url().should("include", "are%20covid-19%20vaccines%20effective%3F");
      cy.getByTestId("card-search-result-item").should("be.visible");
    });
  });

  it("should open help content", () => {
    cy.visit("/search");

    cy.getByTestId("help-button").should("be.visible").click();
    cy.getByTestId("help-content").should("be.visible");
  });

  it("should hide loader when click back button", () => {
    cy.visit("/search");

    const text = "are covid-19 vaccines effective?";
    cy.wait(5000);
    cy.getByTestId("search-input").should("be.visible");
    cy.getByTestId("search-input").type(text);
    cy.wait(5000);
    cy.get("#search-button").click();
    cy.url().should("include", "are%20covid-19%20vaccines%20effective%3F");
    cy.get('[data-testid="icon-loader"]').should("exist");
    cy.go("back");
    cy.get('[data-testid="icon-loader"]').should("not.exist");
  });
});

export {};
