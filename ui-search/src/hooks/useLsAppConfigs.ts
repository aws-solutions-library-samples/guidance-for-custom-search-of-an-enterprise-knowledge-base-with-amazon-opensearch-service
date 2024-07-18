import { LSK } from 'src/constants';
import useLocalStorage from 'use-local-storage';

export const INIT_APP_CONFIGS = {
  urlWss: JSON.parse(process.env.REACT_APP_DEMO)
    ? process.env.REACT_APP_URL_WSS
    : '',
  urlApiGateway: JSON.parse(process.env.REACT_APP_DEMO)
    ? process.env.REACT_APP_URL_APIGATEWAY
    : '',
  s3FileUpload: '',
  responseIfNoDocsFound: 'Cannot find the answer',
  mode: 'light',
  density: 'comfortable',
  // tokenContentCheck: '',
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
