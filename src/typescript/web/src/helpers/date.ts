export function getMinutesBetweenDates(startDate: Date, endDate: Date): number {
  var diff = endDate.getTime() - startDate.getTime();
  return Math.round(diff / 60000);
}

export function getDaysBetweenDates(startDate: Date, endDate: Date): number {
  var diff = endDate.getTime() - startDate.getTime();
  return Math.round(diff / (1000 * 60 * 60 * 24));
}
