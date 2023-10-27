import { screen } from "@testing-library/react";
import { ISubscriptionUsageData } from "helpers/subscription";
import SubscriptionUsageCard from "../SubscriptionUsageCard/SubscriptionUsageCard";
import { renderWithProviders } from "./../../../__tests__/renderWithProvider";

describe("components/SubscriptionUsageCard", () => {
  it("should render SubscriptionUsageCard", () => {
    const handleClick = jest.fn();
    const data: ISubscriptionUsageData = {
      creditUsageNum: 1,
      userCreatedDate: "June 12, 2023",
      stripeCustomerId: "",
      isSet: false,
      synthesizedQueries: [],
      studyPaperIds: [],
    };
    renderWithProviders(
      <SubscriptionUsageCard subscriptionUsageData={data} isPremium={false} />
    );

    const title: HTMLElement = screen.getByText("Usage");
    expect(title).toBeInTheDocument();

    const noCreditLeftTitle: HTMLElement = screen.getByTestId(
      "no-credits-left-title"
    );
    expect(noCreditLeftTitle).toBeInTheDocument();

    const noBookmarkLeftTitle: HTMLElement = screen.getByTestId(
      "no-bookmark-left-title"
    );
    expect(noBookmarkLeftTitle).toBeInTheDocument();

    const refreshDate: HTMLElement = screen.getByTestId("refresh-date-text");
    expect(refreshDate).toHaveTextContent("July 12, 2023");
  });

  it("should render SubscriptionUsageCard 2", () => {
    const handleClick = jest.fn();
    const data: ISubscriptionUsageData = {
      creditUsageNum: 20,
      userCreatedDate: "May 15, 2023",
      stripeCustomerId: "",
      synthesizedQueries: [],
      studyPaperIds: [],
      isSet: true,
    };
    renderWithProviders(
      <SubscriptionUsageCard subscriptionUsageData={data} isPremium={true} />
    );

    const title: HTMLElement = screen.getByText("Usage");
    expect(title).toBeInTheDocument();

    const unlimitedTitle: HTMLElement = screen.getByTestId(
      "ai-credits-unlimited-title"
    );
    expect(unlimitedTitle).toBeInTheDocument();

    const refreshDate: HTMLElement | null =
      screen.queryByTestId("refresh-date-text");
    expect(refreshDate).toBeNull();
  });
});
