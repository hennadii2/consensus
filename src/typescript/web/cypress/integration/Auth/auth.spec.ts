describe("Auth", () => {
  before(() => {
    cy.initializeAuth();
  });

  it("should signin and signout", () => {
    cy.visit("/search/");

    // waiting for the clerk to be initiated
    cy.wait(3000);
    cy.signin();
    cy.signout();

    cy.url().should("include", "sign-in");

    // waiting for all events to be sent
    cy.wait(5000);
    cy.window().then((win) => {
      // login event analytics
      const login = win.dataLayer.filter(
        (item) => item.event === "login" && item.login_method === "email"
      );
      expect(login.length === 1).to.equal(true);
    });
  });

  it("should visit sign up page", () => {
    cy.visit("/sign-up");
    cy.reload(true);
    // waiting for the clerk to be initiated
    cy.wait(3000);
    cy.get("button").contains("Continue").should("be.visible");
  });

  it("should sign up redirect to google", () => {
    cy.visit("/sign-up");
    cy.reload(true);
    // waiting for the clerk to be initiated
    cy.wait(5000);
    cy.get("button").contains("Continue with Google").should("be.visible");
    cy.get("button").contains("Continue with Google").click();
  });

  it("should send single event analytics", () => {
    cy.visit("/sign-in");
    cy.reload(true);
    // waiting for the clerk to be initiated
    cy.wait(5000);
    cy.signin();

    // waiting for all events to be sent
    cy.wait(5000);
    cy.window().then((win) => {
      // login event analytics
      const login = win.dataLayer.filter((item) => item.event === "login");
      expect(login.length === 1).to.equal(true);

      // signup event analytics
      const signup = win.dataLayer.filter((item) => item.event === "signup");
      expect(signup.length === 0).to.equal(true);
    });

    cy.signout();
    cy.url().should("include", "sign-in");
  });
});

export {};
