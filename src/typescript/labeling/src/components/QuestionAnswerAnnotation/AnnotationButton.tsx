type AnnotationButtonProps = {
  label: number;
  isSelected: boolean;
  color: string;
  onClick: (label: number) => void;
};

const AnnotationButton = (props: AnnotationButtonProps) => {
  const { color, label } = props;
  const btnColor = props.isSelected ? color : "white";
  const activeWeight = 400;
  const btnWeight = props.isSelected ? activeWeight : 300;

  const handleOnClick = () => {
    props.onClick(label);
  };

  return (
    <button
      type="button"
      onClick={handleOnClick}
      className={`inline-block px-6 py-2.5 bg-${btnColor}-${btnWeight} text-gray font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-${color}-${btnWeight} hover:shadow-lg focus:bg-${btnColor}-${btnWeight} focus:shadow-lg focus:outline-none focus:ring-0 active:bg-${btnColor}-800 active:shadow-lg transition duration-150 ease-in-out`}
    >
      {label}
    </button>
  );
};

export default AnnotationButton;
