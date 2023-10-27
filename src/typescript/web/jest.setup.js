import "@testing-library/jest-dom/extend-expect";
import "isomorphic-fetch";

window.matchMedia =
  window.matchMedia ||
  function () {
    return {
      matches: false,
      addListener: function () {},
      removeListener: function () {},
    };
  };
