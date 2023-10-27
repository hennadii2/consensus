/** Page to display all configured CSS colors in the project. **/
import classNames from "classnames";
import COLORS from "constants/colors.json";
import useDevelopmentComponent from "hooks/useDevelopmentComponent";
import isObject from "lodash/isObject";
import type { NextPage } from "next";

type ColorProps = {
  color: string;
  suffix?: string;
};

const ColorTitle = ({ color }: ColorProps) => {
  return <p className="uppercase mb-4">{color}</p>;
};

const ColorPreview = ({ color, suffix }: ColorProps) => {
  return (
    <div className="inline-flex flex-col items-center">
      <div className={`bg-${color} w-10 h-10 rounded-full shadow-lg`} />
      <p className="text-sm mt-2 text-gray-300">
        {color}
        {suffix && `-${suffix}`}
      </p>
    </div>
  );
};

/**
 * Colors page
 */
const Colors: NextPage = () => {
  useDevelopmentComponent();

  return (
    <div className="grid place-items-center py-96">
      <div className="bg-gray-100 p-20 rounded-3xl shadow-2xl w-1/2">
        <p className="text-2xl font-semibold mb-8">Colors</p>
        {Object.keys(COLORS).map((color, index) => {
          const colorKeys = (COLORS as any)[color];

          if (isObject(colorKeys)) {
            return (
              <div key={color} className={classNames(index !== 0 && "mt-6")}>
                <ColorTitle color={color} />
                <div className="flex gap-x-8">
                  {Object.keys(colorKeys).map((item) => (
                    <ColorPreview
                      key={`${color}-${item}`}
                      color={`${color}-${item}`}
                    />
                  ))}
                </div>
              </div>
            );
          }

          return (
            <div key={color} className={classNames(index !== 0 && "mt-4")}>
              <ColorTitle color={color} />
              <ColorPreview color={color} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Colors;
