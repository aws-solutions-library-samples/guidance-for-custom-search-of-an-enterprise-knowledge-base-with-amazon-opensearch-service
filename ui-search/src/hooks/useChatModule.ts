import { useCallback, useState } from 'react';
import useLsAppConfigs from './useLsAppConfigs';
import toast from 'react-hot-toast';

const useChatModule = () => {
  const [chatModuleResult, setChatModuleResult] = useState();
  const { urlApiGateway } = useLsAppConfigs();

  /**
   * Promise<a query string>
   */
  const getChatModuleResult = useCallback(
    async ({ configs, question }) => {
      try {
        const res = await fetch(`${urlApiGateway}/langchain_processor_qa`, {
          method: 'POST',
          body: JSON.stringify({ configs, question, requestType: 'restful' }),
        });

        const data = await res.json();
        if (data?.message === 'error') {
          toast.error(data.errorMessage);
          console.warn('Error Data got from CHAT module: ', data);
          return '';
        }
        if (!data?.text) {
          const msg = 'No text returned from CHAT module';
          toast.error(msg);
          throw new Error(msg);
        }
        if (data?.text && !data.text.includes('query')) {
          toast(data.text, { icon: '🤔', duration: 10000 });
          return '';
        }
        // data example: the result of JSON.stringify({query:'xxxx'}), hence ⬇️
        const parsedData = JSON.parse(data.text);
        // TODO: regex match in case of llm error outputs
        // const match = parsedData.match(/"?({.*})"?/);
        // if (match?.length === 2) {
        //   const result = JSON.parse(match[1]);
        //   if (result.query) setChatModuleResult(result);
        //   return result;
        // } else {
        //   throw new Error(`Error matching chat module response ${data.query}`);
        //   //...
        // }
        if (!parsedData?.query)
          throw new Error('LLM output error: no "query" in LLM response');
        setChatModuleResult(parsedData.query);
        return parsedData.query;
      } catch (error) {
        console.debug('Error processing chat_module_response: ', error);
        toast.error(
          'Error processing chat_module_response: check browser console for more error info'
        );
        return 'Error processing chat_module_response';
      }
    },
    [urlApiGateway]
  );
  return { chatModuleResult, getChatModuleResult };
};

export default useChatModule;
