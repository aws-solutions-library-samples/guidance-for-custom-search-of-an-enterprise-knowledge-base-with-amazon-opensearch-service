import { LSK } from 'src/constants';
import useLocalStorage from 'use-local-storage';

/**
 * To manage CRUD operations to Arrays in localStorage
 */
const useLsArray = <T = any>(
  key: keyof typeof LSK,
  idName = 'id',
  initValue: T[] = [],
  options?: Parameters<typeof useLocalStorage<T[]>>[2]
) => {
  const [value, setValue] = useLocalStorage<T[]>(key, initValue, options);

  return {
    // commons
    value,
    setValue,
    add: (newValue: T) => setValue((prev) => [...prev, newValue]),
    clear: () => setValue([]),
    reset: () => setValue(initValue),

    // Operate by index
    // getIndex: (index) => value[index],
    delIndex: (index: number) =>
      setValue((prev) => prev.filter((_, i) => i !== index)),
    updateIndex: (index, newValue) =>
      setValue((prev) =>
        prev.map((item, i) => (i === index ? newValue : item))
      ),

    // Operate by ID
    getById: (id: string, arr: T[]) => arr.find((item) => item[idName] === id),
    delById: (id: string) =>
      setValue((prev) => prev.filter((item) => item[idName] !== id)),
    updateById: (id: string, newValue: T) => {
      setValue((prev) => {
        return prev.map((item) => (item[idName] === id ? newValue : item));
      });
    },
  };
};

export default useLsArray;
