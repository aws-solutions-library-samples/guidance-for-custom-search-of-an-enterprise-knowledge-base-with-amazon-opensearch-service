import { useCallback, useState } from 'react';

/**
 * ‼️ Only use this for Cloudscape-design components
 */
const useInput = (initValue = '', cb) => {
  const [value, setValue] = useState(initValue);
  const bind = {
    value,
    onChange: ({ detail }) => {
      setValue(detail.value);
      if (cb) cb(detail.value);
    },
  };
  const reset = useCallback((v) => setValue(v || initValue), [initValue]);
  return [value, bind, reset, setValue];
};

export default useInput;
