import Card from "components/Card";

export default function LoadingSubscriptionCard() {
  return (
    <div data-testid="loadingsubscriptioncard" className="">
      <Card className="mt-0">
        <div className="animate-pulse">
          <div className="flex space-x-10">
            <div className="flex-1">
              <div className="bg-loading-200 h-3 w-full  rounded-xl mb-4" />
              <div className="bg-loading-200 h-3 w-[50%] rounded-xl mb-4" />
              <div className="bg-loading-200 h-3 w-[60%] rounded-xl mb-4" />
              <div className="bg-loading-200 h-3 w-[70%] rounded-xl mb-4" />
              <div className="bg-loading-200 h-3 w-[80%] rounded-xl mb-4" />
              <div className="bg-loading-200 h-3 w-[90%] rounded-xl" />
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
