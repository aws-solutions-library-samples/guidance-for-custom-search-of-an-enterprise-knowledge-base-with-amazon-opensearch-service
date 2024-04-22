import boto3
import json
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple
from opensearchpy import OpenSearch


IMPORT_OPENSEARCH_PY_ERROR = (
    "Could not import OpenSearch. Please install it with `pip install opensearch-py`."
)

def get_opensearch_client() -> Any:
    sm_client = boto3.client('secretsmanager')
    
    master_user = sm_client.get_secret_value(SecretId='opensearch-host-url')['SecretString']
    data= json.loads(master_user)
    es_host_name = data.get('host')
    if es_host_name.find('http') >=0:
        host = es_host_name+'/' if es_host_name[-1] != '/' else es_host_name
        host = host[8:-1]
    else:
        host = es_host_name
    region = boto3.Session().region_name # e.g. cn-north-1

    master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
    data= json.loads(master_user)
    username = data.get('username')
    password = data.get('password')
    
    port = 443
    hosts = [{'host': host, 'port': port}]
    http_auth = (username, password)

    search_client = OpenSearch(hosts=hosts,http_auth=http_auth,use_ssl = True)
    return search_client

def _import_bulk() -> Any:
    """Import bulk if available, otherwise raise error."""
    try:
        from opensearchpy.helpers import bulk
    except ImportError:
        raise ImportError(IMPORT_OPENSEARCH_PY_ERROR)
    return bulk

def _import_not_found_error() -> Any:
    """Import not found error if available, otherwise raise error."""
    try:
        from opensearchpy.exceptions import NotFoundError
    except ImportError:
        raise ImportError(IMPORT_OPENSEARCH_PY_ERROR)
    return NotFoundError

def _bulk_ingest_embeddings(
    client: Any,
    index_name: str,
    embeddings: List[List[float]],
    texts: Iterable[str],
    images: Iterable[str],
    metadatas: Optional[List[dict]] = None,
    ids: Optional[List[str]] = None,
    vector_field: str = "vector_field",
    text_field: str = "text",
    image_field: str = "image_base64",
    mapping: Optional[Dict] = None,
    max_chunk_bytes: Optional[int] = 1 * 1024 * 1024
) -> List[str]:
    """Bulk Ingest Embeddings into given index."""
    if not mapping:
        mapping = dict()

    bulk = _import_bulk()
    not_found_error = _import_not_found_error()
    requests = []
    return_ids = []
    mapping = mapping

    try:
        client.indices.get(index=index_name)
    except not_found_error:
        client.indices.create(index=index_name, body=mapping)

    for i, text in enumerate(texts):
        metadata = metadatas[i] if metadatas else {}
        _id = ids[i] if ids else str(uuid.uuid4())
        request = {}
        if images is not None and len(images) > 0:
            request = {
                "_op_type": "index",
                "_index": index_name,
                vector_field: embeddings[i],
                text_field: text,
                image_field: images[i],
                "metadata": metadata,
            }
        else:
            request = {
                "_op_type": "index",
                "_index": index_name,
                vector_field: embeddings[i],
                text_field: text,
                "metadata": metadata,
            }

        request["_id"] = _id
        requests.append(request)
        return_ids.append(_id)
    bulk(client, requests, max_chunk_bytes=max_chunk_bytes)
    client.indices.refresh(index=index_name)
    return return_ids


def _default_text_mapping(
    dim: int,
    engine: str = "nmslib",
    space_type: str = "l2",
    ef_search: int = 512,
    ef_construction: int = 512,
    m: int = 16,
    vector_field: str = "vector_field",
) -> Dict:
    """For Approximate k-NN Search, this is the default mapping to create index."""
    return {
        "settings": {"index": {"knn": True, "knn.algo_param.ef_search": ef_search}},
        "mappings": {
            "properties": {
                vector_field: {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": space_type,
                        "engine": engine,
                        "parameters": {"ef_construction": ef_construction, "m": m},
                    },
                }
            }
        },
    }
        

def _validate_embeddings_and_bulk_size(embeddings_length: int, bulk_size: int) -> None:
    """Validate Embeddings Length and Bulk Size."""
    if embeddings_length == 0:
        raise RuntimeError("Embeddings size is zero")
    if bulk_size < embeddings_length:
        raise RuntimeError(
            f"The embeddings count, {embeddings_length} is more than the "
            f"[bulk_size], {bulk_size}. Increase the value of [bulk_size]."
        )

        
def add_multimodel_documents(
        index_name: str,
        texts: Iterable[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[dict]] = None,
        images: Iterable[str] = None,
        ids: Optional[List[str]] = None,
        bulk_size: int = 10000000,
        **kwargs: Any,
    ) -> List[str]:
        _validate_embeddings_and_bulk_size(len(embeddings), bulk_size)
        text_field = kwargs.get("text_field", "text")
        dim = len(embeddings[0])
        engine = kwargs.get("engine", "nmslib")
        space_type = kwargs.get("space_type", "l2")
        ef_search = kwargs.get("ef_search", 512)
        ef_construction = kwargs.get("ef_construction", 512)
        m = kwargs.get("m", 16)
        vector_field = kwargs.get("vector_field", "vector_field")
        image_field = kwargs.get("image_field", "image_base64")
        max_chunk_bytes = kwargs.get("max_chunk_bytes", 1 * 1024 * 1024)

        mapping = _default_text_mapping(
            dim, engine, space_type, ef_search, ef_construction, m, vector_field
        )

        client = get_opensearch_client()
        
        return _bulk_ingest_embeddings(
            client,
            index_name,
            embeddings,
            texts,
            images,
            metadatas=metadatas,
            ids=ids,
            vector_field=vector_field,
            text_field=text_field,
            image_field=image_field,
            mapping=mapping,
            max_chunk_bytes=max_chunk_bytes
        )



    
    
