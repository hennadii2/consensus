import classNames from "classnames";
import Icon from "components/Icon";
import React, { ChangeEvent, ReactNode, useEffect, useState } from "react";

type FeatureFlagItemProps = {
  name: string;
  features: string[];
  onChange(e: ChangeEvent<HTMLInputElement>): void;
  children: ReactNode;
};

const FeatureFlagItem = ({
  name,
  features,
  onChange,
  children,
}: FeatureFlagItemProps) => {
  const [isActive, setIsActive] = useState<boolean>(false);

  useEffect(() => {
    setIsActive(features?.includes(name));
  }, [setIsActive, features, name]);

  return (
    <div data-testid="feature-flag-item" className="mb-4">
      <input
        type="checkbox"
        name={name}
        id={name}
        checked={isActive}
        onChange={onChange}
        className="hidden"
        data-testid="feature-flag-input"
      />
      <label
        htmlFor={name}
        className="flex items-center cursor-pointer select-none"
      >
        <Icon
          name={isActive ? "check-square" : "square"}
          className={classNames(
            "mr-2",
            isActive ? "text-green-600" : "text-gray-800"
          )}
          size={20}
          data-testid="feature-flag-icon"
        />
        {children}
      </label>
    </div>
  );
};

export default FeatureFlagItem;
