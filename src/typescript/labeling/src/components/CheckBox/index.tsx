type CheckBoxProps = {
  label: string;
  onChange: () => void;
  isChecked: boolean;
};

const CheckBox = ({ label, onChange, isChecked }: CheckBoxProps) => {
  return (
    <div>
      <div className="form-check" />
      <input
        type="checkbox"
        value=""
        checked={isChecked}
        onChange={onChange}
        id="flexCheckDefault"
        className={
          "form-check-input h-4 w-4 border border-gray-300 rounded-sm " +
          "bg-white checked:bg-blue-600 checked:border-blue-600 focus:outline-none " +
          "transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain float-left mr-2 cursor-pointer"
        }
      />
      <label className="form-check-label inline-block text-gray-800">
        {label}
      </label>
    </div>
  );
};

export default CheckBox;
