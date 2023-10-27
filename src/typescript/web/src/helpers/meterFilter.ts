import { MeterFilterParams } from "types/MeterFilterParams";
import { YesNoType } from "types/YesNoType";

export const defaultMeterFilter: MeterFilterParams = {
  no: true,
  possibly: true,
  yes: true,
};

export function getIsMeterFilterActive(
  meterFilter: MeterFilterParams
): boolean {
  return !(meterFilter.yes && meterFilter.possibly && meterFilter.no);
}

export function removedByYesNoMeterFilter(
  meterFilter: MeterFilterParams,
  yesNoType?: YesNoType
): boolean {
  if (!meterFilter.yes && yesNoType === "YES") {
    return false;
  }
  if (!meterFilter.no && yesNoType === "NO") {
    return false;
  }
  if (!meterFilter.possibly && yesNoType === "POSSIBLY") {
    return false;
  }
  if (yesNoType === "UNKNOWN") {
    return false;
  }
  if (!yesNoType) {
    return false;
  }
  return true;
}
