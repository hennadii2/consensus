describe("Results page", () => {
  it("should open the results page with topbar with search input, claims", () => {
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");
    cy.getByTestId("card-search-result-item").should("be.visible");

    cy.getByTestId("topbar").within(() => {
      cy.getByTestId("search-input").should("be.visible");
    });
  });

  it("should update the results page with query text search", () => {
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");

    cy.getByTestId("user-button").should("be.visible");
    cy.getByTestId("card-search-result-item").should("be.visible");

    cy.getByTestId("search-input").focus().clear().type("Hello Consensus");
    cy.get("#search-button").click();
    cy.url().should("include", "Hello%20Consensus");
  });

  it("should navigate to the details page when clicking one of the title of the claims", () => {
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");

    cy.getByTestId("user-button").should("be.visible");
    cy.getByTestId("card-search-result-item")
      .first()
      .within(() => {
        const resultItemLink = cy.getByTestId("result-item-link");

        resultItemLink.click().then(() => {
          resultItemLink.invoke("data", "test-text").as("dataTestText");
          cy.get("@dataTestText").then((text) => {
            cy.url().should("include", text);
          });
        });
      });
  });

  it("should be able to click loadmore", () => {
    cy.visit(
      "/results/?q=Is%20a%20COVID-19%20vaccine%20the%20best%20way%20to%20control%20the%20pandemic%3F"
    );
    cy.wait(10000);

    cy.getByTestId("user-button").should("be.visible");
    cy.getByTestId("card-search-result-item").should("be.visible");
    cy.getByTestId("loadmore-button").should("be.visible");

    const loadmoreButton = cy.getByTestId("loadmore-button");
    loadmoreButton.click().then(() => {
      cy.getByTestId("card-search-results")
        .children()
        .should("have.length.greaterThan", 10);
    });
  });

  it("should be able to share", () => {
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");
    cy.wait(3000);
    cy.window().then((win) => {
      cy.stub(win, "open").as("openresult");
    });
    cy.wait(3000);
    cy.getByTestId("share-results").click();
    cy.getByTestId("twitter-share").click();
    cy.get("@openresult").should("be.called");
  });

  it("should be to go back", () => {
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");
    cy.wait(10000);
    cy.getByTestId("card-search-result-item")
      .first()
      .within(() => {
        cy.getByTestId("result-item-link").click();
      });

    cy.wait(3000);
    cy.url().should("include", "details");
    cy.go("back");
    cy.url().should("include", "results");
    cy.get('[data-testid="loadingsearchresult"]').should("not.exist");
  });

  it("should navigate to error page", () => {
    cy.visit("/search");

    cy.intercept(
      {
        method: "GET",
        url: "/api/search/*",
      },
      {
        forceNetworkError: true,
      }
    ).as("results");

    const text = "are covid-19 vaccines effective?";
    cy.getByTestId("user-button").should("be.visible");
    cy.getByTestId("search-input").type(text);
    cy.get("#search-button").click();
    cy.url().should("include", "/500");
  });

  it("should refetch data when same query executes", () => {
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");
    cy.getByTestId("user-button").should("be.visible");
    cy.getByTestId("card-search-result-item").should("be.visible");

    cy.get("#search-button").click();
    cy.getByTestId("card-search-result-item").should("be.visible");
  });
});

export {};
