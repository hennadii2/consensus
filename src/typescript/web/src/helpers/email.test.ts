import { emailHasAllowedDomain, emailHasStudentDomain } from "./email";

export const MOCK_DOMAINS: { [key: string]: string } = {
  "northwestern.edu": "Northwestern University",
  "virginia.edu": "Univeristy of Virginia",
  "consensus.app": "Consensus App",
};

describe("helper/email", () => {
  describe("emailHasStudentDomain", () => {
    it("should allow .edu emails", () => {
      expect(emailHasStudentDomain("mock@university.edu")).toBeTruthy();
      expect(emailHasStudentDomain("mock@student.uwa.edu.au")).toBeTruthy();
      expect(emailHasStudentDomain("mock@student.uwa.edu")).toBeTruthy();
      expect(emailHasStudentDomain("mock@edu.student.uwa.au")).toBeTruthy();
    });

    it("should allow .ac emails", () => {
      expect(emailHasStudentDomain("mock@university.ac")).toBeTruthy();
      expect(emailHasStudentDomain("mock@student.uwa.ac.au")).toBeTruthy();
      expect(emailHasStudentDomain("mock@student.uwa.ac")).toBeTruthy();
      expect(emailHasStudentDomain("mock@ac.student.uwa.au")).toBeTruthy();
    });

    it("should block non .edu .ac emails", () => {
      expect(emailHasStudentDomain("mock@university.com")).toBeFalsy();
      expect(emailHasStudentDomain("mock@student.uwa.au")).toBeFalsy();
      expect(emailHasStudentDomain("mock@student.uwa.app")).toBeFalsy();
    });
  });

  describe("emailHasAllowedDomain", () => {
    it("should return null if email is not allowed", () => {
      expect(
        emailHasAllowedDomain("mock@university.com", MOCK_DOMAINS)
      ).toBeNull();
      expect(
        emailHasAllowedDomain("mock@university.com.app", MOCK_DOMAINS)
      ).toBeNull();
      expect(
        emailHasAllowedDomain("mock@northwestern.edu.app", MOCK_DOMAINS)
      ).toBeNull();
    });

    it("should allow primary and subdomain", () => {
      expect(
        emailHasAllowedDomain("mock@northwestern.edu", MOCK_DOMAINS)
      ).toEqual("Northwestern University");
      expect(
        emailHasAllowedDomain("mock@alum.northwestern.edu", MOCK_DOMAINS)
      ).toEqual("Northwestern University");
    });

    it("should return ending valid domain", () => {
      expect(
        emailHasAllowedDomain(
          "mock@northwestern.edu.consensus.app",
          MOCK_DOMAINS
        )
      ).toEqual("Consensus App");
      expect(
        emailHasAllowedDomain(
          "mock@consensus.app.northwestern.edu",
          MOCK_DOMAINS
        )
      ).toEqual("Northwestern University");
    });
  });
});
