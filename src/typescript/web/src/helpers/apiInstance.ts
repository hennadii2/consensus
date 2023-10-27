import axios from "axios";

// Number of ms to keep a network connection alive.
const REQUEST_TIMEOUT_MILLISECONDS = 300000;

// True if the call is made on the server, false otherwise
// https://github.com/vercel/next.js/issues/5354#issuecomment-520305040
export const isServer = (): boolean => {
  return typeof window === "undefined";
};

/** Kicks off a network request to the backend. */
const apiInstance = axios.create({
  baseURL: isServer() ? process.env.HOST : "/api",
  timeout: REQUEST_TIMEOUT_MILLISECONDS,
});

export default apiInstance;
