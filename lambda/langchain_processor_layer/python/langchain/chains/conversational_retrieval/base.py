"""Chain for chatting with a vector database."""
from __future__ import annotations

import json
import requests
import time
from collections import defaultdict
import os
import inspect
import warnings
from abc import abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
    Callbacks,
)
from langchain.chains.base import Chain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.pydantic_v1 import BaseModel, Extra, Field, root_validator
from langchain.schema import BasePromptTemplate, BaseRetriever, Document
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.messages import BaseMessage
from langchain.schema.runnable.config import RunnableConfig
from langchain.schema.vectorstore import VectorStore

# Depending on the memory type and configuration, the chat history format may differ.
# This needs to be consolidated.
CHAT_TURN_TYPE = Union[Tuple[str, str], BaseMessage]


_ROLE_MAP = {"human": "Human: ", "ai": "Assistant: "}


#add get aos search docs
def _get_aos_docs(question,
                  index,
                  username,
                  password,
                  host,
                  port,
                  docs_num
                  ) -> List[Document]:
    num_output = 10
    awsauth = (username, password)
    source_includes = ["sentence","paragraph","metadata"]
    fields = ["sentence"]
    headers = { "Content-Type": "application/json" }
    url = f'https://{host}/{index}/_search'
    print("url:",url)
    query = {
    "size": num_output,
      "_source": {
          "includes": source_includes
        },
    'query': {
      "multi_match": {
        "query": question,
        "fields": fields
            }
        }
      }
    #r = requests.post(host + index + '/_search', auth=awsauth, headers=headers, json=query)
    r = requests.post(url, auth=awsauth, headers=headers, json=query)
    r = json.loads(r.text)
    clean = []
    aos_docs = []
    for hit in r['hits']['hits']:
        document_score = float(hit['_score'])/10
        document_paragraph = hit['_source']['paragraph']
        document_metadata = hit['_source']['metadata']
        document_sentence = hit['_source']['sentence']
        if  document_paragraph  not in clean:
           #Remove duplicate paragraph
            clean.append(document_paragraph)
            document_paragraph = "\n".join(document_paragraph)
            document_sentence = "\n".join(document_sentence)
            aos_docs.append(
                            (Document(page_content=document_paragraph,metadata=document_metadata),
                             document_score,
                             document_sentence
                            )
                           )
    aos_docs = sorted(aos_docs, key=lambda x: x[1], reverse=True)
    aos_docs = aos_docs[:docs_num]
    return aos_docs

#add cal aos score
def _cal_aos_docs_score(docs,
                  aos_docs
                  ) -> List[Document]:
    num1 = 0
    avg_point = 0
    sum_point = 0
    new_aos_docs = []
    if len(docs) > 0 and len(aos_docs) > 0:
        docs_pagecontent = [doc[0].page_content for doc in docs]
        docs_scores = [doc[1] for doc in docs]
        ori_aos_docs = [doc[0] for doc in aos_docs]
        aos_docs_pagecontent = [doc[0].page_content for doc in aos_docs]
        aos_docs_scores = [doc[1] for doc in aos_docs]
        aos_docs_sentenct = [doc[2] for doc in aos_docs]
        for i in range(len(docs_pagecontent)):
            for i1 in range(len(aos_docs_pagecontent)):
                if aos_docs_pagecontent[i1] == docs_pagecontent[i] and aos_docs_scores[i1] !=0:
                    sum_point += docs_scores[i] / aos_docs_scores[i1]
                    #print(docs_scores[i],aos_docs_scores[i1],sum_point)
                    num1 += 1
        if num1 !=0 and sum_point !=0:
            avg_point = sum_point / num1
            for i in range(len(aos_docs)):
                new_aos_score = aos_docs_scores[i] * avg_point
                new_aos_docs.append((ori_aos_docs[i],new_aos_score,aos_docs_sentenct[i]))
                aos_docs = new_aos_docs
    aos_docs = sorted(aos_docs, key=lambda x: x[1], reverse=True)
    aos_docs = aos_docs[:3]
    return aos_docs

def _get_chat_history(chat_history: List[CHAT_TURN_TYPE]) -> str:
    buffer = ""
    for dialogue_turn in chat_history:
        if isinstance(dialogue_turn, BaseMessage):
            role_prefix = _ROLE_MAP.get(dialogue_turn.type, f"{dialogue_turn.type}: ")
            buffer += f"\n{role_prefix}{dialogue_turn.content}"
        elif isinstance(dialogue_turn, tuple):
            human = "Human: " + dialogue_turn[0]
            ai = "Assistant: " + dialogue_turn[1]
            buffer += "\n" + "\n".join([human, ai])
        else:
            raise ValueError(
                f"Unsupported chat history format: {type(dialogue_turn)}."
                f" Full chat history: {chat_history} "
            )
    return buffer


class InputType(BaseModel):
    question: str
    chat_history: List[CHAT_TURN_TYPE] = Field(default_factory=list)


class BaseConversationalRetrievalChain(Chain):
    """Chain for chatting with an index."""

    combine_docs_chain: BaseCombineDocumentsChain
    """The chain used to combine any retrieved documents."""
    question_generator: LLMChain
    """The chain used to generate a new question for the sake of retrieval.
    This chain will take in the current question (with variable `question`)
    and any chat history (with variable `chat_history`) and will produce
    a new standalone question to be used later on."""
    output_key: str = "answer"
    """The output key to return the final answer of this chain in."""
    rephrase_question: bool = True
    """Whether or not to pass the new generated question to the combine_docs_chain.
    If True, will pass the new generated question along.
    If False, will only use the new generated question for retrieval and pass the
    original question along to the combine_docs_chain."""
    return_source_documents: bool = False
    """Return the retrieved source documents as part of the final result."""
    return_generated_question: bool = False
    """Return the generated question as part of the final result."""
    get_chat_history: Optional[Callable[[List[CHAT_TURN_TYPE]], str]] = None
    """An optional function to get a string of the chat history.
    If None is provided, will use a default."""
    response_if_no_docs_found: Optional[str]
    """If specified, the chain will return a fixed response if no docs 
    are found for the question. """

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    @property
    def input_keys(self) -> List[str]:
        """Input keys."""
        return ["question", "chat_history"]

    def get_input_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return InputType

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys.

        :meta private:
        """
        _output_keys = [self.output_key]
        if self.return_source_documents:
            _output_keys = _output_keys + ["source_documents"]
        if self.return_generated_question:
            _output_keys = _output_keys + ["generated_question"]
        return _output_keys

    @abstractmethod
    def _get_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: CallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        question = inputs["question"]
        #add get index and aos parameters
        index_name = inputs["index_name"]
        aos_username = inputs["aos_username"]
        aos_passwd = inputs["aos_passwd"]
        aos_host = inputs["aos_host"]
        aos_port = inputs["aos_port"]
        search_engine = inputs["search_engine"]
        search_method = inputs["search_method"]
        txt_docs_num = int(inputs["txt_docs_num"])
        self.response_if_no_docs_found = inputs["response_if_no_docs_found"]
        vec_docs_score_thresholds = float(inputs["vec_docs_score_thresholds"])
        txt_docs_score_thresholds = float(inputs["txt_docs_score_thresholds"])
        
        get_chat_history = self.get_chat_history or _get_chat_history
        chat_history_str = get_chat_history(inputs["chat_history"])

        if chat_history_str:
            callbacks = _run_manager.get_child()
            new_question = self.question_generator.run(
                question=question, chat_history=chat_history_str, callbacks=callbacks
            )
        else:
            new_question = question
        accepts_run_manager = (
            "run_manager" in inspect.signature(self._get_docs).parameters
        )
        vec_docs = []
        aos_docs = []
        docs = []
        if search_method != "text":
            if accepts_run_manager:
                vec_docs = self._get_docs(new_question, inputs, run_manager=_run_manager)
            else:
                vec_docs = self._get_docs(new_question, inputs)  # type: ignore[call-arg]
            print('vec_docs:',vec_docs)
        #add get aos docs
        if search_engine == "opensearch" and search_method != "vector" and txt_docs_num > 0:
            aos_docs = _get_aos_docs(new_question,index_name,aos_username,aos_passwd,aos_host,aos_port,txt_docs_num)
            print('aos_docs:',aos_docs)
        
        output: Dict[str, Any] = {}
        if self.response_if_no_docs_found is not None and len(vec_docs+aos_docs) == 0:
            output[self.output_key] = self.response_if_no_docs_found
        else:
            new_vec_docs = []
            new_aos_docs = []
            if search_method != "text" and len(vec_docs) > 0 and vec_docs_score_thresholds > 0:              
                for doc in vec_docs:
                    if float(doc[1]) >= vec_docs_score_thresholds:
                        new_vec_docs.append(doc)
            else:
                new_vec_docs = vec_docs
                
            if search_method != "vector" and len(aos_docs) > 0 and txt_docs_score_thresholds > 0:
                for doc in aos_docs:
                    if float(doc[1]) >= txt_docs_score_thresholds:
                        new_aos_docs.append(doc)
            else:
                new_aos_docs = aos_docs
            
            if search_method == "text":
                docs = new_aos_docs
            elif search_method == "mix":
                docs = new_vec_docs + new_aos_docs
            else:
                docs = new_vec_docs
            print('last docs:',docs)
            
            if len(docs) == 0:
                output[self.output_key] = self.response_if_no_docs_found
            else:
                new_inputs = inputs.copy()
                if self.rephrase_question:
                    new_inputs["question"] = new_question
                new_inputs["chat_history"] = chat_history_str


                deduplication_docs = docs
                if len(docs) > 0 and isinstance (docs[0],tuple):
                    ori_only_docs = [doc[0] for doc in docs]
                    scores = [doc[1] for doc in docs]
                    sentences = [doc[2] for doc in docs]
                    new_docs_with_scores = []
                    page_contents = []
                    for i in range(len(ori_only_docs)):
                        page_content = ori_only_docs[i].page_content
                        if len(page_contents) > 0:
                            find_flag = False
                            for content in page_contents:
                                if content == page_content:
                                    find_flag = True
                                    break
                            if not find_flag:
                                page_contents.append(page_content)
                                new_docs_with_scores.append((ori_only_docs[i],scores[i],sentences[i]))
                        else:
                            page_contents.append(page_content)
                            new_docs_with_scores.append((ori_only_docs[i],scores[i],sentences[i]))
                    deduplication_docs = [doc[0] for doc in new_docs_with_scores]
                    docs = new_docs_with_scores
                    print('deduplication docs:',docs)

                answer = self.combine_docs_chain.run(
                    input_documents=deduplication_docs, callbacks=_run_manager.get_child(), **new_inputs
                )
                output[self.output_key] = answer

        if self.return_source_documents:
            output["source_documents"] = docs
        if self.return_generated_question:
            output["generated_question"] = new_question
        return output

    @abstractmethod
    async def _aget_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: AsyncCallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        question = inputs["question"]
        get_chat_history = self.get_chat_history or _get_chat_history
        chat_history_str = get_chat_history(inputs["chat_history"])
        if chat_history_str:
            callbacks = _run_manager.get_child()
            new_question = await self.question_generator.arun(
                question=question, chat_history=chat_history_str, callbacks=callbacks
            )
        else:
            new_question = question
        accepts_run_manager = (
            "run_manager" in inspect.signature(self._aget_docs).parameters
        )
        if accepts_run_manager:
            docs = await self._aget_docs(new_question, inputs, run_manager=_run_manager)
        else:
            docs = await self._aget_docs(new_question, inputs)  # type: ignore[call-arg]

        new_inputs = inputs.copy()
        if self.rephrase_question:
            new_inputs["question"] = new_question
        new_inputs["chat_history"] = chat_history_str
        answer = await self.combine_docs_chain.arun(
            input_documents=docs, callbacks=_run_manager.get_child(), **new_inputs
        )
        output: Dict[str, Any] = {self.output_key: answer}
        if self.return_source_documents:
            output["source_documents"] = docs
        if self.return_generated_question:
            output["generated_question"] = new_question
        return output

    def save(self, file_path: Union[Path, str]) -> None:
        if self.get_chat_history:
            raise ValueError("Chain not saveable when `get_chat_history` is not None.")
        super().save(file_path)


class ConversationalRetrievalChain(BaseConversationalRetrievalChain):
    """Chain for having a conversation based on retrieved documents.

    This chain takes in chat history (a list of messages) and new questions,
    and then returns an answer to that question.
    The algorithm for this chain consists of three parts:

    1. Use the chat history and the new question to create a "standalone question".
    This is done so that this question can be passed into the retrieval step to fetch
    relevant documents. If only the new question was passed in, then relevant context
    may be lacking. If the whole conversation was passed into retrieval, there may
    be unnecessary information there that would distract from retrieval.

    2. This new question is passed to the retriever and relevant documents are
    returned.

    3. The retrieved documents are passed to an LLM along with either the new question
    (default behavior) or the original question and chat history to generate a final
    response.

    Example:
        .. code-block:: python

            from langchain.chains import (
                StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
            )
            from langchain.prompts import PromptTemplate
            from langchain.llms import OpenAI

            combine_docs_chain = StuffDocumentsChain(...)
            vectorstore = ...
            retriever = vectorstore.as_retriever()

            # This controls how the standalone question is generated.
            # Should take `chat_history` and `question` as input variables.
            template = (
                "Combine the chat history and follow up question into "
                "a standalone question. Chat History: {chat_history}"
                "Follow up question: {question}"
            )
            prompt = PromptTemplate.from_template(template)
            llm = OpenAI()
            question_generator_chain = LLMChain(llm=llm, prompt=prompt)
            chain = ConversationalRetrievalChain(
                combine_docs_chain=combine_docs_chain,
                retriever=retriever,
                question_generator=question_generator_chain,
            )
    """

    retriever: BaseRetriever
    """Retriever to use to fetch documents."""
    max_tokens_limit: Optional[int] = None
    """If set, enforces that the documents returned are less than this limit.
    This is only enforced if `combine_docs_chain` is of type StuffDocumentsChain."""

    def _reduce_tokens_below_limit(self, docs: List[Document]) -> List[Document]:
        num_docs = len(docs)

        if self.max_tokens_limit and isinstance(
            self.combine_docs_chain, StuffDocumentsChain
        ):
            tokens = [
                self.combine_docs_chain.llm_chain.llm.get_num_tokens(doc.page_content)
                for doc in docs
            ]
            token_count = sum(tokens[:num_docs])
            while token_count > self.max_tokens_limit:
                num_docs -= 1
                token_count -= tokens[num_docs]

        return docs[:num_docs]

    def _get_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: CallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        docs = self.retriever.get_relevant_documents(
            question, callbacks=run_manager.get_child()
        )
        return self._reduce_tokens_below_limit(docs)

    async def _aget_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: AsyncCallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        docs = await self.retriever.aget_relevant_documents(
            question, callbacks=run_manager.get_child()
        )
        return self._reduce_tokens_below_limit(docs)

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        retriever: BaseRetriever,
        condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
        chain_type: str = "stuff",
        verbose: bool = False,
        condense_question_llm: Optional[BaseLanguageModel] = None,
        combine_docs_chain_kwargs: Optional[Dict] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> BaseConversationalRetrievalChain:
        """Convenience method to load chain from LLM and retriever.

        This provides some logic to create the `question_generator` chain
        as well as the combine_docs_chain.

        Args:
            llm: The default language model to use at every part of this chain
                (eg in both the question generation and the answering)
            retriever: The retriever to use to fetch relevant documents from.
            condense_question_prompt: The prompt to use to condense the chat history
                and new question into a standalone question.
            chain_type: The chain type to use to create the combine_docs_chain, will
                be sent to `load_qa_chain`.
            verbose: Verbosity flag for logging to stdout.
            condense_question_llm: The language model to use for condensing the chat
                history and new question into a standalone question. If none is
                provided, will default to `llm`.
            combine_docs_chain_kwargs: Parameters to pass as kwargs to `load_qa_chain`
                when constructing the combine_docs_chain.
            callbacks: Callbacks to pass to all subchains.
            **kwargs: Additional parameters to pass when initializing
                ConversationalRetrievalChain
        """
        combine_docs_chain_kwargs = combine_docs_chain_kwargs or {}
        doc_chain = load_qa_chain(
            llm,
            chain_type=chain_type,
            verbose=verbose,
            callbacks=callbacks,
            **combine_docs_chain_kwargs,
        )

        _llm = condense_question_llm or llm
        condense_question_chain = LLMChain(
            llm=_llm,
            prompt=condense_question_prompt,
            verbose=verbose,
            callbacks=callbacks,
        )
        return cls(
            retriever=retriever,
            combine_docs_chain=doc_chain,
            question_generator=condense_question_chain,
            callbacks=callbacks,
            **kwargs,
        )


class ChatVectorDBChain(BaseConversationalRetrievalChain):
    """Chain for chatting with a vector database."""

    vectorstore: VectorStore = Field(alias="vectorstore")
    top_k_docs_for_context: int = 4
    search_kwargs: dict = Field(default_factory=dict)

    @property
    def _chain_type(self) -> str:
        return "chat-vector-db"

    @root_validator()
    def raise_deprecation(cls, values: Dict) -> Dict:
        warnings.warn(
            "`ChatVectorDBChain` is deprecated - "
            "please use `from langchain.chains import ConversationalRetrievalChain`"
        )
        return values

    def _get_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: CallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        vectordbkwargs = inputs.get("vectordbkwargs", {})
        full_kwargs = {**self.search_kwargs, **vectordbkwargs}
        return self.vectorstore.similarity_search(
            question, k=self.top_k_docs_for_context, **full_kwargs
        )

    async def _aget_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: AsyncCallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        raise NotImplementedError("ChatVectorDBChain does not support async")

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        vectorstore: VectorStore,
        condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
        chain_type: str = "stuff",
        combine_docs_chain_kwargs: Optional[Dict] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> BaseConversationalRetrievalChain:
        """Load chain from LLM."""
        combine_docs_chain_kwargs = combine_docs_chain_kwargs or {}
        doc_chain = load_qa_chain(
            llm,
            chain_type=chain_type,
            callbacks=callbacks,
            **combine_docs_chain_kwargs,
        )
        condense_question_chain = LLMChain(
            llm=llm, prompt=condense_question_prompt, callbacks=callbacks
        )
        return cls(
            vectorstore=vectorstore,
            combine_docs_chain=doc_chain,
            question_generator=condense_question_chain,
            callbacks=callbacks,
            **kwargs,
        )
