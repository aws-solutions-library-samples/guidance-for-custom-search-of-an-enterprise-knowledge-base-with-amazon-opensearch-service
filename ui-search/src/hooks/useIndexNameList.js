import { useEffect, useState } from 'react';
import useLsAppConfigs from './useLsAppConfigs';
import toast from 'react-hot-toast';

const useIndexNameList = () => {
  const { urlApiGateway } = useLsAppConfigs();
  const [indexNameList, setIndexNameList] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${urlApiGateway}/knowledge_base_handler`)
      .then((res) => {
        if (res.ok) {
          return res.json();
        }
        throw new Error('Network response was not ok.');
      })
      .then((data) => {
        setIndexNameList(data.map((item) => item.name));
      })
      .catch((error) => {
        toast.error('Error fetching knowledge base index names');
      })
      .finally(() => setLoading(false));
  }, [urlApiGateway]);

  return { indexNameList, loading };
};

export default useIndexNameList;
