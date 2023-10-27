import useInterval from "hooks/useInterval";
import { useCallback, useState } from "react";
import Spinner from "./Spinner";

const AUTO_SAVE_MILLISECONDS = 5000;

type SaveButtonProps = {
  onSave: () => Promise<void>;
  autoSave: boolean;
  needsSave: boolean;
};

const SaveButton = ({ onSave, autoSave, needsSave }: SaveButtonProps) => {
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const color = needsSave ? "bg-red-600" : "bg-gray-400";
  const hoverColor = needsSave ? "bg-red-500" : "bg-gray-400";

  useInterval(
    () => {
      if (needsSave) {
        handleOnClick();
      }
    },
    autoSave ? AUTO_SAVE_MILLISECONDS : null
  );

  const handleOnClick = useCallback(async () => {
    setIsSaving(true);
    await onSave();
    setIsSaving(false);
  }, [onSave]);

  return (
    <div className="flex items-center justify-center">
      <button
        type="button"
        onClick={handleOnClick}
        disabled={isSaving || !needsSave}
        className={`inline-flex items-center px-4 py-2 text-sm font-semibold leading-6 text-white transition duration-150 ease-in-out ${color} rounded-md shadow hover:${hoverColor}`}
      >
        {isSaving && <Spinner />}
        {isSaving ? "Saving..." : needsSave ? "Save" : "Saved"}
      </button>
    </div>
  );
};

export default SaveButton;
