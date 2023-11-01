import { useEffect } from 'react';
import toast from 'react-hot-toast';
import { useLocation, useNavigate } from 'react-router-dom';
import useLsAppConfigs from './useLsAppConfigs';

const pleaseConfigure = (what) =>
  toast(
    what
      ? `Please configure: ${what}`
      : `Please complete the app configuration beforehand!`,
    {
      icon: '👏',
    }
  );
const useCheckAppConfigsEffect = () => {
  const { appConfigs } = useLsAppConfigs();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!appConfigs.urlWss || !appConfigs.urlApiGateway) {
      pleaseConfigure();
      if (location.pathname !== '/app-configs') navigate('/app-configs');
    }
    if (!appConfigs.urlWss) pleaseConfigure('WebSocket URL');
    if (!appConfigs.urlApiGateway) pleaseConfigure('API Gateway URL');
  }, [location, appConfigs.urlWss, appConfigs.urlApiGateway, navigate]);
};

export default useCheckAppConfigsEffect;
