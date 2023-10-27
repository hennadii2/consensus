describe("Details page", () => {
  before(() => {
    // sign in
    cy.visit("/search");
    // waiting for the clerk to be initiated
    cy.wait(3000);
    cy.signin();
  });

  beforeEach(() => {
    cy.wait(10000);
    cy.visit("/results/?q=are%20covid-19%20vaccines%20effective%3F");
    cy.wait(10000);
    cy.getByTestId("card-search-result-item")
      .first()
      .within(() => {
        cy.getByTestId("result-item-link").click();
      });
  });

  it("should open the details page with topbar with search input, claim details, paper, journal, related claims", () => {
    cy.getByTestId("topbar").within(() => {
      cy.getByTestId("search-input").should("be.visible");
    });
    cy.getByTestId("result-claim").should("be.visible");
    cy.getByTestId("result-paper").should("be.visible");
    cy.getByTestId("result-journal").should("be.visible");
  });

  it("should update the details page when clicking one of the title of the related claims", () => {
    const oldUrl = cy.url();

    // click 1 of the related claim
    cy.getByTestId("card-search-result-item")
      .first()
      .within(() => {
        cy.getByTestId("result-item-link").click();
      });

    expect(oldUrl).to.not.equal(cy.url());
  });

  it("should be able to share", () => {
    // handle open new tab
    cy.window().then((win) => {
      cy.stub(win, "open").as("open");
    });

    cy.getByTestId("share-detail").click();
    cy.getByTestId("twitter-share").click();
    cy.get("@open").should("have.been.calledOnce");
  });

  it("should redirect to correct slug", () => {
    cy.getByTestId("result-claim").should("be.visible");
    cy.location().then((loc) => {
      const splits = loc.pathname.split("/");
      splits[2] = "test";
      const newPathname = splits.join("/");
      cy.visit(newPathname);
      cy.url().should("eq", loc.href);
    });
  });
});

export {};
