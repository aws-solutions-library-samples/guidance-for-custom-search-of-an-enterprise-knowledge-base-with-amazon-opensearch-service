import { DEFAULT_CHAT_SYSTEM_PROMPT } from '../PROMPT_TEMPLATES';
import { configs } from './ragModule';


/**
 * CHAT module: restful api
 * @method POST: body example below:
 */
export const chatModuleRequest = {
  configs: {
    // v3.2 RAG configs
    ...configs,
    workMode: 'multi-modal',
    chatSystemPrompt: JSON.stringify(DEFAULT_CHAT_SYSTEM_PROMPT),
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
