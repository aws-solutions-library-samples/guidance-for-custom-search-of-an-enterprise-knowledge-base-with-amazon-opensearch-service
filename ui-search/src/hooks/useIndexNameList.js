import { useEffect, useState } from 'react';
import useLsAppConfigs from './useLsAppConfigs';
import toast from 'react-hot-toast';

const useIndexNameList = (bool = true) => {
  const { urlApiGateway } = useLsAppConfigs();
  const [indexNameList, setIndexNameList] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    if (!urlApiGateway) return setLoading(false);
    let timer = setTimeout(() => {
      if (bool) {
        fetch(`${urlApiGateway}/knowledge_base_handler`)
          .then((res) => {
            if (res.ok) return res.json();
            throw new Error('Network response was not ok.');
          })
          .then((data) => setIndexNameList(data.map((item) => item.name)))
          .catch((error) => {
            toast.error('Error fetching knowledge base index names');
            setIndexNameList([]);
          })
          .finally(() => setLoading(false));
      }
    }, 1000);
    return () => clearTimeout(timer);
  }, [urlApiGateway, bool]);

  return { indexNameList, loading };
};

export default useIndexNameList;
