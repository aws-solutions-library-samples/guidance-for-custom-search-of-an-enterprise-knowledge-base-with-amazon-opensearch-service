class BedrockAdapter:
    @classmethod
    def prepare_input(
            cls, provider: str, prompt: str, model_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        input_body = {**model_kwargs}
        if provider == "anthropic":
            input_body["prompt"] = _human_assistant_format(prompt)
        elif provider == "ai21" or provider == "cohere":
            input_body["prompt"] = prompt
        elif provider == "amazon":
            input_body = dict()
            input_body["inputText"] = prompt
            input_body["textGenerationConfig"] = {**model_kwargs}
        else:
            input_body["prompt"] = prompt

        if provider == "anthropic" and "max_tokens_to_sample" not in input_body:
            input_body["max_tokens_to_sample"] = 256

        if "prompt" in event['queryStringParameters'].keys():
            prompt = event['queryStringParameters']['prompt']


        max_tokens=512
        if "max_tokens" in input_body.keys():
            max_tokens = int(input_body['max_tokens'])
        print('max_tokens:',max_tokens)

        modelId = 'anthropic.claude-v2'
        if "modelId" in input_body.keys():
            modelId = input_body['modelId']
        print('modelId:',modelId)

        temperature=0.01
        if "temperature" in input_body.keys():
            temperature = float(input_body['temperature'])
        print('temperature:',temperature)


        if modelId.find('claude') >=0:
            input_body = json.dumps({"prompt": prompt, "max_tokens_to_sample": max_tokens,"temperature": temperature})
        elif modelId == 'amazon.titan-tg1-large':
            input_body = json.dumps({"inputText": prompt,
                               "textGenerationConfig" : {
                                   "maxTokenCount": max_tokens,
                                   "stopSequences": [],
                                   "temperature":temperature,
                                   "topP":0.9
                               }
                               })
        elif modelId == 'amazon.titan-e1t-medium':
            input_body = json.dumps({"inputText": prompt})
        elif modelId == 'meta.llama2-13b-chat-v1':
            input_body = json.dumps({
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature,
                "top_p": 0.9
            })
        return input_body