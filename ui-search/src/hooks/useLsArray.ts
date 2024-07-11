import useLocalStorage from 'use-local-storage';

/**
 * To manage CRUD operations to Arrays in localStorage
 */
const useLsArray = (
  key,
  idName = 'id',
  initValue = [],
  options = undefined
) => {
  const [value, setValue] = useLocalStorage(key, initValue, options);

  return {
    // commons
    value,
    setValue,
    add: (newValue) => setValue((prev) => [...prev, newValue]),
    clear: () => setValue([]),
    reset: () => setValue(initValue),

    // Operate by index
    // getIndex: (index) => value[index],
    delIndex: (index) => setValue((prev) => prev.filter((_, i) => i !== index)),
    updateIndex: (index, newValue) =>
      setValue((prev) =>
        prev.map((item, i) => (i === index ? newValue : item))
      ),

    // Operate by ID
    getById: (id, arr) => arr.find((item) => item[idName] === id),
    delById: (id) =>
      setValue((prev) => prev.filter((item) => item[idName] !== id)),
    updateById: (id, newValue) => {
      setValue((prev) => {
        return prev.map((item) => (item[idName] === id ? newValue : item));
      });
    },
  };
};

export default useLsArray;
