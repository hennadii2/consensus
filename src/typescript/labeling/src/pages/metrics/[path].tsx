import { GetServerSidePropsContext } from "next";
import { downloadMetrics, SearchMetrics } from "util/search_metrics/storage";

const FILE_NOT_FOUND_ERROR = "File not found";

interface SearchMetricsProps {
  fileName: string;
  metrics: SearchMetrics | null;
}

const SearchMetrics = ({ fileName, metrics }: SearchMetricsProps) => {
  return (
    <div className="flex flex-col">
      <h1 className="flex-none">{`${fileName}`}</h1>
      {metrics !== null && (
        <div>
          <pre>{JSON.stringify(metrics, null, 2)}</pre>
        </div>
      )}
      {metrics === null && <div>{FILE_NOT_FOUND_ERROR}</div>}
    </div>
  );
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const fileName = context.query.path?.toString() || "";
  const metrics = await downloadMetrics(fileName);
  return {
    props: {
      fileName: fileName,
      metrics,
    },
  };
}

export default SearchMetrics;
