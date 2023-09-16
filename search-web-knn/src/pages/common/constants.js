// Below items needs to be changed
// mainapi / opensearch_api / opensearch_region / SOURCE_DATA_BUCKET
export const mainapi = ''
export const opensearch_api = ""
export const opensearch_region = ""
export const SOURCE_DATA_BUCKET = ""


export const HEADERS = {'Content-Type': 'application/json'}
export const post_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}
export const SOURCE_DATA_BUCKET_PREFIX = "source_data/"
export var last_table_name = 'FeedbackRecordsSEWCFAQ'

export const FILE_TYPES = [
    {value: "faq", label: "FAQ Document"},
    {value: "content_search", label: "Content Search Document"}
]