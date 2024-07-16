import { useCallback, useState } from 'react';

/**
 * ‼️ Only use this for Cloudscape-design components
 */
const useInput = <T = string>(initValue?: T, cb?: (v: T) => any) => {
  const [value, setValue] = useState(initValue);
  const bind = {
    value,
    onChange: ({ detail }) => {
      setValue(detail.value);
      if (cb) cb(detail.value);
    },
  };
  const reset = useCallback(
    (v?: typeof initValue) => setValue(v ?? initValue),
    [initValue]
  );
  return [value, bind, reset, setValue] as const;
};

export default useInput;
