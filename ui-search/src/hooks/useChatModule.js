import { useCallback, useState } from 'react';
import useLsAppConfigs from './useLsAppConfigs';
import toast from 'react-hot-toast';

const useChatModule = () => {
  const [chatModuleResult, setChatModuleResult] = useState();
  const { urlApiGateway } = useLsAppConfigs();

  // https://o3whwqjb3e.execute-api.us-west-2.amazonaws.com/prod/langchain_processor_qa?query=what is the safety preparation?&task=qa&session_id=qa1713510282.083172&top_k=1&textField=text&imageField=image_base64&vectorField=vector_field&requestType=http&streaming=False&modelType=bedrock&modelName=anthropic.claude-3-sonnet-20240229-v1:0&workMode=multi-model&language=english&embeddingEndpoint=cohere.embed-multilingual-v3&sagemakerEndpoint=anthropic.claude-3-sonnet-20240229-v1:0&index=multi-model-test-0419

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
