import { useState } from 'react';

/**
 * ‼️ Only use this for Cloudscape-design components
 */
const useToggle = (initValue = false, cb = (boolean) => {}) => {
  const [checked, setChecked] = useState(initValue);
  const bind = {
    checked,
    onChange: ({ detail }) => {
      setChecked(detail.checked);
      cb(detail.checked);
    },
  };
  const reset = () => setChecked(initValue);
  return [checked, bind, reset, setChecked];
};

export default useToggle;
