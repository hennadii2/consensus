import { INTERCOM_API_IDENTITY_VERIFICATION_SECRET } from "constants/config";
import { enc, HmacSHA256 } from "crypto-js";

export const generateHmac = (userId: string): string => {
  const hash = HmacSHA256(
    userId,
    INTERCOM_API_IDENTITY_VERIFICATION_SECRET!
  ).toString(enc.Hex);
  return hash;
};
