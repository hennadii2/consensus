export function roundDownSignificantDigits(number: number, decimals: number) {
  let significantDigits = parseInt(number.toExponential().split("e-")[1]) || 0;
  let decimalsUpdated = (decimals || 0) + significantDigits - 1;
  decimals = Math.min(decimalsUpdated, number.toString().length);

  return Math.floor(number * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

export function numberWithCommas(x: string) {
  return x.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
