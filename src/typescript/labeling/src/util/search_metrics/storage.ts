import { QA_METRICS_BUCKET_PATH } from "constants/paths";
import { downloadJson } from "util/storage";

export type SearchMetrics = { [key: string]: any };

/** Downloads search metrics file from GCS and returns the data. */
export async function downloadMetrics(
  jsonFileName: string
): Promise<SearchMetrics | null> {
  if (!jsonFileName.endsWith(".json")) {
    jsonFileName = jsonFileName + ".json";
  }
  const data = await downloadJson(jsonFileName, QA_METRICS_BUCKET_PATH);
  if (data === null) {
    console.error(`Missing file: ${QA_METRICS_BUCKET_PATH}/${jsonFileName}`);
  }
  return data;
}
