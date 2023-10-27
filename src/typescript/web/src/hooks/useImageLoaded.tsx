import { useEffect, useRef, useState } from "react";

const useImageLoaded = () => {
  const [loaded, setLoaded] = useState(false);
  const ref = useRef(null);

  const onLoad = () => {
    setLoaded(true);
  };

  useEffect(() => {
    if (ref.current && (ref.current as any).complete) {
      onLoad();
    }
  });

  return { ref, loaded, onLoad };
};

export default useImageLoaded;
