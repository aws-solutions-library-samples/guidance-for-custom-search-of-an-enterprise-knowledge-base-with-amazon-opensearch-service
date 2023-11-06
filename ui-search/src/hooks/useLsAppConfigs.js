import { LSK } from 'src/constants';
import useLocalStorage from 'use-local-storage';

export const INIT_APP_CONFIGS = {
  urlWss: 'wss://tg4k9c6ol5.execute-api.us-west-2.amazonaws.com/prod',
  urlApiGateway: 'https://31c9ke6fk8.execute-api.us-west-2.amazonaws.com/prod',
  s3FileUpload: 'intelligent-search-data-bucket-955643200499-us-west-2',
  // vector, text, mix
  searchMethod: 'vector',
  txtDocsNum: 0,
  vecDocsScoreThresholds: 0,
  txtDocsScoreThresholds: 0,
  responseIfNoDocsFound: 'Cannot find the answer',
  mode: 'light',
  density: 'comfortable',
  tokenContentCheck: '',
};

const useLsAppConfigs = () => {
  const [appConfigs, setAppConfigs] = useLocalStorage(
    LSK.appConfigs,
    INIT_APP_CONFIGS
  );

  return {
    urlWss: appConfigs.urlWss,
    urlApiGateway: appConfigs.urlApiGateway,
    s3FileUpload: appConfigs.s3FileUpload,
    setAConfig: (key, value) =>
      setAppConfigs((prev) => ({ ...prev, [key]: value })),
    appConfigs,
    setAppConfigs,
  };
};

export default useLsAppConfigs;
