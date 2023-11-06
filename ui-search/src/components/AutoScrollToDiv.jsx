import { useEffect, useRef } from 'react';

const AutoScrollToDiv = (data = {}) => {
  const refInputDiv = useRef(null);
  // NOTE: to automatically scroll down to the user input
  useEffect(() => {
    if (refInputDiv.current) {
      const elementPosition = refInputDiv.current.getBoundingClientRect().top;
      if (window.innerHeight < elementPosition) {
        refInputDiv.current?.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [refInputDiv, data]);
  return <div ref={refInputDiv} />;
};

export default AutoScrollToDiv;
