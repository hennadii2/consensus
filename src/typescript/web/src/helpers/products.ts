import { STRIPE_PRICE_METADATA_TYPE_PREMIUM } from "constants/config";
import { ISubscriptionData } from "./subscription";

export interface SubscriptionProduct {
  name: string | null;
  price: any | null;
}

export interface MonthAnnualPrice {
  monthPrice: any;
  annualPrice: any;
}

export function sortProducts(products: any): any {
  products.map((product: any) => {
    product.product_data.prices.sort((a: any, b: any) => {
      return a.unit_amount - b.unit_amount;
    });
  });

  products.sort((a: any, b: any) => {
    let aHighPrice = 0;
    let bHighPrice = 0;
    for (let i = 0; i < a.product_data.prices.length; i++) {
      if (a.product_data.prices[i].unit_amount > aHighPrice) {
        aHighPrice = a.product_data.prices[i].unit_amount;
      }
    }
    for (let i = 0; i < b.product_data.prices.length; i++) {
      if (b.product_data.prices[i].unit_amount > bHighPrice) {
        bHighPrice = b.product_data.prices[i].unit_amount;
      }
    }
    return aHighPrice - bHighPrice;
  });

  return products;
}

export function getUpgradePrice(products: any, upgradePlan: string): any {
  let upgradePrice = null;
  products.map((product: any) => {
    if (
      product.product_data.metadata?.tier == upgradePlan.toLocaleLowerCase() &&
      product.product_data.prices.length > 0
    ) {
      for (let i = 0; i < product.product_data.prices.length; i++) {
        if (
          product.product_data.prices[i].unit_amount > 0 &&
          product.product_data.prices[i].recurring.interval == "year" &&
          product.product_data.prices[i].metadata.type ==
            STRIPE_PRICE_METADATA_TYPE_PREMIUM
        ) {
          upgradePrice = product.product_data.prices[i];
          break;
        }
      }
    }
  });
  return upgradePrice;
}

export function findSubscriptionProduct(
  products: any,
  subscription: ISubscriptionData | null | undefined
): SubscriptionProduct {
  if (products && subscription?.user) {
    for (const product of products) {
      for (const price of product.product_data.prices) {
        if (subscription.user.plan.id == price.id) {
          return {
            name: product.product_data.name,
            price: price,
          };
        }
      }
    }
  }

  return { name: null, price: null };
}

export function getMonthAnnualPrices(products: any): MonthAnnualPrice {
  let monthPrice = null;
  let annualPrice = null;
  if (products && products.length > 0) {
    products[0].product_data.prices.map((price: any) => {
      if (
        price.recurring.interval == "month" &&
        price.metadata.type == STRIPE_PRICE_METADATA_TYPE_PREMIUM
      ) {
        monthPrice = price;
      }

      if (
        price.unit_amount > 0 &&
        price.recurring.interval == "year" &&
        price.metadata.type == STRIPE_PRICE_METADATA_TYPE_PREMIUM
      ) {
        annualPrice = price;
      }
    });
  }

  return {
    monthPrice: monthPrice,
    annualPrice: annualPrice,
  };
}
