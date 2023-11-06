import { LSK } from 'src/constants';
import useLsArray from './useLsArray';

const useLsLanguageModelList = () => {
  const {
    value: lsLanguageModelList,
    setValue: setLsLanguageModelList,
    add: lsAddLanguageModelItem,
    clear: lsClearLanguageModelList,
    getById: lsGetLanguageModelItem,
    delById: lsDelLanguageModelItem,
  } = useLsArray(LSK.languageModelList, 'recordId');

  return {
    lsLanguageModelList,
    setLsLanguageModelList,
    lsAddLanguageModelItem,
    lsClearLanguageModelList,
    lsGetLanguageModelItem,
    lsDelLanguageModelItem,
  };
};

export default useLsLanguageModelList;
