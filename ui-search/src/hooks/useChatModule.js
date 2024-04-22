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
        // const res = await fetch(`${urlApiGateway}/chat-module`, {
        //   method: 'POST',
        //   body: JSON.stringify({ configs, question, requestType: 'restful' }),
        // });

        const params = new URLSearchParams({
          configs: JSON.stringify(configs),
          question: JSON.stringify(question),
          requestType: 'restful',
        });
        const url = `${urlApiGateway}?${params}`;
        const res = await fetch(url);
        const data = await res.json();
        // data example: the result of JSON.stringify({query:'xxxx'}), hence ⬇️
        const parsedData = JSON.parse(data);
        if (!parsedData.query)
          throw new Error('LLM output error: no "query" in LLM response');

        setChatModuleResult(parsedData.query);
        return parsedData.query;

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
      } catch (error) {
        console.error('Error processing chat_module_response: ', error);
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
