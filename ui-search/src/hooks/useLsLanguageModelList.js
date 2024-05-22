import { LSK } from 'src/constants';
import useLsArray from './useLsArray';
import LLM_STRATEGY_TEMPLATE from 'src/utils/LLM_STRATEGY_TEMPLATE';

const useLsLanguageModelList = () => {
  const {
    value: lsLanguageModelList,
    setValue: setLsLanguageModelList,
    add: lsAddLanguageModelItem,
    clear: lsClearLanguageModelList,
    getById: lsGetLanguageModelItem,
    delById: lsDelLanguageModelItem,
  } = useLsArray(LSK.languageModelList, 'recordId', LLM_STRATEGY_TEMPLATE);

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
