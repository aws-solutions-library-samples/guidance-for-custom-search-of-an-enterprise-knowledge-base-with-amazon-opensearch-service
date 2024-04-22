import { configs } from './ragModule';

export const exampleChatSystemPrompt = `任务要求:
1. 接受图片和文字作为输入,输入格式不作限制
2. 根据输入的图片和文字信息生成一句综合描述
3. 描述内容尽可能详尽

输出要求:
输出必须严格符合以下JSON格式,不包含任何其他多余的文字或说明,只输出JSON数据
{
  "query": "一句综合描述"
}

其中,"query"字段的值为根据输入图片和文字生成的一句综合描述

示例输入:
图片1, 图片2
文字 "这是一段关于旅游的介绍,描述了某个城市的地理位置、景点等信息。"

示例输出(注意,下面的输出中只包含JSON数据,没有其他多余信息):
{"query": "这是一张展示户外自然景观的图片,图中有蓝天、绿树和溪流,并附有一段关于某个城市旅游景点和地理位置的文字介绍。"}

注意事项:
1. 输出格式必须严格遵守给定的JSON格式
2. 除JSON数据外,不输出任何其他多余的文字或说明`;

/**
 * CHAT module: restful api
 * @method POST: body example below:
 */
export const chatModuleRequest = {
  configs: {
    // v3.2 RAG configs
    ...configs,
    workMode: 'multi-modal',
    chatSystemPrompt: JSON.stringify(exampleChatSystemPrompt),
  },
  // multi-modal: user input
  question: [
    { type: 'text', text: "What's in this image?" },
    { type: 'image', base64: 'iVBORw...' },
    { type: 'text', text: 'and in this image' },
    { type: 'image', base64: 'iVBORw...' },
  ],
};

/**
 * @return a string that contains whatever output user defined in the prompt
 */
const chatModuleResponse = JSON.stringify({
  query: `What's in this image? <img> and in this image <img>`,
  question: [],
});

try {
  const match = chatModuleResponse.match(/"?({.*})"?/);
  if (match?.length === 2) {
    const res = JSON.parse(match[1]);
    console.log({ res });
  } else {
    throw new Error(
      `Error matching chat module response ${chatModuleResponse}`
    );
    //...
  }
} catch (error) {
  console.error('matching chat module response error: ', error);
}

// {
//   query: "What's in these images?",
//   question: [
//     {
//       type: 'text',
//       text: "What's in this image?",
//     },
//     {
//       type: 'image',
//       source: {
//         type: 'base64',
//         media_type: 'image/jpeg',
//         data: 'iVBORw...',
//       },
//     },
//     {
//       type: 'text',
//       text: 'and in this image',
//     },
//     {
//       type: 'image',
//       source: {
//         type: 'base64',
//         media_type: 'image/jpeg',
//         data: 'iVBORw...',
//       },
//     },
//   ],
// };
